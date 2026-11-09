import asyncio
import logging
from typing import Any
from unittest.mock import Mock

import pytest
from django.test import RequestFactory
from pytest_django import Settings

from modernrpc import Protocol, RpcRequestContext, RpcServer
from modernrpc.core import ProcedureWrapper
from modernrpc.exceptions import (
    RPCException,
    RPCInternalError,
    RPCInvalidParams,
    RPCMarshallingError,
    RPCMethodNotFound,
)
from modernrpc.handler import RpcHandler
from modernrpc.jsonrpc.handler import JsonRpcHandler
from modernrpc.types import RpcErrorResult, RpcRequest
from modernrpc.xmlrpc.handler import XmlRpcHandler


@pytest.fixture
def mocked_request_context() -> Mock:
    return Mock(spec=RpcRequestContext)


class TestRpcServerErrorHandling:
    """Tests for RpcServer error handling mechanism."""

    def test_default_error_handling_rpc_exception(self, mocked_request_context: Mock) -> None:
        """Test that RpcServer.on_error returns RPCException as is."""
        server = RpcServer()

        exception = RPCMethodNotFound("test_method")
        result = server.on_error(exception, mocked_request_context)

        assert result is exception
        assert result.code == -32601
        assert "Method not found" in result.message

    def test_default_error_handling_standard_exception(self, mocked_request_context: Mock) -> None:
        """Test that RpcServer.on_error wraps standard exceptions in RPCInternalError."""
        server = RpcServer()

        exception = ValueError("Test error message")
        result = server.on_error(exception, mocked_request_context)

        assert isinstance(result, RPCInternalError)
        assert result.code == -32603
        assert result.message == "Internal error"

    def test_standard_exception_details_are_logged(
        self, mocked_request_context: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that details of a masked exception are kept in server logs."""
        server = RpcServer()

        exception = ValueError("Test error message")
        with caplog.at_level(logging.ERROR, logger="modernrpc.server"):
            server.on_error(exception, mocked_request_context)

        assert "Test error message" in caplog.text
        assert caplog.records[-1].exc_info is not None
        assert caplog.records[-1].exc_info[1] is exception

    @pytest.mark.parametrize("from_settings", [False, True], ids=["init-arg", "settings"])
    def test_expose_internal_errors(
        self, mocked_request_context: Mock, settings: Settings, from_settings: bool
    ) -> None:
        """Test that standard exceptions message is returned when expose_internal_errors is enabled."""
        if from_settings:
            settings.MODERNRPC_EXPOSE_INTERNAL_ERRORS = True
            server = RpcServer()
        else:
            server = RpcServer(expose_internal_errors=True)

        result = server.on_error(ValueError("Test error message"), mocked_request_context)

        assert isinstance(result, RPCInternalError)
        assert result.code == -32603
        assert result.message == "Internal error: Test error message"

    def test_init_arg_overrides_settings(self, mocked_request_context: Mock, settings: Settings) -> None:
        settings.MODERNRPC_EXPOSE_INTERNAL_ERRORS = True
        server = RpcServer(expose_internal_errors=False)

        result = server.on_error(ValueError("Test error message"), mocked_request_context)

        assert result.message == "Internal error"

    def test_marshalling_error_is_masked(self, mocked_request_context: Mock) -> None:
        """Test that RPCMarshallingError, which includes result data in its message, is masked by default."""
        server = RpcServer()

        exception = RPCMarshallingError({"secret": "s3cr3t"}, TypeError("not serializable"))
        result = server.on_error(exception, mocked_request_context)

        assert isinstance(result, RPCInternalError)
        assert result.code == -32603
        assert result.message == "Internal error"
        assert exception.result_data == {"secret": "s3cr3t"}
        assert isinstance(exception.original_exc, TypeError)

    def test_marshalling_error_is_exposed(self, mocked_request_context: Mock) -> None:
        server = RpcServer(expose_internal_errors=True)

        exception = RPCMarshallingError({"secret": "s3cr3t"}, TypeError("not serializable"))
        result = server.on_error(exception, mocked_request_context)

        assert result is exception
        assert "s3cr3t" in result.message

    def test_custom_error_handler(self, mocked_request_context: Mock) -> None:
        """Test that custom error handler is called and its result is used."""
        custom_handler = Mock(side_effect=RPCException(-1000, "Custom error"))
        server = RpcServer(error_handler=custom_handler)

        exception = ValueError("Test error message")
        result = server.on_error(exception, mocked_request_context)

        custom_handler.assert_called_once_with(exception, mocked_request_context)
        assert result.code == -1000
        assert result.message == "Custom error"

    def test_custom_error_handler_returns_none(self, mocked_request_context: Mock) -> None:
        """Test that when custom error handler returns None, default handling is used."""
        custom_handler = Mock(return_value=None)
        server = RpcServer(error_handler=custom_handler)

        exception = ValueError("Test error message")
        result = server.on_error(exception, mocked_request_context)

        custom_handler.assert_called_once_with(exception, mocked_request_context)
        assert isinstance(result, RPCInternalError)
        assert result.code == -32603
        assert result.message == "Internal error"

    def test_custom_error_handler_can_expose_message(self, mocked_request_context: Mock) -> None:
        """Test that an error handler can explicitly forward the message of an exception to the client."""

        def handler(exc: BaseException, _ctx: RpcRequestContext) -> None:
            if isinstance(exc, ValueError):
                raise RPCInvalidParams(str(exc)) from exc

        server = RpcServer(error_handler=handler)
        result = server.on_error(ValueError("Test error message"), mocked_request_context)

        assert result.code == -32602
        assert result.message == "Invalid parameters: Test error message"

    @pytest.mark.parametrize(
        ("protocol", "handler", "content_type"),
        [
            (Protocol.JSON_RPC, JsonRpcHandler(), "application/json"),
            (Protocol.XML_RPC, XmlRpcHandler(), "application/xml"),
        ],
    )
    def test_error_handling_integration_with_handler(
        self, rf: RequestFactory, protocol: Protocol, handler: RpcHandler[RpcRequest], content_type: str
    ) -> None:
        """Test integration of error handling with request handlers."""
        # Create a server with a custom error handler
        custom_handler = Mock(side_effect=RPCException(-1000, "Custom error"))
        server = RpcServer(error_handler=custom_handler)

        request = rf.post("/rpc", content_type=content_type)
        context = RpcRequestContext(request, server, handler, protocol)

        # Create a mock request object
        mocked_rpc_request = Mock(method_name="non_existent_method", args=[])

        # Process the request
        result = handler.process_single_request(mocked_rpc_request, context)

        # Verify that the error handler was called
        custom_handler.assert_called_once()
        assert isinstance(result, RpcErrorResult)
        assert result.code == -1000
        assert result.message == "Custom error"

    @pytest.mark.parametrize(
        ("protocol", "handler", "content_type"),
        [
            (Protocol.JSON_RPC, JsonRpcHandler(), "application/json"),
            (Protocol.XML_RPC, XmlRpcHandler(), "application/xml"),
        ],
    )
    async def test_task_cancellation_is_propagated(
        self, rf: RequestFactory, protocol: Protocol, handler: RpcHandler[RpcRequest], content_type: str
    ):
        """Test that asyncio.CancelledError raised from a procedure is not converted into an RPC error."""
        custom_handler = Mock()
        server = RpcServer(error_handler=custom_handler)

        @server.register_procedure(name="cancelled")
        async def cancelled():
            raise asyncio.CancelledError

        request = rf.post("/rpc", content_type=content_type)
        context = RpcRequestContext(request, server, handler, protocol)

        mocked_rpc_request = Mock(method_name="cancelled", args=[], kwargs={})

        with pytest.raises(asyncio.CancelledError):
            await handler.aprocess_single_request(mocked_rpc_request, context)

        custom_handler.assert_not_called()


class TestProcedureParamsCheck:
    """Tests for params validation performed before calling a procedure."""

    @pytest.fixture
    def procedure_context(self) -> Mock:
        return Mock(spec=RpcRequestContext, request=Mock())

    @staticmethod
    def procedure(a: int, b: int = 2) -> int:
        return a + b

    @staticmethod
    def buggy_procedure(a: int) -> int:
        raise TypeError(f"internal bug with {a}")

    @staticmethod
    async def async_buggy_procedure(a: int) -> int:
        raise TypeError(f"internal bug with {a}")

    @pytest.mark.parametrize(
        ("args", "kwargs", "expected"),
        [
            ([1, 2, 3], {}, "too many positional arguments"),
            ([], {}, "missing a required argument: 'a'"),
            ([1], {"c": 3}, "got an unexpected keyword argument 'c'"),
            ([1], {"a": 3}, "multiple values for argument 'a'"),
        ],
    )
    def test_invalid_params(
        self, procedure_context: Mock, args: list[Any], kwargs: dict[str, Any], expected: str
    ) -> None:
        wrapper = ProcedureWrapper(self.procedure)

        with pytest.raises(RPCInvalidParams) as exc_info:
            wrapper.execute(procedure_context, args, kwargs)

        assert exc_info.value.message == f"Invalid parameters: {expected}"

    async def test_invalid_params_async(self, procedure_context: Mock) -> None:
        wrapper = ProcedureWrapper(self.procedure)

        with pytest.raises(RPCInvalidParams) as exc_info:
            await wrapper.aexecute(procedure_context, [1, 2, 3])

        assert exc_info.value.message == "Invalid parameters: too many positional arguments"

    def test_type_error_from_procedure_body(self, procedure_context: Mock) -> None:
        """A TypeError raised by the procedure itself must not be reported as an invalid params error."""
        wrapper = ProcedureWrapper(self.buggy_procedure)

        with pytest.raises(TypeError):
            wrapper.execute(procedure_context, [1])

    async def test_type_error_from_procedure_body_async(self, procedure_context: Mock) -> None:
        wrapper = ProcedureWrapper(self.async_buggy_procedure)

        with pytest.raises(TypeError):
            await wrapper.aexecute(procedure_context, [1])

    def test_procedure_without_signature(self, procedure_context: Mock) -> None:
        """Callables without introspectable signature (some builtins) can still be called."""
        wrapper = ProcedureWrapper(max, name="max")

        assert wrapper.execute(procedure_context, [3, 7]) == 7
