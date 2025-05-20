from __future__ import annotations

MODERNRPC_DEFAULT_ENCODING = "utf-8"

# List of handler classes used by default in any ``RPCEntryPoint`` instance
MODERNRPC_HANDLERS = [
    "modernrpc.handlers.JsonRpcHandler",
    "modernrpc.handlers.XmlRpcHandler",
]

# Configure the format of the docstring used to document your RPC methods.
# Possible values are: '', 'rst' or 'md'
MODERNRPC_DOC_FORMAT = ""

# Set to False if you need to disable exception logging
MODERNRPC_LOG_EXCEPTIONS = True

# Set to False if you want to disable automatic registration of system procedures
MODERNRPC_REGISTER_SYSTEM_PROCEDURES = True

MODERNRPC_JSON_DESERIALIZER = {"class": "modernrpc.backends.builtin_json.BuiltinJSON", "kwargs": {}}
MODERNRPC_JSON_SERIALIZER = {"class": "modernrpc.backends.builtin_json.BuiltinJSON", "kwargs": {}}
MODERNRPC_XML_DESERIALIZER = {"class": "modernrpc.backends.builtin_xmlrpc.BuiltinXmlRpc", "kwargs": {}}
MODERNRPC_XML_SERIALIZER = {"class": "modernrpc.backends.builtin_xmlrpc.BuiltinXmlRpc", "kwargs": {}}
