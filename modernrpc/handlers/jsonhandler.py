from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from django.utils.module_loading import import_string

from modernrpc import Protocol
from modernrpc.conf import settings
from modernrpc.exceptions import RPCException
from modernrpc.handlers.base import (
    JsonRpcErrorResult,
    JsonRpcRequest,
    JsonRpcResult,
    JsonRpcSuccessResult,
    RpcHandler,
)

if TYPE_CHECKING:
    from typing import Any, Generator

    from modernrpc.backends.base import JsonRpcDeserializer, JsonRpcSerializer
    from modernrpc.core import RpcRequestContext

logger = logging.getLogger(__name__)


class JsonRpcHandler(RpcHandler[JsonRpcRequest]):
    """Default JSON-RPC handler implementation"""

    protocol = Protocol.JSON_RPC

    def __init__(self) -> None:
        deserializer_klass: type[JsonRpcDeserializer] = import_string(settings.MODERNRPC_JSON_DESERIALIZER["class"])
        deserializer_kwargs: dict[str, Any] = settings.MODERNRPC_JSON_DESERIALIZER.get("kwargs", {})
        self.deserializer: JsonRpcDeserializer = deserializer_klass(**deserializer_kwargs)

        serializer_klass: type[JsonRpcSerializer] = import_string(settings.MODERNRPC_JSON_SERIALIZER["class"])
        serializer_kwargs: dict[str, Any] = settings.MODERNRPC_JSON_SERIALIZER.get("kwargs", {})
        self.serializer: JsonRpcSerializer = serializer_klass(**serializer_kwargs)

    @classmethod
    def valid_content_types(cls) -> list[str]:
        return [
            "application/json",
            "application/json-rpc",
            "application/jsonrequest",
        ]

    @classmethod
    def response_content_type(cls) -> str:
        return "application/json"

    @property
    def success_result_type(self) -> type[JsonRpcSuccessResult]:
        return JsonRpcSuccessResult

    @property
    def error_result_type(self) -> type[JsonRpcErrorResult]:
        return JsonRpcErrorResult

    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, standard or batch request will be handled here.
        """
        try:
            parsed_request = self.deserializer.loads(request_body)
        except RPCException as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            # We can't extract request_id from incoming request. According to the spec, a null 'id' should be used
            # in response payload
            fake_request = JsonRpcRequest(request_id=None, method_name="")
            return self.serializer.dumps(JsonRpcErrorResult(fake_request, exc.code, exc.message))

        # Parsed request is an Iterable, we should handle it as batch request
        if isinstance(parsed_request, list):
            return self.process_batch_request(parsed_request, context)

        # By default, handle a standard single request
        result = self.process_single_request(parsed_request, context)

        if parsed_request.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        return self.serializer.dumps(result)

    def process_batch_request(
        self, requests: list[JsonRpcRequest], context: RpcRequestContext
    ) -> str | tuple[HTTPStatus, str]:
        # Process each request and store corresponding results (success or error)
        results: Generator[JsonRpcResult] = (self.process_single_request(request, context) for request in requests)

        # Filter out notification results
        filtered_results = [result for result in results if not result.request.is_notification]

        # Return JSON-serialized response list
        if filtered_results:
            return self.serializer.dumps(filtered_results)

        # Notifications-only batch request returns 204 no content
        return HTTPStatus.NO_CONTENT, ""
