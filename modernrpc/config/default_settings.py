from typing import Any

MODERNRPC_DEFAULT_ENCODING = "utf-8"

# Configure the format of the docstring used to document your RPC methods.
# Possible values are: '', 'rst' or 'md'
MODERNRPC_DOC_FORMAT = ""

MODERNRPC_XMLRPC_ASYNC_MULTICALL = False

# When False, unexpected exceptions raised while processing a request (i.e. not subclasses of RPCException, plus
# serialization errors) are returned to the client with a generic "Internal error" message. Full details are logged.
# When True, the original exception message is returned to the client. Do not enable this in production.
MODERNRPC_EXPOSE_INTERNAL_ERRORS = False

# Maximum number of calls allowed in a single JSON-RPC batch request or XML-RPC system.multicall call.
# Set to None to disable the limit.
MODERNRPC_MAX_BATCH_SIZE: int | None = 100

# List of handler classes used by default in any ``RpcServer`` instance
MODERNRPC_HANDLERS = [
    "modernrpc.jsonrpc.handler.JsonRpcHandler",
    "modernrpc.xmlrpc.handler.XmlRpcHandler",
]

MODERNRPC_XML_DESERIALIZER: dict[str, Any] = {
    "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer",
    "kwargs": {},
}
MODERNRPC_XML_SERIALIZER: dict[str, Any] = {
    "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
    "kwargs": {},
}
MODERNRPC_JSON_DESERIALIZER: dict[str, Any] = {
    "class": "modernrpc.jsonrpc.backends.json.PythonJsonDeserializer",
    "kwargs": {},
}
MODERNRPC_JSON_SERIALIZER: dict[str, Any] = {
    "class": "modernrpc.jsonrpc.backends.json.PythonJsonSerializer",
    "kwargs": {},
}
