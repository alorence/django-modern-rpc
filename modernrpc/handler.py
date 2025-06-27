from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic

from modernrpc.exceptions import RPCMethodNotFound
from modernrpc.types import RequestType, RpcErrorResult, RpcSuccessResult

if TYPE_CHECKING:
    from http import HTTPStatus
    from typing import Any, ClassVar

    from django.http import HttpRequest

    from modernrpc import Protocol, RpcRequestContext


logger = logging.getLogger(__name__)


class RpcHandler(ABC, Generic[RequestType]):
    """Base class for concrete RPC Handlers. Provide an interface as well as some common methods implementations."""

    protocol: Protocol
    valid_content_types: ClassVar[list[str]]
    response_content_type: str
    success_result_type: type[RpcSuccessResult[RequestType]]
    error_result_type: type[RpcErrorResult[RequestType]]

    @classmethod
    def can_handle(cls, request: HttpRequest) -> bool:
        """
        Return True if this instance can handle the given request.

        The default implementation will check Content-Type for a supported value
        """
        return getattr(request, "content_type", "").lower() in cls.valid_content_types

    # @abc.abstractmethod
    def build_success_result(self, request: RequestType, data: Any) -> RpcSuccessResult[RequestType]:
        return self.success_result_type(request=request, data=data)

    # @abc.abstractmethod
    def build_error_result(
        self, request: RequestType, code: int, message: str, data: Any = None
    ) -> RpcErrorResult[RequestType]:
        return self.error_result_type(request=request, code=code, message=message, data=data)

    def process_single_request(
        self, rpc_request: RequestType, context: RpcRequestContext
    ) -> RpcSuccessResult[RequestType] | RpcErrorResult[RequestType]:
        """Check and call the RPC method, based on the given request dict."""

        try:
            wrapper = context.server.get_procedure_wrapper(rpc_request.method_name, self.protocol)

        except RPCMethodNotFound as exc:
            # exc variable cannot be reused here without triggering an error with static type checker
            # In this particular case, an error handler may decide to convert the given RPCMethodNotFound to a more
            # generic RPCException (or one of its subclasses).
            excp = context.server.on_error(exc, context)
            return self.build_error_result(request=rpc_request, code=excp.code, message=excp.message, data=excp.data)

        try:
            result_data = wrapper.execute(context, rpc_request.args, getattr(rpc_request, "kwargs", None))

        except Exception as exc:
            exc = context.server.on_error(exc, context)
            return self.build_error_result(request=rpc_request, code=exc.code, message=exc.message, data=exc.data)

        return self.build_success_result(rpc_request, result_data)

    async def aprocess_single_request(
        self, rpc_request: RequestType, context: RpcRequestContext
    ) -> RpcSuccessResult[RequestType] | RpcErrorResult[RequestType]:
        """
        Asynchronous version of process_single_request().
        Check and call the RPC method, based on the given request dict.
        """

        try:
            wrapper = context.server.get_procedure_wrapper(rpc_request.method_name, self.protocol)

        except RPCMethodNotFound as exc:
            # exc variable cannot be reused here without triggering an error with static type checker
            # In this particular case, an error handler may decide to convert the given RPCMethodNotFound to a more
            # generic RPCException (or one of its subclasses).
            excp = context.server.on_error(exc, context)
            return self.build_error_result(request=rpc_request, code=excp.code, message=excp.message, data=excp.data)

        try:
            result_data = await wrapper.aexecute(context, rpc_request.args, getattr(rpc_request, "kwargs", None))

        except Exception as exc:
            exc = context.server.on_error(exc, context)
            return self.build_error_result(request=rpc_request, code=exc.code, message=exc.message, data=exc.data)

        return self.build_success_result(rpc_request, result_data)

    @abstractmethod
    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[HTTPStatus, str]:
        """
        Fully process a request. Return the str content ready to be sent as HttpResponse.

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
