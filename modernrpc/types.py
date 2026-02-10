from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Optional, Sequence, TypeVar, Union

from django.http import HttpRequest

if TYPE_CHECKING:
    from modernrpc.compat import TypeAlias


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


# Type aliases.
# Each one may be typed with typing.TypeAlias as soon as Python 3.10 will be the minimal requirement
# New syntax `type X = list[str]` will be available from Python 3.12
DictStrAny: TypeAlias = Dict[str, Any]  # Python 3.8 requires use of "Dict" instead of "dict" here
CustomKwargs: TypeAlias = Optional[DictStrAny]

NotSetType = object
AuthPredicate: TypeAlias = Callable[[HttpRequest], Any]
AuthPredicateType: TypeAlias = Union[NotSetType, AuthPredicate, Sequence[AuthPredicate]]

FuncOrCoro: TypeAlias = Callable[..., Any]
