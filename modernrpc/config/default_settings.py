MODERNRPC_DEFAULT_ENCODING = "utf-8"

# List of handler classes used by default in any ``RPCEntryPoint`` instance
MODERNRPC_HANDLERS = [
    "modernrpc.jsonrpc.handler.JsonRpcHandler",
    "modernrpc.xmlrpc.handler.XmlRpcHandler",
]

MODERNRPC_JSON_DESERIALIZER = {"class": "modernrpc.jsonrpc.backends.json.PythonJsonBackend", "kwargs": {}}
MODERNRPC_JSON_SERIALIZER = {"class": "modernrpc.jsonrpc.backends.json.PythonJsonBackend", "kwargs": {}}
MODERNRPC_XML_DESERIALIZER = {"class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcBackend", "kwargs": {}}
MODERNRPC_XML_SERIALIZER = {"class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcBackend", "kwargs": {}}

# Configure the format of the docstring used to document your RPC methods.
# Possible values are: '', 'rst' or 'md'
MODERNRPC_DOC_FORMAT = ""

MODERNRPC_XMLRPC_ASYNC_MULTICALL = False
