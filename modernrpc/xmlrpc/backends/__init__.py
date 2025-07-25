# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
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
