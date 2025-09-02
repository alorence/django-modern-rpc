from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Sequence, TypeVar, Union


@dataclass
class RpcRequest:
    """Basic information about RPC request"""

    method_name: str
    args: list[Any] | tuple[Any] = field(default_factory=list)


RequestType = TypeVar("RequestType", bound=RpcRequest)


@dataclass
class RpcResult(Generic[RequestType]):
    request: RequestType


@dataclass
class RpcSuccessResult(RpcResult[RequestType]):
    data: Any = None


@dataclass
class RpcErrorResult(RpcResult[RequestType]):
    code: int
    message: str
    # This field is only dumped to JSON-RPC clients!
    data: Any = None


NotSetType = object
AuthPredicate = Callable[[RpcRequest], bool]
AuthPredicateType = Union[NotSetType, AuthPredicate, Sequence[AuthPredicate]]
