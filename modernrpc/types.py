from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, TypeAlias, TypeVar

from django.http import HttpRequest

from modernrpc.constants import Default


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

AuthPredicate: TypeAlias = Callable[[HttpRequest], Any]
AuthPredicateType: TypeAlias = Literal[Default.NOT_SET] | AuthPredicate | Sequence[AuthPredicate] | None

FuncOrCoro: TypeAlias = Callable[..., Any] | Callable[..., Awaitable[Any]]
