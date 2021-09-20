# coding: utf-8
import json
import logging

from django.http.response import HttpResponse
from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import JSONRPC_PROTOCOL, RPCRequest
from modernrpc.exceptions import (RPCException, RPCInternalError,
                                  RPCInvalidRequest, RPCParseError)
from modernrpc.handlers.base import RPCHandler

try:
    # Python 3
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2: json.loads will raise a ValueError when loading json
    JSONDecodeError = ValueError

logger = logging.getLogger(__name__)


class JSONRPCBatchResult(object):
    def __init__(self):
        self.results = []


class JSONRPCHandler(RPCHandler):
    protocol = JSONRPC_PROTOCOL

    def __init__(self, entry_point):
        super(JSONRPCHandler, self).__init__(entry_point)

        self.decoder = import_string(settings.MODERNRPC_JSON_DECODER)
        self.encoder = import_string(settings.MODERNRPC_JSON_ENCODER)

    @staticmethod
    def valid_content_types():
        return [
            'application/json',
            'application/json-rpc',
            'application/jsonrequest',
        ]

    def parse_request(self, data):
        try:
            payload = json.loads(data, cls=self.decoder)
        except JSONDecodeError as err:
            raise RPCParseError(str(err))

        return RPCRequest(payload["method"], payload.get("params"))

    def build_result_success(self, data, **kwargs):

        result_payload = {
            'id': kwargs.get("request_id"),
            'jsonrpc': '2.0',
            'result': data,
        }
        return json.dumps(result_payload, cls=self.encoder)

    def build_result_error(self, code, message, **kwargs):
        result = {
            'id': kwargs.get("request_id"),
            'jsonrpc': '2.0',
            'error': {
                'code': code,
                'message': message,
            }
        }
        if "error_data" in kwargs:
            result["error"]["data"] = kwargs["error_data"]
        return json.dumps(result, cls=self.encoder)

    def loads(self, str_data):
        try:
            decoder = import_string(settings.MODERNRPC_JSON_DECODER)
            return json.loads(str_data, cls=decoder)

        except JSONDecodeError as jde:
            raise RPCParseError(str(jde))

    def dumps(self, obj):
        try:
            encoder = import_string(settings.MODERNRPC_JSON_ENCODER)
            return json.dumps(obj, cls=encoder)
        except Exception as exc:
            raise RPCInternalError('Unable to serialize result as valid JSON: ' + str(exc))

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
                        raise RPCInvalidRequest('Single RPC call payload must be a struct')

                    result = self.process_single_request(single_payload)

                    # As stated in documentation:
                    # "A Response object SHOULD exist for each Request object, except that there SHOULD NOT be any
                    # Response objects for notifications."
                    if request_id:
                        batch_result.results.append(self.json_success_response(result, override_id=request_id))

                except RPCException as exc:
                    logger.warning('RPC Exception raised in a JSON-RPC batch handling: %s', exc,
                                   exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
                    batch_result.results.append(self.json_error_response(exc, override_id=request_id))

                except Exception as exc:
                    logger.warning('Exception raised in a JSON-RPC batch handling: %s', exc,
                                   exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
                    rpc_exception = RPCInternalError(str(exc))
                    batch_result.results.append(self.json_error_response(rpc_exception, override_id=request_id))

            return batch_result

        else:
            raise RPCInvalidRequest('Bad JSON-RPC payload: {}'.format(str(payload)))

    def process_single_request(self, payload):

        if 'jsonrpc' not in payload:
            raise RPCInvalidRequest('Missing parameter "jsonrpc"')

        elif 'method' not in payload:
            raise RPCInvalidRequest('Missing parameter "method"')

        if payload['jsonrpc'] != '2.0':
            raise RPCInvalidRequest('The attribute "jsonrpc" must contain "2.0"')

        method_name = payload['method']

        params = payload.get('params')
        args = params if isinstance(params, (list, tuple)) else []
        kwargs = params if isinstance(params, dict) else {}

        return self.execute_procedure(method_name, args=args, kwargs=kwargs)

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

            # Result data for Batch requests is ready to dump, no need to insert it in a response payload
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

        if getattr(exception, 'data', None):
            result['error']['data'] = exception.data

        return result

    def result_error(self, exception, http_response_cls=HttpResponse):
        result = self.json_error_response(exception)
        return self.json_http_response(self.dumps(result), http_response_cls=http_response_cls)
