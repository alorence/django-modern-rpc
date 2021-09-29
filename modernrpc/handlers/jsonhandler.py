# coding: utf-8
import json
import logging

from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import JSONRPC_PROTOCOL, RpcRequest, RpcResult
from modernrpc.exceptions import RPCParseError, RPCInvalidRequest, RPC_INTERNAL_ERROR
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

    def parse_request(self, request_body):
        try:
            payload = json.loads(request_body, cls=self.decoder)
        except JSONDecodeError as err:
            raise RPCParseError("Error while parsing XML-RPC request: {}".format(err))

        if isinstance(payload, list):
            requests = []
            for single_payload in payload:
                try:
                    requests.append(
                        RpcRequest(
                            single_payload.get("method"),
                            single_payload.get("params"),
                            jsonrpc=single_payload.get("jsonrpc"),
                            request_id=single_payload.get("id"),
                        )
                    )
                except Exception:
                    requests.append(RpcRequest(None))
            return requests

        elif isinstance(payload, dict):
            return RpcRequest(
                payload.get("method"),
                payload.get("params"),
                jsonrpc=payload.get("jsonrpc"),
                request_id=payload.get("id")
            )

        raise RPCInvalidRequest("Bad JSON-RPC payload")

    def validate_request(self, rpc_request):
        if not rpc_request.method_name:
            raise RPCInvalidRequest('Missing parameter "method"')
        elif not rpc_request.jsonrpc:
            raise RPCInvalidRequest('Missing parameter "jsonrpc"')
        elif rpc_request.jsonrpc != "2.0":
            raise RPCInvalidRequest('jsonrpc version must be set to 2.0')

    def _build_error_result_data(self, rpc_result):
        result_payload = {
            'id': rpc_result.request_id,
            'jsonrpc': "2.0",
            "error": {
                'code': rpc_result.error_code,
                'message': rpc_result.error_message
            },
        }
        if rpc_result.error_data:
            result_payload["error"]["data"] = rpc_result.error_data
        return json.dumps(result_payload, cls=self.encoder)

    def _build_success_result_data(self, rpc_result):
        result_payload = {
            'id': rpc_result.request_id,
            'jsonrpc': "2.0",
            "result": rpc_result.success_data,
        }
        try:
            return json.dumps(result_payload, cls=self.encoder)
        except TypeError:
            rpc_result.set_error(RPC_INTERNAL_ERROR, "Unable to serialize result")
            return self._build_error_result_data(rpc_result)

    def _build_single_response_data(self, single_result):
        """
        :param single_result:
        :type single_result: RpcResult
        :return:
        """

        if single_result.is_error():
            return self._build_error_result_data(single_result)

        if single_result.request_id is None:
            # Notification
            return ""

        return self._build_success_result_data(single_result)

    def build_response_data(self, res):
        """
        :param res:
        :type res: List[RpcResult] | RpcResult
        :return:
        """
        if isinstance(res, list):
            final_result = [
                self._build_single_response_data(r)
                for r in res
            ]

            batch_response_data = ",\n".join(filter(None, final_result))
            if batch_response_data:
                return "[{}]".format(batch_response_data)
            return ""
        else:
            return self._build_single_response_data(res)
