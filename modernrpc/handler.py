import logging
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, ClassVar, Generic

from django.http import HttpRequest, HttpResponse

from modernrpc.constants import Protocol
from modernrpc.core import RpcRequestContext
from modernrpc.exceptions import RPCException
from modernrpc.types import RequestType, RpcErrorResult, RpcSuccessResult

logger = logging.getLogger(__name__)


class RpcHandler(ABC, Generic[RequestType]):
    """Base class for concrete RPC Handlers. Provide an interface as well as some common methods implementations."""

    protocol: Protocol
    valid_content_types: ClassVar[list[str]]
    response_content_type: str

    @classmethod
    def can_handle(cls, request: HttpRequest) -> bool:
        """
        Return True if this instance can handle the given request.

        The default implementation will check Content-Type for a supported value
        """
        content_type = request.content_type or ""
        return content_type.lower() in cls.valid_content_types

    @staticmethod
    def build_success_result(rpc_request: RequestType, data: Any) -> RpcSuccessResult[RequestType]:
        """Build a RpcSuccessResult for the given request. Subclass may override this method to customize the output"""
        return RpcSuccessResult(request=rpc_request, data=data)

    def build_error_result(
        self, exc: BaseException, context: RpcRequestContext, rpc_request: RequestType | None = None
    ) -> RpcErrorResult[RequestType]:
        """
        Build the error result for a request that failed outside the procedure itself: unreadable body, invalid
        request, too many calls in a batch, result that can't be serialized, etc.

        The exception is passed through `context.server.on_error()` first. Its `data` is never part of the result,
        since it only holds internal details here (e.g. the original exception raised by a deserializer). When
        `rpc_request` is None (the request couldn't be read), a dummy request is used, see build_dummy_request().
        """
        rpc_exc = context.server.on_error(exc, context)
        if rpc_request is None:
            rpc_request = self.build_dummy_request()
        return RpcErrorResult(request=rpc_request, code=rpc_exc.code, message=rpc_exc.message)

    @abstractmethod
    def build_dummy_request(self) -> RequestType:
        """Build the request object used to answer a request that couldn't be read. See
        build_request_error_result()."""

    @abstractmethod
    def serialize_result(self, result: RpcSuccessResult[RequestType] | RpcErrorResult[RequestType]) -> str:
        """Serialize a single result, according to the protocol implemented by the concrete handler. May raise
        an RPCException (RPCMarshallingError) when the result contains data that can't be serialized."""

    def serialize_result_safely(
        self, result: RpcSuccessResult[RequestType] | RpcErrorResult[RequestType], context: RpcRequestContext
    ) -> str:
        """Same as serialize_result(), but when the result can't be serialized, serialize the corresponding error."""
        try:
            return self.serialize_result(result)

        except RPCException as exc:
            return self.serialize_request_error(exc, context, result.request)

    def serialize_request_error(
        self, exc: BaseException, context: RpcRequestContext, rpc_request: RequestType | None = None
    ) -> str:
        """Same as build_request_error_result(), but return the serialized result."""
        return self.serialize_result(self.build_error_result(exc, context, rpc_request))

    def build_http_response(self, content: str | tuple[HTTPStatus, str]) -> HttpResponse:
        """Build the HttpResponse from the value returned by process_request() or serialize_request_error()."""
        status, body = content if isinstance(content, tuple) else (HTTPStatus.OK, content)
        return HttpResponse(body, status=status, content_type=self.response_content_type)

    def process_single_request(
        self, rpc_request: RequestType, context: RpcRequestContext
    ) -> RpcSuccessResult[RequestType] | RpcErrorResult[RequestType]:  # FIXME: replace return type by RpcResult?
        """Check and call the remote procedure, based on the given request dict."""
        try:
            wrapper = context.server.get_procedure_wrapper(rpc_request.method_name, self.protocol)
            result_data = wrapper.execute(context, rpc_request.args, getattr(rpc_request, "kwargs", None))

        except Exception as exc:  # ruff: ignore[BLE001]
            return self.build_error_result(exc, context, rpc_request)

        return self.build_success_result(rpc_request, result_data)

    async def aprocess_single_request(
        self, rpc_request: RequestType, context: RpcRequestContext
    ) -> RpcSuccessResult[RequestType] | RpcErrorResult[RequestType]:
        """
        Asynchronous version of process_single_request().
        Check and call the remote procedure, based on the given request dict.
        """
        try:
            wrapper = context.server.get_procedure_wrapper(rpc_request.method_name, self.protocol)
            result_data = await wrapper.aexecute(context, rpc_request.args, getattr(rpc_request, "kwargs", None))

        except Exception as exc:  # ruff: ignore[BLE001]
            return self.build_error_result(exc, context, rpc_request)

        return self.build_success_result(rpc_request, result_data)

    @abstractmethod
    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Fully process a request. Return the serialized content (optionally with an HTTP status), ready to be
        passed to build_http_response().

        This is the only method the view is supposed to call after choosing the right handler.
        Concrete implementation must perform all work here, according to its protocol specifications.

        Important: This method should delegate concrete procedure execution to process_single_request(). This will
        help to implement multi-request (JSON-RPC batch / XML-RPC system.multicall) features.

        Implementations of this method must ensure no exception is raised from here. All code must be secured
        to return a proper RPC error response on any exception.
        """

    @abstractmethod
    async def aprocess_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Asynchronous version of process_request(). It takes the same arguments and returns the same result.
        Delegates its work to aprocess_single_request() instead of process_single_request() for async support.
        """
