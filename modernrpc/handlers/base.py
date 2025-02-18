from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

from modernrpc.constants import NOT_SET
from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPCException

if TYPE_CHECKING:
    from http import HTTPStatus

    from django.http import HttpRequest

    from modernrpc import Protocol
    from modernrpc.core import RpcRequestContext


logger = logging.getLogger(__name__)


@dataclass
class RpcRequest:
    """Basic information about RPC request.
    XML-RPC protocol will use this as it"""

    method_name: str
    args: list[Any] | tuple[Any] = field(default_factory=list)


T = TypeVar("T")


@dataclass
class GenericRpcResult(Generic[T]):
    request: T

    def is_error(self) -> bool:
        return False


@dataclass
class GenericRpcSuccessResult(GenericRpcResult[T]):
    data: Any = None


@dataclass
class GenericRpcErrorResult(GenericRpcResult[T]):
    code: int
    message: str
    # This field is only dumped to JSON-RPC clients!
    data: Any = None

    def is_error(self) -> bool:
        return True


class XmlRpcRequest(RpcRequest): ...


# class XmlRpcSuccessResult(GenericRpcSuccessResult[XmlRpcRequest]):
#     """An XML-RPC success result"""
XmlRpcSuccessResult = GenericRpcSuccessResult[XmlRpcRequest]


# class XmlRpcErrorResult(GenericRpcErrorResult[XmlRpcRequest]): ...
XmlRpcErrorResult = GenericRpcErrorResult[XmlRpcRequest]

# Alias to simplify typehints in XMLRPCHandler methods
XmlRpcResult = Union[XmlRpcSuccessResult, XmlRpcErrorResult]


RequestIdType = Union[str, int, float, None]


@dataclass
class JsonRpcRequest(RpcRequest):
    """
    JSON-RPC request specific data
    """

    kwargs: dict[str, Any] = field(default_factory=dict)
    request_id: RequestIdType | object = NOT_SET
    jsonrpc: str = "2.0"

    @property
    def is_notification(self) -> bool:
        return self.request_id is NOT_SET


# @dataclass
# class JsonRpcSuccessResult(GenericRpcSuccessResult[JsonRpcRequest]): ...
JsonRpcSuccessResult = GenericRpcSuccessResult[JsonRpcRequest]


# @dataclass
# class JsonRpcErrorResult(GenericRpcErrorResult[JsonRpcRequest]): ...
JsonRpcErrorResult = GenericRpcErrorResult[JsonRpcRequest]

# Alias to simplify typehints in JSONRPCHandler methods
JsonRpcResult = Union[JsonRpcSuccessResult, JsonRpcErrorResult]


RequestType = TypeVar("RequestType", bound=RpcRequest)


class RpcHandler(ABC, Generic[RequestType]):
    """Base class for concrete RPC Handlers. Provide an interface as well as some common methods implementations."""

    protocol: Protocol

    @classmethod
    @abstractmethod
    def valid_content_types(cls) -> list[str]:
        """Return the list of content-types supported by the concrete handler"""

    @classmethod
    @abstractmethod
    def response_content_type(cls) -> str:
        """Return the Content-Type value to set in responses"""

    @property
    @abstractmethod
    def success_result_type(self) -> type[GenericRpcSuccessResult[RequestType]]: ...

    @property
    @abstractmethod
    def error_result_type(self) -> type[GenericRpcErrorResult[RequestType]]: ...

    @classmethod
    def can_handle(cls, request: HttpRequest) -> bool:
        """
        Return True if this instance can handle the given request.

        Default implementation will check Content-Type for supported value
        """
        return getattr(request, "content_type", "").lower() in cls.valid_content_types()

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
            call_kwargs = None if not hasattr(rpc_request, "kwargs") else rpc_request.kwargs
            result_data = wrapper.execute(context, rpc_request.args, call_kwargs)

        except RPCException as exc:
            return self.build_error_result(request=rpc_request, code=exc.code, message=exc.message, data=exc.data)

        except Exception as exc:
            return self.build_error_result(request=rpc_request, code=RPC_INTERNAL_ERROR, message=str(exc))

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
