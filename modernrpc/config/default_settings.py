MODERNRPC_DEFAULT_ENCODING = "utf-8"

# Configure the format of the docstring used to document your RPC methods.
# Possible values are: '', 'rst' or 'md'
MODERNRPC_DOC_FORMAT = ""

MODERNRPC_XMLRPC_ASYNC_MULTICALL = False

# List of handler classes used by default in any ``RPCEntryPoint`` instance
MODERNRPC_HANDLERS = [
    "modernrpc.jsonrpc.handler.JsonRpcHandler",
    "modernrpc.xmlrpc.handler.XmlRpcHandler",
]

MODERNRPC_XML_DESERIALIZER = {"class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer", "kwargs": {}}
MODERNRPC_XML_SERIALIZER = {"class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer", "kwargs": {}}
MODERNRPC_JSON_DESERIALIZER = {"class": "modernrpc.jsonrpc.backends.json.PythonJsonDeserializer", "kwargs": {}}
MODERNRPC_JSON_SERIALIZER = {"class": "modernrpc.jsonrpc.backends.json.PythonJsonSerializer", "kwargs": {}}
