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
    """Wraps JSON-RPC specific information used to handle requests"""

    request_id = None  # type: Optional[int]
    version = "2.0"  # type: str
    # Note: In some case, it is possible to have a null request_id on standard request (not a notification), when an
    # error appear on request parsing. Thus, the result must be sent with an "id" parameter set to None (null in JSON)
    is_notification = False

    def set_jsonrpc_data(self, request_id, version, is_notification=False):
        self.request_id = request_id
        self.version = version
        self.is_notification = is_notification


class JsonSuccessResult(JsonRpcDataMixin, SuccessResult):
    """A JSON-RPC success result"""

    def format(self):
        return {
            "result": self.data,
        }


class JsonErrorResult(JsonRpcDataMixin, ErrorResult):
    """A JSON-RPC error result. Allows setting additional data, as specified in standard"""

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


# Alias to simplify typehints in JSONRPCHandler methods
JsonResult = Union[JsonSuccessResult, JsonErrorResult]


class JSONRPCHandler(RPCHandler):
    """Default JSON-RPC handler implementation"""

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

    @staticmethod
    def response_content_type() -> str:
        return "application/json"

    def process_request(self, request_body: str, context: RPCRequestContext) -> str:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, standard or batch request will be handled here.
        """
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

    def parse_request(self, request_body: str) -> Union[dict, List[dict]]:
        """
        Parse request body and return deserialized payload, or raise an RPCParseError

        Returned payload may be a dict (for standard request) or a list of dicts (for batch request).
        """
        try:
            payload = json.loads(request_body, cls=self.decoder)
        except (JSONDecodeError, Exception) as exc:
            raise RPCParseError(
                "Error while parsing JSON-RPC request: {}".format(exc)
            ) from exc

        return payload

    def process_single_request(
        self, request_data: dict, context: RPCRequestContext
    ) -> JsonResult:
        """Check and call the RPC method, based on given request dict."""
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
            _method = self.get_method_wrapper(method_name)

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

    def dumps_result(self, result: JsonResult) -> str:  # type: ignore[override]
        """
        Dumps result instance into a proper JSON-RPC response

        Notifications are supported here, based on result's `is_notification` member: return an empty string
        """
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
