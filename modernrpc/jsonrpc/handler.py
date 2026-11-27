import asyncio
import logging
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import TYPE_CHECKING, ClassVar, TypeAlias

from django.utils.module_loading import import_string

from modernrpc import Protocol, RpcRequestContext
from modernrpc.config import settings
from modernrpc.constants import NOT_SET
from modernrpc.exceptions import RPCException, RPCInvalidRequest
from modernrpc.handler import RpcHandler
from modernrpc.types import DictStrAny, RpcErrorResult, RpcRequest, RpcSuccessResult

if TYPE_CHECKING:
    from collections.abc import Iterator

    from modernrpc.jsonrpc.backends import JsonRpcDeserializer, JsonRpcSerializer

logger = logging.getLogger(__name__)


RequestIdType: TypeAlias = str | int | float | None


@dataclass
class JsonRpcRequest(RpcRequest):
    """
    JSON-RPC request specific data
    """

    kwargs: DictStrAny = field(default_factory=dict)
    request_id: RequestIdType | object = NOT_SET
    jsonrpc: str = "2.0"

    @property
    def is_notification(self) -> bool:
        return self.request_id is NOT_SET


JsonRpcSuccessResult: TypeAlias = RpcSuccessResult[JsonRpcRequest]
JsonRpcErrorResult: TypeAlias = RpcErrorResult[JsonRpcRequest]
JsonRpcResult: TypeAlias = JsonRpcSuccessResult | JsonRpcErrorResult

# An item of a batch request: a valid request, or the error raised while validating the corresponding item
JsonRpcBatchItem: TypeAlias = JsonRpcRequest | RPCInvalidRequest


class JsonRpcHandler(RpcHandler[JsonRpcRequest]):
    """Default JSON-RPC handler implementation"""

    protocol = Protocol.JSON_RPC
    valid_content_types: ClassVar[list[str]] = ["application/json", "application/json-rpc", "application/jsonrequest"]
    response_content_type = "application/json"
    success_result_type = JsonRpcSuccessResult
    error_result_type = JsonRpcErrorResult

    def __init__(self) -> None:
        deserializer_config = settings.MODERNRPC_JSON_DESERIALIZER
        deserializer_klass: type[JsonRpcDeserializer] = import_string(deserializer_config["class"])
        deserializer_kwargs: DictStrAny = deserializer_config.get("kwargs", {})
        self.deserializer: JsonRpcDeserializer = deserializer_klass(**deserializer_kwargs)

        serializer_config = settings.MODERNRPC_JSON_SERIALIZER
        serializer_klass: type[JsonRpcSerializer] = import_string(serializer_config["class"])
        serializer_kwargs: DictStrAny = serializer_config.get("kwargs", {})
        self.serializer: JsonRpcSerializer = serializer_klass(**serializer_kwargs)

    def build_empty_dummy_request(self) -> JsonRpcRequest:
        return JsonRpcRequest(request_id=None, method_name="")

    def serialize_result(self, result: JsonRpcResult) -> str:
        return self.serializer.dumps(result)

    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, a standard or a batch request will be handled here.
        """
        try:
            parsed_request = self.deserializer.loads(request_body)

        except RPCException as exc:
            return self.build_serialized_error_response(exc, context)

        # Parsed request is a list, we should handle it as a batch request
        if isinstance(parsed_request, list):
            try:
                context.server.check_batch_size(len(parsed_request))
            except RPCException as exc:
                return self.build_serialized_error_response(exc, context)

            return self.process_batch_request(parsed_request, context)

        # By default, handle a standard single request
        result = self.process_single_request(parsed_request, context)

        if parsed_request.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        try:
            return self.serialize_result(result)

        except RPCException as exc:
            return self.build_serialized_error_response(exc, context, parsed_request)

    async def aprocess_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, a standard or a batch request will be handled here.
        """
        try:
            parsed_request = self.deserializer.loads(request_body)

        except RPCException as exc:
            return self.build_serialized_error_response(exc, context)

        # Parsed request is a list, we should handle it as a batch request
        if isinstance(parsed_request, list):
            try:
                context.server.check_batch_size(len(parsed_request))
            except RPCException as exc:
                return self.build_serialized_error_response(exc, context)
            return await self.aprocess_batch_request(parsed_request, context)

        # By default, handle a standard single request
        result = await self.aprocess_single_request(parsed_request, context)

        if parsed_request.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        try:
            return self.serialize_result(result)
        except RPCException as exc:
            return self.build_serialized_error_response(exc, context, parsed_request)

    def build_invalid_item_result(self, exc: RPCException, context: RpcRequestContext) -> JsonRpcResult:
        """
        Build the error result for an invalid item of a batch request. Since the request id can't be reliably
        determined, a null id is used, as required by the JSON-RPC 2.0 specification.
        """
        return self.build_request_error_response(exc, context)

    def process_batch_request(
        self, rpc_requests: list[JsonRpcBatchItem], context: RpcRequestContext
    ) -> str | tuple[HTTPStatus, str]:
        # Process each request and store corresponding results (success or error)
        results: Iterator[JsonRpcResult] = (
            self.build_invalid_item_result(item, context)
            if isinstance(item, RPCException)
            else self.process_single_request(item, context)
            for item in rpc_requests
        )

        # Filter out notification results
        filtered_results = [result for result in results if not result.request.is_notification]

        # Return JSON-serialized response list
        if filtered_results:
            return self.serializer.dumps(filtered_results)

        # Notifications-only batch request returns 204 no content
        return HTTPStatus.NO_CONTENT, ""

    async def _aprocess_batch_item(self, item: JsonRpcBatchItem, context: RpcRequestContext) -> JsonRpcResult:
        if isinstance(item, RPCException):
            return self.build_invalid_item_result(item, context)
        return await self.aprocess_single_request(item, context)

    async def aprocess_batch_request(
        self, requests: list[JsonRpcBatchItem], context: RpcRequestContext
    ) -> str | tuple[HTTPStatus, str]:
        # Process each request and store corresponding results (success or error)
        results: list[JsonRpcResult] = await asyncio.gather(
            *(self._aprocess_batch_item(item, context) for item in requests)
        )

        # Filter out notification results
        filtered_results = [result for result in results if not result.request.is_notification]

        # Return JSON-serialized response list
        if filtered_results:
            return self.serializer.dumps(filtered_results)

        # Notifications-only batch request returns 204 no content
        return HTTPStatus.NO_CONTENT, ""
