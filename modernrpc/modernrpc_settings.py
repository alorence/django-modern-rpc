# coding: utf-8
from django.conf import settings

# Override this to use a different JSON serializer when decoding JSON-RPC request
MODERNRPC_JSON_DECODER = getattr(settings, 'MODERNRPC_JSON_DECODER', 'json.decoder.JSONDecoder')

# Override this to use a different JSON deserializer when encoding JSON-RPC response
MODERNRPC_JSON_ENCODER = getattr(settings, 'MODERNRPC_JSON_ENCODER', 'django.core.serializers.json.DjangoJSONEncoder')
