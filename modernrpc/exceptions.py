# coding: utf-8
"""
JSON-RPC error codes
From http://www.jsonrpc.org/specification#error_object

-32700              Parse error 	    Invalid JSON was received by the server.
                                        An error occurred on the server while parsing the JSON text.
-32600              Invalid Request 	The JSON sent is not a valid Request object.
-32601              Method not found 	The method does not exist / is not available.
-32602              Invalid params 	    Invalid method parameter(s).
-32603              Internal error 	    Internal JSON-RPC error.
-32000 to -32099 	Server error 	    Reserved for implementation-defined server-errors.

XML-RPC error codes
From http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php

-32700 ---> parse error. not well formed
-32701 ---> parse error. unsupported encoding
-32702 ---> parse error. invalid character for encoding
-32600 ---> server error. invalid xml-rpc. not conforming to spec.
-32601 ---> server error. requested method not found
-32602 ---> server error. invalid method parameters
-32603 ---> server error. internal xml-rpc error
-32500 ---> application error
-32400 ---> system error
-32300 ---> transport error

In addition, the range -32099 .. -32000, inclusive is reserved for implementation defined server errors. Server
errors which do not cleanly map to a specific error defined by this spec should be assigned to a number in this range.
This leaves the remainder of the space available for application defined errors.
"""

RPC_PARSE_ERROR = -32700
RPC_INVALID_REQUEST = -32600
RPC_METHOD_NOT_FOUND = -32601
RPC_INVALID_PARAMS = -32602
RPC_INTERNAL_ERROR = -32603

RPC_CUSTOM_ERROR_BASE = -32099
RPC_CUSTOM_ERROR_MAX = -32000


class RPCException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message


class RPCParseError(RPCException):

    def __init__(self, message=''):
        err_msg = 'Parse error, unable to read the request; {}'.format(message)
        super(RPCParseError, self).__init__(RPC_PARSE_ERROR, err_msg)


class RPCInvalidRequest(RPCException):

    def __init__(self, message=''):
        err_msg = 'Invalid request, {}'.format(message)
        super(RPCInvalidRequest, self).__init__(RPC_INVALID_REQUEST, err_msg)


class RPCUnknownMethod(RPCException):

    def __init__(self, name):
        err_msg = 'Method not found: {}'.format(name)
        super(RPCUnknownMethod, self).__init__(RPC_METHOD_NOT_FOUND, err_msg)


class RPCInvalidParams(RPCException):

    def __init__(self, message=''):
        err_msg = 'Invalid parameters, {}'.format(message)
        super(RPCInvalidParams, self).__init__(RPC_INVALID_PARAMS, err_msg)


class RPCInternalError(RPCException):

    def __init__(self, message):
        err_msg = 'Internal error: {}'.format(message)
        super(RPCInternalError, self).__init__(RPC_INTERNAL_ERROR, err_msg)
