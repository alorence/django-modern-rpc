from __future__ import annotations

import json
import logging
from abc import ABC
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Generator, Union

from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import Protocol, RPCRequestContext
from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPC_INVALID_REQUEST, RPCException, RPCInvalidRequest, RPCParseError
from modernrpc.handlers.base import BaseResult, DataMixin, ErrorMixin, RPCHandler

logger = logging.getLogger(__name__)

REQUEST_ID = "_jsonrpc_request_id"
VERSION = "_jsonrpc_request_version"

RequestIdType = Union[str, int, float, None]


@dataclass
class JsonRpcDataMixin(BaseResult, ABC):
    """Wraps JSON-RPC specific information used to handle requests"""

    request_id: RequestIdType = None
    version: str = "2.0"
    # Note: Since null request_id is allowed by specs, we must have a separate boolean field for notifications
    is_notification = False

    def set_jsonrpc_data(self, request_id, version, is_notification=False):
        self.request_id = request_id
        self.version = version
        self.is_notification = is_notification


@dataclass
class JsonSuccessResult(JsonRpcDataMixin, DataMixin):
    """A JSON-RPC success result"""

    def serializable_data(self):
        return {
            "result": self.data,
        }


@dataclass
class JsonErrorResult(JsonRpcDataMixin, DataMixin, ErrorMixin):
    """A JSON-RPC error result. Allows setting additional data, as specified in standard"""

    def serializable_data(self):
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

    def __init__(self, entry_point: str):
        super().__init__(entry_point)

        self.decoder = import_string(settings.MODERNRPC_JSON_DECODER)
        self.encoder = import_string(settings.MODERNRPC_JSON_ENCODER)

    @staticmethod
    def valid_content_types() -> list[str]:
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
                results: Generator[JsonResult, None, None] = (
                    self.process_single_request(_req, context) for _req in parsed_request
                )

                # Transform each result into its str result representation and remove notifications result
                dumped_results: Generator[str, None, None] = (
                    self.dumps_result(_res) for _res in results if not _res.is_notification
                )

                # Rebuild final JSON content manually
                serialized_result = ", ".join(dumped_results)

                # Return JSON-serialized response list, or empty string for notifications-only request
                return f"[{serialized_result}]" if serialized_result else ""

            # By default, handle a standard single request
            return self.dumps_result(self.process_single_request(parsed_request, context))

    def parse_request(self, request_body: str) -> dict | list[dict]:
        """
        Parse request body and return deserialized payload, or raise an RPCParseError

        Returned payload may be a dict (for standard request) or a list of dicts (for batch request).
        """
        try:
            payload = json.loads(request_body, cls=self.decoder)
        except (JSONDecodeError, Exception) as exc:
            raise RPCParseError(f"Error while parsing JSON-RPC request: {exc}") from exc

        return payload

    @staticmethod
    def check_request(request_data: dict) -> None:
        """Perform request validation raises RPCInvalidRequest on any error"""

        method_name = request_data.get("method")
        jsonrpc_version = request_data.get("jsonrpc")
        is_notification = "id" not in request_data
        request_id = request_data.get("id")

        if not method_name:
            raise RPCInvalidRequest('Missing parameter "method"')

        if not jsonrpc_version:
            raise RPCInvalidRequest('Missing parameter "jsonrpc"')

        if jsonrpc_version != "2.0":
            raise RPCInvalidRequest(
                f'Parameter "jsonrpc" has an unsupported value "{jsonrpc_version}". It must be set to "2.0"'
            )

        if not is_notification and type(request_id) not in (type(None), int, float, str):
            request_data["id"] = None
            raise RPCInvalidRequest(
                'Parameter "id" has an unsupported value. According to JSON-RPC 2.0 standard, it must '
                "be a String, a Number or a Null value."
            )

    def process_single_request(self, request_data: dict, context: RPCRequestContext) -> JsonResult:
        """Check and call the RPC method, based on given request dict."""
        if not isinstance(request_data, dict):
            error_msg = f'Invalid JSON-RPC payload, expected "object", found "{type(request_data).__name__}"'
            return JsonErrorResult(RPC_INVALID_REQUEST, error_msg)

        params = request_data.get("params")
        args = params if isinstance(params, (list, tuple)) else []
        kwargs = params if isinstance(params, dict) else {}

        try:
            # Perform standard error checks
            self.check_request(request_data)

            _method = self.get_method_wrapper(request_data.get("method"))  # type: ignore[arg-type]

            result_data = _method.execute(context, args, kwargs)
            result: JsonResult = JsonSuccessResult(result_data)

        except RPCException as exc:
            logger.warning(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = JsonErrorResult(exc.code, exc.message, exc.data)

        except Exception as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = JsonErrorResult(RPC_INTERNAL_ERROR, str(exc))

        result.set_jsonrpc_data(
            request_id=request_data.get("id"),
            version=request_data.get("jsonrpc"),
            is_notification="id" not in request_data,
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
            return json.dumps({**result_base, **result.serializable_data()}, cls=self.encoder)

        except Exception as exc:
            # Error on result serialization: serialize an error instead
            error_msg = f"Unable to serialize result: {exc}"
            logger.error(error_msg, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            error_result = JsonErrorResult(RPC_INTERNAL_ERROR, error_msg)
            return json.dumps({**result_base, **error_result.serializable_data()}, cls=self.encoder)
