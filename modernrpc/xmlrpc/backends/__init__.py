from typing import Any, Protocol

from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


class XmlRpcDeserializer(Protocol):
    def __init__(self, **kwargs: Any): ...

    def loads(self, data: str) -> XmlRpcRequest: ...


class XmlRpcSerializer(Protocol):
    def __init__(self, **kwargs: Any): ...

    def dumps(self, result: XmlRpcResult) -> str: ...
