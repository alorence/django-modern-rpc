import asyncio
from unittest.mock import Mock

import django
import pytest
from asgiref.sync import sync_to_async
from asgiref.testing import ApplicationCommunicator
from django.core.handlers.asgi import ASGIHandler
from django.urls import path

from modernrpc import Protocol, RpcRequestContext, RpcServer
from modernrpc.exceptions import RPCException, RPCInternalError, RPCMethodNotFound
from modernrpc.jsonrpc.handler import JsonRpcHandler
from modernrpc.xmlrpc.handler import XmlRpcHandler


@pytest.fixture
def mocked_request_context():
    return Mock(spec=RpcRequestContext)


class TestRpcServerErrorHandling:
    """Tests for RpcServer error handling mechanism."""

    def test_default_error_handling_rpc_exception(self, mocked_request_context):
        """Test that RpcServer.on_error returns RPCException as is."""
        server = RpcServer()

        exception = RPCMethodNotFound("test_method")
        result = server.on_error(exception, mocked_request_context)

        assert result is exception
        assert result.code == -32601
        assert "Method not found" in result.message

    def test_default_error_handling_standard_exception(self, mocked_request_context):
        """Test that RpcServer.on_error wraps standard exceptions in RPCInternalError."""
        server = RpcServer()

        exception = ValueError("Test error message")
        result = server.on_error(exception, mocked_request_context)

        assert isinstance(result, RPCInternalError)
        assert result.code == -32603
        assert "Internal error" in result.message
        assert "Test error message" in result.message

    def test_custom_error_handler(self, mocked_request_context):
        """Test that custom error handler is called and its result is used."""
        custom_handler = Mock(side_effect=RPCException(-1000, "Custom error"))
        server = RpcServer(error_handler=custom_handler)

        exception = ValueError("Test error message")
        result = server.on_error(exception, mocked_request_context)

        custom_handler.assert_called_once_with(exception, mocked_request_context)
        assert result.code == -1000
        assert result.message == "Custom error"

    def test_custom_error_handler_returns_none(self, mocked_request_context):
        """Test that when custom error handler returns None, default handling is used."""
        custom_handler = Mock(return_value=None)
        server = RpcServer(error_handler=custom_handler)

        exception = ValueError("Test error message")
        result = server.on_error(exception, mocked_request_context)

        custom_handler.assert_called_once_with(exception, mocked_request_context)
        assert isinstance(result, RPCInternalError)
        assert result.code == -32603
        assert "Internal error" in result.message
        assert "Test error message" in result.message

    @pytest.mark.parametrize(
        ("protocol", "handler", "content_type"),
        [
            (Protocol.JSON_RPC, JsonRpcHandler(), "application/json"),
            (Protocol.XML_RPC, XmlRpcHandler(), "application/xml"),
        ],
    )
    def test_error_handling_integration_with_handler(self, rf, protocol, handler, content_type):
        """Test integration of error handling with request handlers."""
        # Create a server with a custom error handler
        custom_handler = Mock(side_effect=RPCException(-1000, "Custom error"))
        server = RpcServer(error_handler=custom_handler)

        request = rf.post("/rpc", content_type=content_type)
        context = RpcRequestContext(request, server, handler, protocol)

        # Create a mock request object
        mocked_rpc_request = Mock()
        mocked_rpc_request.method_name = "non_existent_method"
        mocked_rpc_request.args = []

        # Process the request
        result = handler.process_single_request(mocked_rpc_request, context)

        # Verify that the error handler was called
        custom_handler.assert_called_once()
        assert result.code == -1000
        assert result.message == "Custom error"


class TestCancellationHandling:
    @pytest.mark.parametrize("request_factory", ["jsonrpc_rf", "xmlrpc_rf"])
    @pytest.mark.parametrize("asynchronous_view", [False, True], ids=["sync-view", "async-view"])
    @pytest.mark.parametrize("asynchronous_procedure", [False, True], ids=["sync-procedure", "async-procedure"])
    async def test_procedure_cancellation(self, request, request_factory, asynchronous_view, asynchronous_procedure):
        error_handler = Mock()
        server = RpcServer(error_handler=error_handler)
        cancellation = asyncio.CancelledError("procedure stopped")

        def sync_procedure():
            raise cancellation

        async def async_procedure():
            raise cancellation

        server.register_procedure(async_procedure if asynchronous_procedure else sync_procedure, name="cancelled")
        rpc_request = request.getfixturevalue(request_factory)(method_name="cancelled")
        view = server.async_view if asynchronous_view else sync_to_async(server.view)

        with pytest.raises(asyncio.CancelledError) as exc_info:
            await view(rpc_request)

        assert exc_info.value is cancellation
        error_handler.assert_not_called()

    @pytest.mark.parametrize("request_factory", ["jsonrpc_rf", "xmlrpc_rf"])
    async def test_running_view_cancellation(self, request, request_factory):
        error_handler = Mock()
        server = RpcServer(error_handler=error_handler)
        entered = asyncio.Event()
        cleaned = asyncio.Event()

        @server.register_procedure
        async def waiting():
            entered.set()
            try:
                await asyncio.Future()
            finally:
                cleaned.set()

        rpc_request = request.getfixturevalue(request_factory)(method_name="waiting")
        task = asyncio.create_task(server.async_view(rpc_request))
        try:
            await asyncio.wait_for(entered.wait(), timeout=2)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=2)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

        assert cleaned.is_set()
        error_handler.assert_not_called()

    @pytest.mark.parametrize("batch", [False, True], ids=["notification", "batch"])
    async def test_json_notification_cancellation(self, jsonrpc_rf, jsonrpc_batch_rf, batch):
        error_handler = Mock()
        server = RpcServer(error_handler=error_handler)

        @server.register_procedure
        async def cancelled():
            raise asyncio.CancelledError

        rpc_request = (
            jsonrpc_batch_rf(requests=[("cancelled", (), True), ("cancelled", (), False)])
            if batch
            else jsonrpc_rf(method_name="cancelled", is_notif=True)
        )

        with pytest.raises(asyncio.CancelledError):
            await server.async_view(rpc_request)

        error_handler.assert_not_called()

    @pytest.mark.skipif(django.VERSION < (5, 0), reason="Django 4.2 does not cancel views on disconnect")
    @pytest.mark.parametrize("request_factory", ["jsonrpc_rf", "xmlrpc_rf"])
    async def test_asgi_disconnect(self, request, request_factory, async_rf, settings):
        error_handler = Mock()
        server = RpcServer(error_handler=error_handler)
        entered = asyncio.Event()
        cleaned = asyncio.Event()

        @server.register_procedure
        async def waiting():
            entered.set()
            try:
                await asyncio.Future()
            finally:
                cleaned.set()

        rpc_request = request.getfixturevalue(request_factory)(method_name="waiting")
        settings.ROOT_URLCONF = type("CancellationUrls", (), {"urlpatterns": [path("rpc", server.async_view)]})
        settings.MIDDLEWARE = []
        asgi_request = async_rf.post("/rpc", data=rpc_request.body, content_type=rpc_request.content_type)
        communicator = ApplicationCommunicator(ASGIHandler(), asgi_request.scope)
        try:
            await communicator.send_input({"type": "http.request", "body": rpc_request.body})
            await asyncio.wait_for(entered.wait(), timeout=2)
            await communicator.send_input({"type": "http.disconnect"})
            await communicator.wait(timeout=2)

            assert cleaned.is_set()
            assert communicator.output_queue.empty()
            error_handler.assert_not_called()
        finally:
            communicator.stop(exceptions=False)
            await asyncio.gather(communicator.future, return_exceptions=True)
