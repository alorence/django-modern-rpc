from modernrpc.exceptions import RPCException, RPCInternalError
from modernrpc.server import RpcServer


class CustomException(Exception):
    """A custom exception for testing error handlers."""


class CustomRPCException(RPCException):
    """A custom RPC exception for testing error handlers."""

    def __init__(self):
        super().__init__(code=12345, message="Custom RPC exception")


class TestErrorHandlers:
    """Tests for the error handling mechanism."""

    def test_default_error_handling(self):
        """Test that the default error handling works correctly."""
        server = RpcServer()

        # Test with a standard exception
        exception = ValueError("Test error")
        result = server.on_error(exception)
        assert isinstance(result, RPCInternalError)
        assert result.message == "Internal error: Test error"

        # Test with an RPCException
        exception = CustomRPCException()
        result = server.on_error(exception)
        assert result is exception
        assert result.code == 12345
        assert result.message == "Custom RPC exception"

    def test_custom_error_handler(self):
        """Test that custom error handlers work correctly."""
        server = RpcServer()

        # Register a custom error handler for ValueError
        def handle_value_error(exc):
            return RPCException(code=54321, message=f"Handled ValueError: {exc}")

        server.error_handler(ValueError, handle_value_error)

        # Test with a ValueError
        exception = ValueError("Test error")
        result = server.on_error(exception)
        assert isinstance(result, RPCException)
        assert result.code == 54321
        assert result.message == "Handled ValueError: Test error"

        # Test with a different exception (should use default handling)
        exception = TypeError("Type error")
        result = server.on_error(exception)
        assert isinstance(result, RPCInternalError)
        assert result.message == "Internal error: Type error"

    def test_custom_exception_handler(self):
        """Test that handlers for custom exceptions work correctly."""
        server = RpcServer()

        # Register a custom error handler for CustomException
        def handle_custom_exception(exc):
            return CustomRPCException()

        server.error_handler(CustomException, handle_custom_exception)

        # Test with a CustomException
        exception = CustomException("Custom error")
        result = server.on_error(exception)
        assert isinstance(result, CustomRPCException)
        assert result.code == 12345
        assert result.message == "Custom RPC exception"

    def test_handler_returning_none(self):
        """Test that handlers returning None don't affect the error handling chain."""
        server = RpcServer()

        # Register a custom error handler that returns None
        def handle_value_error_none(exc):
            return None

        server.error_handler(ValueError, handle_value_error_none)

        # Test with a ValueError
        exception = ValueError("Test error")
        result = server.on_error(exception)
        assert isinstance(result, RPCInternalError)
        assert result.message == "Internal error: Test error"

    def test_multiple_handlers(self):
        """Test that multiple handlers are tried in order."""
        server = RpcServer()

        # Register multiple handlers
        def handle_exception(exc):
            return None  # This handler doesn't handle the exception

        def handle_value_error(exc):
            return RPCException(code=11111, message="Handled by second handler")

        server.error_handler(Exception, handle_exception)
        server.error_handler(ValueError, handle_value_error)

        # Test with a ValueError
        exception = ValueError("Test error")
        result = server.on_error(exception)
        assert isinstance(result, RPCException)
        assert result.code == 11111
        assert result.message == "Handled by second handler"
