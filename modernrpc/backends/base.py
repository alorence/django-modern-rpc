# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Iterable

    from modernrpc.handlers.jsonhandler import JsonRpcRequest, JsonRpcResult
    from modernrpc.handlers.xmlhandler import XmlRpcRequest, XmlRpcResult


class XmlRpcDeserializer(Protocol):
    def loads(self, data: str) -> XmlRpcRequest: ...


class XmlRpcSerializer(Protocol):
    def dumps(self, result: XmlRpcResult) -> str: ...


class JsonRpcDeserializer(Protocol):
    def loads(self, data: str) -> JsonRpcRequest | list[JsonRpcRequest]: ...


class JsonRpcSerializer(Protocol):
    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str: ...
