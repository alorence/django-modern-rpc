from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, TypeAlias, TypeVar

from django.http import HttpRequest


@dataclass
class RpcRequest:
    """Basic information about RPC request"""

    method_name: str
    args: list[Any] | tuple[Any, ...] = field(default_factory=list)


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


# Type aliases. New syntax `type X = list[str]` will be available from Python 3.12
DictStrAny: TypeAlias = dict[str, Any]
CustomKwargs: TypeAlias = DictStrAny | None

NotSetType = object
AuthPredicate: TypeAlias = Callable[[HttpRequest], Any]
AuthPredicateType: TypeAlias = NotSetType | AuthPredicate | Sequence[AuthPredicate]

FuncOrCoro: TypeAlias = Callable[..., Any]
