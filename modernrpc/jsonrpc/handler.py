import asyncio
import logging
from collections.abc import Iterable
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

    def __init__(self) -> None:
        deserializer_config = settings.MODERNRPC_JSON_DESERIALIZER
        deserializer_klass: type[JsonRpcDeserializer] = import_string(deserializer_config["class"])
        deserializer_kwargs: DictStrAny = deserializer_config.get("kwargs", {})
        self.deserializer: JsonRpcDeserializer = deserializer_klass(**deserializer_kwargs)

        serializer_config = settings.MODERNRPC_JSON_SERIALIZER
        serializer_klass: type[JsonRpcSerializer] = import_string(serializer_config["class"])
        serializer_kwargs: DictStrAny = serializer_config.get("kwargs", {})
        self.serializer: JsonRpcSerializer = serializer_klass(**serializer_kwargs)

    def build_dummy_request(self) -> JsonRpcRequest:
        # The JSON-RPC 2.0 specification requires a null id when the request id can't be determined
        return JsonRpcRequest(request_id=None, method_name="")

    def serialize_result(self, result: JsonRpcResult) -> str:
        return self.serializer.dumps(result)

    def parse_request(self, request_body: str, context: RpcRequestContext) -> JsonRpcRequest | list[JsonRpcBatchItem]:
        """
        Deserialize the request body into a single request or a batch request (list of items).

        :raise RPCException: if the body can't be parsed, or if a batch request contains too many items
        """
        parsed_request = self.deserializer.loads(request_body)
        if isinstance(parsed_request, list):
            context.server.check_batch_size(len(parsed_request))
        return parsed_request

    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, a standard or a batch request will be handled here.
        """
        try:
            parsed_request = self.parse_request(request_body, context)

        except RPCException as exc:
            return self.serialize_request_error(exc, context)

        if isinstance(parsed_request, list):
            return self.process_batch_request(parsed_request, context)

        result = self.process_single_request(parsed_request, context)
        if parsed_request.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        return self.serialize_result_safely(result, context)

    async def aprocess_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """Asynchronous version of process_request()."""
        try:
            parsed_request = self.parse_request(request_body, context)

        except RPCException as exc:
            return self.serialize_request_error(exc, context)

        if isinstance(parsed_request, list):
            return await self.aprocess_batch_request(parsed_request, context)

        result = await self.aprocess_single_request(parsed_request, context)
        if parsed_request.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        return self.serialize_result_safely(result, context)

    def _serialize_batch_results(self, results: Iterable[JsonRpcResult]) -> str | tuple[HTTPStatus, str]:
        """Serialize results of a batch request, ignoring notifications. Return 204 if no result remains."""
        filtered_results = [result for result in results if not result.request.is_notification]
        if filtered_results:
            return self.serializer.dumps(filtered_results)

        return HTTPStatus.NO_CONTENT, ""

    def process_batch_request(
        self, rpc_requests: list[JsonRpcBatchItem], context: RpcRequestContext
    ) -> str | tuple[HTTPStatus, str]:
        """Process each item of a batch request and return the serialized list of results."""
        results = (
            self.build_error_result(item, context)
            if isinstance(item, RPCException)
            else self.process_single_request(item, context)
            for item in rpc_requests
        )
        return self._serialize_batch_results(results)

    async def _aprocess_batch_item(self, item: JsonRpcBatchItem, context: RpcRequestContext) -> JsonRpcResult:
        if isinstance(item, RPCException):
            return self.build_error_result(item, context)
        return await self.aprocess_single_request(item, context)

    async def aprocess_batch_request(
        self, rpc_requests: list[JsonRpcBatchItem], context: RpcRequestContext
    ) -> str | tuple[HTTPStatus, str]:
        """Asynchronous version of process_batch_request(). Items are processed concurrently."""
        results = await asyncio.gather(*(self._aprocess_batch_item(item, context) for item in rpc_requests))
        return self._serialize_batch_results(results)
