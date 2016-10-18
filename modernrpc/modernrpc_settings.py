# coding: utf-8
from django.conf import settings

#: Override this to use a different JSON serializer when decoding JSON-RPC request
MODERNRPC_JSON_DECODER = getattr(settings, 'MODERNRPC_JSON_DECODER', 'json.decoder.JSONDecoder')

#: Override this to use a different JSON deserializer when encoding JSON-RPC response
MODERNRPC_JSON_ENCODER = getattr(settings, 'MODERNRPC_JSON_ENCODER', 'django.core.serializers.json.DjangoJSONEncoder')

#: Override these to change the key used in kwars for request object
MODERNRPC_REQUEST_PARAM_NAME = getattr(settings, 'MODERNRPC_REQUEST_PARAM_NAME', 'request')
#: Override these to change the key used in kwars for protocol string
MODERNRPC_PROTOCOL_PARAM_NAME = getattr(settings, 'MODERNRPC_PROTOCOL_PARAM_NAME', 'rpc_protocol')
#: Override these to change the key used in kwars for entry point name
MODERNRPC_ENTRY_POINT_PARAM_NAME = getattr(settings, 'MODERNRPC_ENTRY_POINT_PARAM_NAME', 'entry_point')

#: Override these to change the key used in kwars for entry point name
MODERNRPC_HANDLERS = getattr(settings, 'MODERNRPC_HANDLERS', [
    'modernrpc.handlers.JSONRPCHandler',
    'modernrpc.handlers.XMLRPCHandler',
])

#: The name set to any entry point which doesn't declare it explicitely
MODERNRPC_DEFAULT_ENTRYPOINT_NAME = getattr(settings, 'MODERNRPC_DEFAULT_ENTRYPOINT_NAME', '__default_entry_point__')

#: Set to False if you want to manipulate dates with DateTime class from Python XML RPC builtin lib.
#: If set to True, dates will be passed as datetime to the RPC function.
MODERNRPC_XML_USE_BUILTIN_TYPES = getattr(settings, 'MODERNRPC_XML_USE_BUILTIN_TYPES', True)
