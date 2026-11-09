from collections.abc import Iterable
from typing import Any, Protocol

from modernrpc.jsonrpc.handler import JsonRpcBatchItem, JsonRpcRequest, JsonRpcResult


class JsonRpcDeserializer(Protocol):
    def __init__(self, **kwargs: Any): ...

    def loads(self, data: str) -> JsonRpcRequest | list[JsonRpcBatchItem]: ...


class JsonRpcSerializer(Protocol):
    def __init__(self, **kwargs: Any): ...

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str: ...
