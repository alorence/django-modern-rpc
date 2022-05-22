# coding: utf-8
# JSON-RPC error codes
# From https://www.jsonrpc.org/specification#error_object
#
# -32700              Parse error 	    Invalid JSON was received by the server.
#                                         An error occurred on the server while parsing the JSON text.
# -32600              Invalid Request 	The JSON sent is not a valid Request object.
# -32601              Method not found 	The method does not exist / is not available.
# -32602              Invalid params 	    Invalid method parameter(s).
# -32603              Internal error 	    Internal JSON-RPC error.
# -32000 to -32099 	Server error 	    Reserved for implementation-defined server-errors.
#
# XML-RPC error codes
# From http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php
#
# -32700 ---> parse error. not well formed
# -32701 ---> parse error. unsupported encoding
# -32702 ---> parse error. invalid character for encoding
# -32600 ---> server error. invalid xml-rpc. not conforming to spec.
# -32601 ---> server error. requested method not found
# -32602 ---> server error. invalid method parameters
# -32603 ---> server error. internal xml-rpc error
# -32500 ---> application error
# -32400 ---> system error
# -32300 ---> transport error
#
# In addition, the range -32099 .. -32000, inclusive is reserved for implementation defined server errors. Server
# errors which do not cleanly map to a specific error defined by this spec should be assigned to a number in this range.
# This leaves the remainder of the space available for application defined errors.

"""
Error handling is fully described in both XML & JSON-RPC standards. Each common error have an associated *faultCode*
and the response format is described, so errors can be handled correctly on the client side.

In django-modern-rpc, all errors are reported using a set of pre-defined exceptions. Thus, in JSON and XML-RPC handlers,
when an exception is caught, the correct error response is returned to the view and transmitted to the client.

This simplifies error management, and allow developers to simply return errors to clients from inside a RPC Method.
The error codes values are defined in:

- http://www.jsonrpc.org/specification#error_object for JSON-RPC
- http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php for XML-RPC

Pre-defined exceptions uses the following error codes::

    RPC_PARSE_ERROR = -32700
    RPC_INVALID_REQUEST = -32600
    RPC_METHOD_NOT_FOUND = -32601
    RPC_INVALID_PARAMS = -32602
    RPC_INTERNAL_ERROR = -32603

    # Used as minimal value for any custom error returned by the server
    RPC_CUSTOM_ERROR_BASE = -32099
    # Used as maximal value for any custom error returned by the server
    RPC_CUSTOM_ERROR_MAX = -32000

"""
from typing import Any

RPC_PARSE_ERROR = -32700
RPC_INVALID_REQUEST = -32600
RPC_METHOD_NOT_FOUND = -32601
RPC_INVALID_PARAMS = -32602
RPC_INTERNAL_ERROR = -32603

# Used as minimal value for any custom error returned by the server
RPC_CUSTOM_ERROR_BASE = -32099
# Used as maximal value for any custom error returned by the server
RPC_CUSTOM_ERROR_MAX = -32000


class RPCException(Exception):
    """
    This is the base class of all RPC exception. Custom exceptions raised by your RPC methods
    should inherits from RPCException.
    """

    def __init__(self, code: int, message: str, data: Any = None):
        super().__init__("[{}] {}".format(code, message))
        self.code = code
        self.message = message
        self.data = data


class RPCParseError(RPCException):
    """Raised by handlers if the request can't be read as valid JSON or XML data."""

    def __init__(self, message: str, data: Any = None):
        err_msg = "Parse error, unable to read the request: {}".format(message)
        super().__init__(RPC_PARSE_ERROR, err_msg, data)


class RPCInvalidRequest(RPCException):
    """Raised by handlers if incoming JSON or XML data is not a valid JSON-RPC or XML-RPC data."""

    def __init__(self, message: str, data: Any = None):
        err_msg = "Invalid request: {}".format(message)
        super().__init__(RPC_INVALID_REQUEST, err_msg, data)


class RPCMethodNotFound(RPCException):
    """Raised by handlers the RPC method called is not defined for the current entry point and protocol."""

    def __init__(self, name: str, data: Any = None):
        err_msg = 'Method not found: "{}"'.format(name)
        super().__init__(RPC_METHOD_NOT_FOUND, err_msg, data)


class RPCInvalidParams(RPCException):
    """Raised by handlers if the RPC method's params does not match the parameters in RPC request"""

    def __init__(self, message: str, data: Any = None):
        err_msg = "Invalid parameters: {}".format(message)
        super().__init__(RPC_INVALID_PARAMS, err_msg, data)


class RPCInternalError(RPCException):
    """Raised by handlers if any standard exception is raised during the execution of the RPC method."""

    def __init__(self, message: str, data: Any = None):
        err_msg = "Internal error: {}".format(message)
        super().__init__(RPC_INTERNAL_ERROR, err_msg, data)


class AuthenticationFailed(RPCException):
    """Raised when authentication system forbade execution of a RPC Method"""

    def __init__(self, method_name: str):
        super().__init__(
            RPC_INTERNAL_ERROR,
            'Authentication failed when calling "{}"'.format(method_name),
        )


# In 1.0, RPCUnknownMethod was renamed to RPCMethodNotFound
# Set as alias for backward compatibility
RPCUnknownMethod = RPCMethodNotFound
