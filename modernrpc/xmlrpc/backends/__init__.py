from typing import Protocol

from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


class XmlRpcDeserializer(Protocol):
    def __init__(self, **kwargs): ...

    def loads(self, data: str) -> XmlRpcRequest: ...


class XmlRpcSerializer(Protocol):
    def __init__(self, **kwargs): ...

    def dumps(self, result: XmlRpcResult) -> str: ...
