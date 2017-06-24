# coding: utf-8
import json

from django.http.response import HttpResponse
from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.exceptions import RPCInternalError, RPCInvalidRequest, RPCParseError
from modernrpc.handlers.base import RPCHandler

try:
    # Python 3
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2: json.loads will raise a ValueError when loading json
    JSONDecodeError = ValueError

JSONRPC = '__json_rpc'


class JSONRPCHandler(RPCHandler):

    protocol = JSONRPC

    def __init__(self, request, entry_point):
        super(JSONRPCHandler, self).__init__(request, entry_point)
        self.request_id = None

    @staticmethod
    def valid_content_types():
        return [
            'application/json',
        ]

    def loads(self, data):
        try:
            decoder = import_string(settings.MODERNRPC_JSON_DECODER)
            return json.loads(data, cls=decoder)
        except JSONDecodeError as e:
            raise RPCParseError(str(e))

    def dumps(self, obj):
        try:
            encoder = import_string(settings.MODERNRPC_JSON_ENCODER)
            return json.dumps(obj, cls=encoder)
        except Exception:
            raise RPCInternalError('Unable to serialize result as valid JSON')

    def parse_request(self):

        encoding = self.request.encoding or 'utf-8'
        data = self.request.body.decode(encoding)
        body = self.loads(data)

        if not isinstance(body, dict):
            raise RPCInvalidRequest('Payload object must be a struct')

        if 'id' in body:
            self.request_id = body['id']
        else:
            raise RPCInvalidRequest('Missing parameter "id"')

        if 'jsonrpc' not in body:
            raise RPCInvalidRequest('Missing parameter "jsonrpc"')
        elif 'method' not in body:
            raise RPCInvalidRequest('Missing parameter "method"')

        if body['jsonrpc'] != '2.0':
            raise RPCInvalidRequest('The attribute "jsonrpc" must contains "2.0"')

        return body['method'], body.get('params', [])

    @staticmethod
    def json_http_response(data, http_response_cls=HttpResponse):
        response = http_response_cls(data)
        response['Content-Type'] = 'application/json'
        return response

    def result_success(self, data):
        result = {
            'id': self.request_id,
            'jsonrpc': '2.0',
            'result': data,
        }
        return self.json_http_response(self.dumps(result))

    def result_error(self, exception, http_response_cls=HttpResponse):
        result = {
            'id': self.request_id,
            'jsonrpc': '2.0',
            'error': {
                'code': exception.code,
                'message': exception.message,
            }
        }

        return self.json_http_response(self.dumps(result), http_response_cls=http_response_cls)
