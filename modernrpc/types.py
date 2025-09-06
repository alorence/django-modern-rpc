from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, Optional, Sequence, TypeVar, Union


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


# Type aliases.
# Each one may be typed with typing.TypeAlias as soon as Python 3.10 will be the minimal requirement
# New syntax `type X = list[str]` will be available from Python 3.12
DictStrAny = Dict[str, Any]  # Not sure why, but using dict instead of typing.Dict here will cause Python 3.8 to crash
CustomKwargs = Optional[DictStrAny]

NotSetType = object
AuthPredicate = Callable[[RpcRequest], bool]
AuthPredicateType = Union[NotSetType, AuthPredicate, Sequence[AuthPredicate]]
