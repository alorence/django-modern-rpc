from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


class XmlRpcDeserializer(Protocol):
    def __init__(self, **kwargs): ...

    def loads(self, data: str) -> XmlRpcRequest: ...


class XmlRpcSerializer(Protocol):
    def __init__(self, **kwargs): ...

    def dumps(self, result: XmlRpcResult) -> str: ...
