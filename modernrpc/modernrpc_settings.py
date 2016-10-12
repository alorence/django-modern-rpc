# coding: utf-8
from django.conf import settings


JSONRPC_DEFAULT_DECODER = getattr(settings, 'JSONRPC_DEFAULT_DECODER', 'json.decoder.JSONDecoder')
JSONRPC_DEFAULT_ENCODER = getattr(settings, 'JSONRPC_DEFAULT_ENCODER', 'django.core.serializers.json.DjangoJSONEncoder')
