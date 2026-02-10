from typing import Any

# Constantes used in builtin exceptions
RPC_PARSE_ERROR = -32700
RPC_INVALID_REQUEST = -32600
RPC_METHOD_NOT_FOUND = -32601
RPC_INVALID_PARAMS = -32602
RPC_INTERNAL_ERROR = -32603

# Used as a minimal value for any custom error returned by the server
RPC_CUSTOM_ERROR_BASE = -32099
# Used as a maximal value for any custom error returned by the server
RPC_CUSTOM_ERROR_MAX = -32000


class RPCException(Exception):
    """
    Base class for all RPC exceptions. Custom exceptions raised by your remote procedures
    should inherit from RPCException.
    """

    def __init__(self, code: int, message: str, data: Any = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.data = data


class RPCParseError(RPCException):
    """Raised by handlers if the request can't be read as valid JSON or XML data."""

    def __init__(self, message: str, data: Any = None):
        err_msg = f"Parse error, unable to read the request: {message}"
        super().__init__(RPC_PARSE_ERROR, err_msg, data)


class RPCInsecureRequest(RPCParseError):
    """Raised in backends if the request is maliciously formed."""

    def __init__(self, message: str, data: Any = None):
        err_msg = f"Security error: {message}"
        RPCException.__init__(self, RPC_PARSE_ERROR, err_msg, data)


class RPCInvalidRequest(RPCException):
    """Raised by handlers if incoming JSON or XML data is not a valid JSON-RPC or XML-RPC data."""

    def __init__(self, message: str, data: Any = None):
        err_msg = f"Invalid request: {message}"
        super().__init__(RPC_INVALID_REQUEST, err_msg, data)


class RPCMethodNotFound(RPCException):
    """Raised by handlers when no procedure was found with the given name on the server (for the current protocol)."""

    def __init__(self, name: str, data: Any = None):
        err_msg = f'Method not found: "{name}"'
        super().__init__(RPC_METHOD_NOT_FOUND, err_msg, data)


class RPCInvalidParams(RPCException):
    """Raised by handlers if the request parameters do not match the procedure's expected ones."""

    def __init__(self, message: str, data: Any = None):
        err_msg = f"Invalid parameters: {message}"
        super().__init__(RPC_INVALID_PARAMS, err_msg, data)


class RPCInternalError(RPCException):
    """Raised by handlers if any standard exception is raised during the execution of the procedure."""

    def __init__(self, message: str, data: Any = None):
        err_msg = f"Internal error: {message}"
        super().__init__(RPC_INTERNAL_ERROR, err_msg, data)


class RPCMarshallingError(RPCException):
    def __init__(self, data: Any, exc: Exception):
        super().__init__(
            RPC_INTERNAL_ERROR,
            f"Unable to serialize result data: {data}. Original exception: {exc}",
        )


class AuthenticationError(RPCException):
    """Raised when the authentication system forbids execution of a remote procedure."""

    def __init__(self, method_name: str):
        super().__init__(
            RPC_INTERNAL_ERROR,
            f'Authentication failed when calling "{method_name}"',
        )


# In 1.0, RPCUnknownMethod were renamed to RPCMethodNotFound
# Set an alias for backward compatibility
RPCUnknownMethod = RPCMethodNotFound
