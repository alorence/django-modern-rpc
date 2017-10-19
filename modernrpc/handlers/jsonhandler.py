# coding: utf-8
import json

from django.http.response import HttpResponse
from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import JSONRPC_PROTOCOL
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

    protocol = JSONRPC_PROTOCOL

    def __init__(self, request, entry_point):
        super(JSONRPCHandler, self).__init__(request, entry_point)
        self.request_id = None

    @staticmethod
    def valid_content_types():
        return [
            'application/json',
        ]

    def loads(self, str_data):
        try:
            decoder = import_string(settings.MODERNRPC_JSON_DECODER)
            return json.loads(str_data, cls=decoder)

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
        payload = self.loads(self.request.body.decode(encoding))

        if isinstance(payload, dict):

            # Store current request id, or None if request is a notification
            self.request_id = payload.get('id')
            return self.process_single_request(payload)

        elif isinstance(payload, (list, tuple)):

            batch_result = JSONRPCBatchResult()

            for single_payload in payload:
                try:
                    try:
                        request_id = single_payload.get('id')

                    except AttributeError:
                        request_id = None
                        raise RPCInvalidRequest()

                    result = self.process_single_request(single_payload)

                    if request_id:
                        # As stated in documentation:
                        # "A Response object SHOULD exist for each Request object, except that there SHOULD NOT be any
                        # Response objects for notifications."
                        batch_result.results.append(self.json_success_response(result, override_id=request_id))

                except RPCException as e:
                    batch_result.results.append(self.json_error_response(e, override_id=request_id))

                except Exception as e:
                    rpc_exception = RPCInternalError(str(e))
                    batch_result.results.append(self.json_error_response(rpc_exception, override_id=request_id))

            return batch_result

        else:
            raise RPCInvalidRequest()

    def process_single_request(self, payload):

        if 'jsonrpc' not in payload:
            raise RPCInvalidRequest('Missing parameter "jsonrpc"')

        elif 'method' not in payload:
            raise RPCInvalidRequest('Missing parameter "method"')

        if payload['jsonrpc'] != '2.0':
            raise RPCInvalidRequest('The attribute "jsonrpc" must contains "2.0"')

        params = payload.get('params')

        if isinstance(params, (list, tuple)):
            rpc_request = RPCRequest(payload['method'], args=params)

        elif isinstance(params, dict):
            rpc_request = RPCRequest(payload['method'], kwargs=params)

        else:
            rpc_request = RPCRequest(payload['method'])

        return rpc_request.execute(self)

    @staticmethod
    def json_http_response(data, http_response_cls=HttpResponse):
        response = http_response_cls(data)
        response['Content-Type'] = 'application/json'
        return response

    def json_success_response(self, data, override_id=None):

        return {
            'id': override_id or self.request_id,
            'jsonrpc': '2.0',
            'result': data,
        }

    def result_success(self, data):

        result = None

        if isinstance(data, JSONRPCBatchResult):

            # Result data for Batch requests is ready to dump, no need to insert it in a
            # response payload
            # As stated in standard:
            # "If there are no Response objects contained within the Response array as it is to be sent to the client,
            # the server MUST NOT return an empty Array and should return nothing at all."
            result = data.results or None

        elif self.request_id is not None:
            result = self.json_success_response(data)

        if result is None:
            # Nothing should be returned when JSON-RPC request is a notification or a batch
            # of notification only requests
            return HttpResponse(status=204)

        return self.json_http_response(self.dumps(result))

    def json_error_response(self, exception, override_id=None):

        result = {
            'id': override_id or self.request_id,
            'jsonrpc': '2.0',
            'error': {
                'code': exception.code,
                'message': exception.message,
            }
        }

        try:
            result['error']['data'] = exception.data
        exception AttributeError:
            pass

        return result

    def result_error(self, exception, http_response_cls=HttpResponse):
        result = self.json_error_response(exception)
        return self.json_http_response(self.dumps(result), http_response_cls=http_response_cls)
