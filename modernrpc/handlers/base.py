from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, TypeVar

from modernrpc.exceptions import RPCMethodNotFound

if TYPE_CHECKING:
    from http import HTTPStatus
    from typing import Any, ClassVar

    from django.http import HttpRequest

    from modernrpc import Protocol, RpcRequestContext


logger = logging.getLogger(__name__)


@dataclass
class RpcRequest:
    """Basic information about RPC request"""

    method_name: str
    args: list[Any] | tuple[Any] = field(default_factory=list)


RequestType = TypeVar("RequestType", bound=RpcRequest)


@dataclass
class GenericRpcResult(Generic[RequestType]):
    request: RequestType


@dataclass
class GenericRpcSuccessResult(GenericRpcResult[RequestType]):
    data: Any = None


@dataclass
class GenericRpcErrorResult(GenericRpcResult[RequestType]):
    code: int
    message: str
    # This field is only dumped to JSON-RPC clients!
    data: Any = None


class RpcHandler(ABC, Generic[RequestType]):
    """Base class for concrete RPC Handlers. Provide an interface as well as some common methods implementations."""

    protocol: Protocol
    valid_content_types: ClassVar[list[str]]
    response_content_type: str
    success_result_type: type[GenericRpcSuccessResult[RequestType]]
    error_result_type: type[GenericRpcErrorResult[RequestType]]

    @classmethod
    def can_handle(cls, request: HttpRequest) -> bool:
        """
        Return True if this instance can handle the given request.

        Default implementation will check Content-Type for supported value
        """
        return getattr(request, "content_type", "").lower() in cls.valid_content_types

    # @abc.abstractmethod
    def build_success_result(self, request: RequestType, data: Any) -> GenericRpcSuccessResult[RequestType]:
        return self.success_result_type(request=request, data=data)

    # @abc.abstractmethod
    def build_error_result(
        self, request: RequestType, code: int, message: str, data: Any = None
    ) -> GenericRpcErrorResult[RequestType]:
        return self.error_result_type(request=request, code=code, message=message, data=data)

    def process_single_request(
        self, rpc_request: RequestType, context: RpcRequestContext
    ) -> GenericRpcSuccessResult[RequestType] | GenericRpcErrorResult[RequestType]:
        """Check and call the RPC method, based on given request dict."""

        try:
            wrapper = context.server.get_procedure_wrapper(rpc_request.method_name, self.protocol)

        except RPCMethodNotFound as exc:
            # exc variable cannot be reused here without triggering an error with static type checker
            # In this particular case, an error handler may decide to convert the given RPCMethodNotFound to a more
            # generic RPCException (or one of its subclasses).
            _exc = context.server.on_error(exc)
            return self.build_error_result(request=rpc_request, code=_exc.code, message=_exc.message, data=_exc.data)

        try:
            result_data = wrapper.execute(context, rpc_request.args, getattr(rpc_request, "kwargs", None))

        except Exception as exc:
            exc = context.server.on_error(exc)
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
