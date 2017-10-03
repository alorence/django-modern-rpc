# coding: utf-8
import json

from django.http.response import HttpResponse
from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import JSONRPC
from modernrpc.exceptions import RPCInternalError, RPCInvalidRequest, RPCParseError, RPCException
from modernrpc.handlers.base import RPCHandler
from modernrpc.core import RPCRequest

try:
    # Python 3
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2: json.loads will raise a ValueError when loading json
    JSONDecodeError = ValueError


class JSONRPCBatchResult(object):
    def __init__(self):
        self.results = []


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

    def process_request(self):

        encoding = self.request.encoding or 'utf-8'
        data = self.request.body.decode(encoding)
        body = self.loads(data)

        if isinstance(body, dict):

            # Store current request id, or None if request is a notification
            self.request_id = body.get('id')
            return self.process_single_request(body)

        elif isinstance(body, (list, tuple)):

            batch_result = JSONRPCBatchResult()

            for single_body in body:

                # If exception is raised early in request parsing, we need to have a null id in returned error response
                request_id = None

                try:
                    result = self.process_single_request(single_body)

                    request_id = single_body.get('id')
                    if request_id:
                        # As stated in documentation:
                        # "A Response object SHOULD exist for each Request object, except that there SHOULD NOT be any
                        # Response objects for notifications."
                        batch_result.results.append(self.get_success_payload(result, override_id=request_id))

                except RPCException as e:
                    batch_result.results.append(self.get_error_payload(e, override_id=request_id))

                except Exception as e:
                    rpc_exception = RPCInternalError(str(e))
                    batch_result.results.append(self.get_error_payload(rpc_exception, override_id=request_id))

            return batch_result

        else:
            raise RPCInvalidRequest()

    def process_single_request(self, body):

        if not isinstance(body, dict):
            raise RPCInvalidRequest()

        if 'jsonrpc' not in body:
            raise RPCInvalidRequest('Missing parameter "jsonrpc"')

        elif 'method' not in body:
            raise RPCInvalidRequest('Missing parameter "method"')

        if body['jsonrpc'] != '2.0':
            raise RPCInvalidRequest('The attribute "jsonrpc" must contains "2.0"')

        params = body.get('params')

        if isinstance(params, (list, tuple)):
            rpc_request = RPCRequest(body['method'], args=params)

        elif isinstance(params, dict):
            rpc_request = RPCRequest(body['method'], kwargs=params)

        else:
            rpc_request = RPCRequest(body['method'])

        return rpc_request.execute(self)

    @staticmethod
    def json_http_response(data, http_response_cls=HttpResponse):
        response = http_response_cls(data)
        response['Content-Type'] = 'application/json'
        return response

    def get_success_payload(self, data, override_id=None):

        if not (override_id or self.request_id):
            return None

        return {
            'id': override_id or self.request_id,
            'jsonrpc': '2.0',
            'result': data,
        }

    def result_success(self, data):

        if isinstance(data, JSONRPCBatchResult):

            # Result data for Batch requests is ready to dump, no need to insert it in a
            # response payload
            # As stated in standard:
            # "If there are no Response objects contained within the Response array as it is to be sent to the client,
            # the server MUST NOT return an empty Array and should return nothing at all."
            result = data.results or None

        else:
            result = self.get_success_payload(data)

        if not result:
            return HttpResponse(status=204)

        return self.json_http_response(self.dumps(result))

    def get_error_payload(self, exception, override_id=None):
        result = {
            'id': override_id or self.request_id,
            'jsonrpc': '2.0',
            'error': {
                'code': exception.code,
                'message': exception.message,
            }
        }

        if exception.data:
            result['error']['data'] = exception.data

        return result

    def result_error(self, exception, http_response_cls=HttpResponse):
        result = self.get_error_payload(exception)
        return self.json_http_response(self.dumps(result), http_response_cls=http_response_cls)
