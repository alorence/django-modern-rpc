# coding: utf-8

# List of python modules containing RPC methods.
MODERNRPC_METHODS_MODULES = []

# Decoder class used to convert python data to JSON
MODERNRPC_JSON_DECODER = 'json.decoder.JSONDecoder'
# Encoder class used to convert JSON data to python values
MODERNRPC_JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'


# Control how builtin types are handled by XML-RPC serializer and deserializer
MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = True
# Control how XML-RPC serializer will handle None values. If set to True, None values will be converted to <nil>
MODERNRPC_XMLRPC_ALLOW_NONE = True
# Configure the default encoding used by XML encoder
MODERNRPC_XMLRPC_DEFAULT_ENCODING = None

# List of handler classes used by default in any ``RPCEntryPoint`` instance
MODERNRPC_HANDLERS = [
    'modernrpc.handlers.JSONRPCHandler',
    'modernrpc.handlers.XMLRPCHandler',
]

# Default name associated with anonymous ``RPCEntryPoint``
MODERNRPC_DEFAULT_ENTRYPOINT_NAME = '__default_entry_point__'

# Configure the format of the docstring used to document your RPC methods.
# Possible values are: '', 'rst' or 'md'
MODERNRPC_DOC_FORMAT = ''

MODERNRPC_PY2_STR_TYPE = None
MODERNRPC_PY2_STR_ENCODING = 'UTF-8'
