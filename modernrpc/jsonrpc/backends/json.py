# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

import json
from functools import cached_property
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Iterable

from modernrpc.exceptions import RPCMarshallingError, RPCParseError
from modernrpc.jsonrpc.backends.marshalling import Marshaller, Unmarshaller

if TYPE_CHECKING:
    from modernrpc.jsonrpc.handler import JsonRpcRequest, JsonRpcResult


class PythonJsonBackend:
    """json-rpc serializer and deserializer based on python builtin json module"""

    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return Unmarshaller()

    @cached_property
    def marshaller(self):
        return Marshaller()

    def loads(self, data: str) -> JsonRpcRequest | list[JsonRpcRequest]:
        try:
            structured_data: list[dict] | dict[str, Any] = json.loads(data, **self.load_kwargs)
        except JSONDecodeError as exc:
            raise RPCParseError(exc.msg, data=exc) from exc

        return self.unmarshaller.dict_to_request(structured_data)

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str:
        structured_data = self.marshaller.result_to_dict(result)
        try:
            return json.dumps(structured_data, **self.dump_kwargs)
        except (TypeError, UnicodeDecodeError) as exc:
            raise RPCMarshallingError(structured_data, exc) from exc
