# coding: utf-8
import json
import logging
from json.decoder import JSONDecodeError
from typing import Optional, Generator, List, Union, Any

from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import Protocol, RPCRequestContext
from modernrpc.exceptions import (
    RPCParseError,
    RPC_INTERNAL_ERROR,
    RPCException,
    RPCInvalidRequest,
    RPC_INVALID_REQUEST,
)
from modernrpc.handlers.base import RPCHandler, SuccessResult, ErrorResult

logger = logging.getLogger(__name__)

REQUEST_ID = "_jsonrpc_request_id"
VERSION = "_jsonrpc_request_version"


class JsonRpcDataMixin:
    request_id = None  # type: Optional[int]
    version = "2.0"  # type: str
    is_notification = False

    def set_jsonrpc_data(self, request_id, version, is_notification=False):
        self.request_id = request_id
        self.version = version
        self.is_notification = is_notification


class JsonSuccessResult(JsonRpcDataMixin, SuccessResult):
    def format(self):
        return {
            "result": self.data,
        }


class JsonErrorResult(JsonRpcDataMixin, ErrorResult):
    def __init__(self, code: int, message: str, data: Any = None):
        super().__init__(code, message)
        self.data = data

    def format(self):
        _part = {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }
        if self.data:
            _part["error"]["data"] = self.data
        return _part


JsonResult = Union[JsonSuccessResult, JsonErrorResult]


class JSONRPCHandler(RPCHandler):
    protocol = Protocol.JSON_RPC

    def __init__(self, entry_point):
        super().__init__(entry_point)

        self.decoder = import_string(settings.MODERNRPC_JSON_DECODER)
        self.encoder = import_string(settings.MODERNRPC_JSON_ENCODER)

    @staticmethod
    def valid_content_types() -> List[str]:
        return [
            "application/json",
            "application/json-rpc",
            "application/jsonrequest",
        ]

    def parse_request(self, request_body: str) -> Union[dict, list]:
        try:
            payload = json.loads(request_body, cls=self.decoder)
        except (JSONDecodeError, Exception) as exc:
            raise RPCParseError("Error while parsing JSON-RPC request: {}".format(exc))

        return payload

    def dumps_result(self, result: JsonResult) -> str:  # type: ignore[override]

        if result.is_notification:
            return ""

        # First, define the ...
        result_base = {
            "id": result.request_id,
            "jsonrpc": result.version,
        }

        try:
            return json.dumps({**result_base, **result.format()}, cls=self.encoder)

        except Exception as exc:
            # Error on result serialization: serialize an error instead
            error_msg = "Unable to serialize result: {}".format(exc)
            logger.error(error_msg, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            error_result = JsonErrorResult(RPC_INTERNAL_ERROR, error_msg)
            return json.dumps(
                {**result_base, **error_result.format()}, cls=self.encoder
            )

    def process_single_request(
        self, request_data: dict, context: RPCRequestContext
    ) -> JsonResult:

        if not isinstance(request_data, dict):
            error_msg = (
                'Invalid JSON-RPC payload, expected "object", found "{}"'.format(
                    type(request_data).__name__
                )
            )
            return JsonErrorResult(RPC_INVALID_REQUEST, error_msg)

        # Retrieve method name, and get corresponding RPCMethod instance.
        # Raises RPCInvalidMethod as early as possible when not found
        method_name = request_data.get("method")

        # ...
        params = request_data.get("params")
        args = params if isinstance(params, (list, tuple)) else []
        kwargs = params if isinstance(params, dict) else {}

        is_notification = "id" not in request_data
        request_id = request_data.get("id")
        jsonrpc_version = request_data.get("jsonrpc")

        try:
            # Perform standard error checks
            if not method_name:
                raise RPCInvalidRequest('Missing parameter "method"')

            if not jsonrpc_version:
                raise RPCInvalidRequest('Missing parameter "jsonrpc"')

            if jsonrpc_version != "2.0":
                raise RPCInvalidRequest(
                    'Parameter "jsonrpc" has an unsupported value "{}". It must be set to "2.0"'.format(
                        jsonrpc_version
                    )
                )

            if not is_notification and request_id is None:
                raise RPCInvalidRequest(
                    'Parameter "id" has an unsupported "null" value. It must be set to a positive integer value, '
                    'or must be completely removed from request payload for special "notification" requests'
                )
            _method = self._get_called_method(method_name)

            result_data = _method.execute(context, args, kwargs)
            result = JsonSuccessResult(result_data)  # type: JsonResult

        except RPCException as exc:
            logger.warning(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = JsonErrorResult(exc.code, exc.message, exc.data)

        except Exception as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = JsonErrorResult(RPC_INTERNAL_ERROR, str(exc))

        result.set_jsonrpc_data(
            request_id=request_id,
            version=jsonrpc_version,
            is_notification=is_notification,
        )
        return result

    def process_request(self, request_body: str, context: RPCRequestContext) -> str:

        try:
            parsed_request = self.parse_request(request_body)
        except RPCException as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            return self.dumps_result(JsonErrorResult(exc.code, exc.message))

        else:
            # Parsed request is a list, we should handle it as batch request
            if isinstance(parsed_request, list):
                # Process each request, getting the resulting JsonResult instance (success or error)
                results = (
                    self.process_single_request(_req, context)
                    for _req in parsed_request
                )  # type: Generator[JsonResult, None, None]

                # Transform each result into its str result representation and remove notifications result
                str_results = (
                    self.dumps_result(_res)
                    for _res in results
                    if not _res.is_notification
                )  # type: Generator[str, None, None]

                # Rebuild final JSON content manually
                concatenated_results = ", ".join(str_results)

                # Return JSON-serialized response list, or empty string for notifications-only request
                return "[%s]" % concatenated_results if concatenated_results else ""

            # By default, handle a standard single request
            return self.dumps_result(
                self.process_single_request(parsed_request, context)
            )
