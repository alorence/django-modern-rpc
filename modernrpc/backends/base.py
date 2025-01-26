# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Protocol

if TYPE_CHECKING:
    from modernrpc.handlers.base import JsonRpcRequest, JsonRpcResult, XmlRpcRequest, XmlRpcResult


class XmlRpcDeserializer(Protocol):
    def loads(self, data: str) -> XmlRpcRequest: ...


class XmlRpcSerializer(Protocol):
    def dumps(self, result: XmlRpcResult) -> str: ...


class JsonRpcDeserializer(Protocol):
    def loads(self, data: str) -> JsonRpcRequest | Iterable[JsonRpcRequest]: ...


class JsonRpcSerializer(Protocol):
    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str: ...
