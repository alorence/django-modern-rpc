from collections.abc import Iterable
from typing import Protocol

from modernrpc.jsonrpc.handler import JsonRpcRequest, JsonRpcResult


class JsonRpcDeserializer(Protocol):
    def __init__(self, **kwargs): ...

    def loads(self, data: str) -> JsonRpcRequest | list[JsonRpcRequest]: ...


class JsonRpcSerializer(Protocol):
    def __init__(self, **kwargs): ...

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str: ...
