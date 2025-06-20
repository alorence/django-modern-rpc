from unittest.mock import Mock

import pytest

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
        custom_handler = Mock(return_value=RPCException(-1000, "Custom error"))
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
        custom_handler = Mock(return_value=RPCException(-1000, "Custom error"))
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
