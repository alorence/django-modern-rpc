from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Iterable

from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import ProcedureWrapper, Protocol, RpcRequestContext
from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPCException
from modernrpc.handlers.base import (
    JsonRpcErrorResult,
    JsonRpcRequest,
    JsonRpcResult,
    JsonRpcSuccessResult,
    RpcHandler,
)

if TYPE_CHECKING:
    from typing import Any

    from modernrpc.backends.base import JsonRpcDeserializer, JsonRpcSerializer

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

    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Parse request and process it, according to its kind. Standard request as well as batch request is supported.

        Delegates to `process_single_request()` to perform most of the checks and procedure execution. Depending on the
        result of `parse_request()`, standard or batch request will be handled here.
        """
        try:
            structured_req: JsonRpcRequest | Iterable[JsonRpcRequest] = self.deserializer.loads(request_body)
        except RPCException as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            # We can't extract request_id from incoming request. According to the spec, a null 'id' should be used
            # in response payload
            fake_request = JsonRpcRequest(request_id=None, method_name="")
            return self.serializer.dumps(JsonRpcErrorResult(fake_request, exc.code, exc.message))

        # Parsed request is an Iterable, we should handle it as batch request
        if isinstance(structured_req, Iterable):
            # Process each request, getting the resulting JsonResult instance (success or error)
            results: Iterable[JsonRpcResult] = (
                self.process_single_request(request, context) for request in structured_req
            )

            # Drop notification results
            results = [result for result in results if not result.request.is_notification]

            # Return JSON-serialized response list
            if results:
                return self.serializer.dumps(results)

            # Notifications-only batch request returns 204 no content
            return HTTPStatus.NO_CONTENT, ""

        # By default, handle a standard single request
        result = self.process_single_request(structured_req, context)

        if structured_req.is_notification:
            return HTTPStatus.NO_CONTENT, ""

        return self.serializer.dumps(result)

    # TODO: restore this ASAP
    # @staticmethod
    # def check_request(request_data: dict) -> None:
    #     """Perform request validation raises RPCInvalidRequest on any error"""
    #
    #     method_name = request_data.get("method")
    #     jsonrpc_version = request_data.get("jsonrpc")
    #     is_notification = "id" not in request_data
    #     request_id = request_data.get("id")
    #
    #     if not method_name:
    #         raise RPCInvalidRequest('Missing parameter "method"')
    #
    #     if not jsonrpc_version:
    #         raise RPCInvalidRequest('Missing parameter "jsonrpc"')
    #
    #     if jsonrpc_version != "2.0":
    #         raise RPCInvalidRequest(
    #             f'Parameter "jsonrpc" has an unsupported value "{jsonrpc_version}". It must be set to "2.0"'
    #         )
    #
    #     if not is_notification and type(request_id) not in (type(None), int, float, str):
    #         request_data["id"] = None
    #         raise RPCInvalidRequest(
    #             'Parameter "id" has an unsupported value. According to JSON-RPC 2.0 standard, it must '
    #             "be a String, a Number or a Null value."
    #         )

    def process_single_request(self, rpc_request: JsonRpcRequest, context: RpcRequestContext) -> JsonRpcResult:
        """Check and call the RPC method, based on given request dict."""
        # FIXME
        # try:
        #     # Perform standard error checks
        #     self.check_request(request_data)
        # except:
        #     pass

        try:
            wrapper: ProcedureWrapper = context.server.get_procedure(rpc_request.method_name)
            result_data = wrapper.execute(context, rpc_request.args, rpc_request.kwargs)
            return JsonRpcSuccessResult(request=rpc_request, data=result_data)

        except RPCException as exc:
            logger.warning(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = JsonRpcErrorResult(request=rpc_request, code=exc.code, message=exc.message, data=exc.data)

        except Exception as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = JsonRpcErrorResult(request=rpc_request, code=RPC_INTERNAL_ERROR, message=str(exc))

        return result
