# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import TYPE_CHECKING, Union

from django.utils.module_loading import import_string

from modernrpc import Protocol
from modernrpc.config import settings
from modernrpc.constants import NOT_SET
from modernrpc.exceptions import RPCException
from modernrpc.handler import RpcHandler
from modernrpc.types import DictStrAny, RpcErrorResult, RpcRequest, RpcSuccessResult

if TYPE_CHECKING:
    from typing import ClassVar, Generator

    from modernrpc import RpcRequestContext
    from modernrpc.jsonrpc.backends import JsonRpcDeserializer, JsonRpcSerializer

logger = logging.getLogger(__name__)


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


RequestIdType = Union[str, int, float, None]
JsonRpcSuccessResult = RpcSuccessResult[JsonRpcRequest]
JsonRpcErrorResult = RpcErrorResult[JsonRpcRequest]
JsonRpcResult = Union[JsonRpcSuccessResult, JsonRpcErrorResult]


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

    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, a standard or a batch request will be handled here.
        """
        try:
            parsed_request = self.deserializer.loads(request_body)

        except RPCException as exc:
            # We can't extract request_id from an incoming request. According to the spec, a
            # null 'id' should be used in response payload
            fake_request = JsonRpcRequest(request_id=None, method_name="")
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(fake_request, exc.code, exc.message))

        # Parsed request is an Iterable, we should handle it as a batch request
        if isinstance(parsed_request, list):
            return self.process_batch_request(parsed_request, context)

        # By default, handle a standard single request
        result = self.process_single_request(parsed_request, context)

        if parsed_request.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        try:
            return self.serializer.dumps(result)
        except RPCException as exc:
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(parsed_request, exc.code, exc.message))

    async def aprocess_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, a standard or a batch request will be handled here.
        """
        try:
            parsed_request = self.deserializer.loads(request_body)

        except RPCException as exc:
            # We can't extract request_id from an incoming request. According to the spec, a
            # null 'id' should be used in response payload
            fake_request = JsonRpcRequest(request_id=None, method_name="")
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(fake_request, exc.code, exc.message))

        # Parsed request is an Iterable, we should handle it as a batch request
        if isinstance(parsed_request, list):
            return await self.aprocess_batch_request(parsed_request, context)

        # By default, handle a standard single request
        result = await self.aprocess_single_request(parsed_request, context)

        if parsed_request.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        try:
            return self.serializer.dumps(result)
        except RPCException as exc:
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(parsed_request, exc.code, exc.message))

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

    async def aprocess_batch_request(
        self, requests: list[JsonRpcRequest], context: RpcRequestContext
    ) -> str | tuple[HTTPStatus, str]:
        # Process each request and store corresponding results (success or error)
        results: list[JsonRpcResult] = await asyncio.gather(
            *(self.aprocess_single_request(request, context) for request in requests)
        )

        # Filter out notification results
        filtered_results = [result for result in results if not result.request.is_notification]

        # Return JSON-serialized response list
        if filtered_results:
            return self.serializer.dumps(filtered_results)

        # Notifications-only batch request returns 204 no content
        return HTTPStatus.NO_CONTENT, ""
