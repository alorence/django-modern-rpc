from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.core import Protocol, RpcRequestContext


T = TypeVar("T")

logger = logging.getLogger(__name__)


@dataclass
class RpcRequest:
    """Basic information about RPC request.
    XML-RPC protocol will use this as it"""

    method_name: str
    args: list[Any] = field(default_factory=list)


@dataclass
class GenericRpcResult(Generic[T]):
    request: T


@dataclass
class GenericRpcSuccessResult(GenericRpcResult[T]):
    data: Any = None


@dataclass
class GenericRpcErrorResult(GenericRpcResult[T]):
    code: int
    message: str
    # This field is only dumped to JSON-RPC clients!
    data: Any = None


class XmlRpcRequest(RpcRequest): ...


class XmlRpcSuccessResult(GenericRpcSuccessResult[XmlRpcRequest]):
    """An XML-RPC success result"""


class XmlRpcErrorResult(GenericRpcErrorResult[XmlRpcRequest]): ...


# Alias to simplify typehints in XMLRPCHandler methods
XmlRpcResult = Union[XmlRpcSuccessResult, XmlRpcErrorResult]


RequestIdType = Union[str, int, float, None]
UNDEFINED = object()


@dataclass
class JsonRpcRequest(RpcRequest):
    """
    JSON-RPC request specific data
    """

    kwargs: dict[str, Any] = field(default_factory=dict)
    request_id: RequestIdType | object = UNDEFINED
    jsonrpc: str = "2.0"

    @property
    def is_notification(self) -> bool:
        return self.request_id is UNDEFINED


@dataclass
class JsonRpcSuccessResult(GenericRpcSuccessResult[JsonRpcRequest]): ...


@dataclass
class JsonRpcErrorResult(GenericRpcErrorResult[JsonRpcRequest]): ...


# Alias to simplify typehints in JSONRPCHandler methods
JsonRpcResult = Union[JsonRpcSuccessResult, JsonRpcErrorResult]


class RpcHandler(ABC):
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

    @classmethod
    def can_handle(cls, request: HttpRequest) -> bool:
        """
        Return True if this instance can handle the given request.

        Default implementation will check Content-Type for supported value
        """
        return getattr(request, "content_type", "").lower() in cls.valid_content_types()

    @abstractmethod
    def process_request(self, request_body: str, context: RpcRequestContext) -> str | tuple[int, str]:
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
    def process_single_request(self, rpc_request: RpcRequest, context: RpcRequestContext) -> GenericRpcResult:
        """
        Perform all mandatory task before executing a single procedure.

        Check request format, retrieve RPCMethod wrapper, call the corresponding function and return the resulting data.
        All errors must be caught internally, concrete implementations must not raise exception from this method.

        :param rpc_request: Request information, as returned by parse_request() method
        :param context: Information needed to execution procedure
        :return: A result instance (Error or Success)
        """
