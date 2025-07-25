# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

import warnings
from functools import cached_property
from typing import TYPE_CHECKING, Any, Iterable

import orjson
from orjson import JSONDecodeError, JSONEncodeError

from modernrpc.exceptions import RPCMarshallingError, RPCParseError
from modernrpc.jsonrpc.backends.marshalling import Marshaller, Unmarshaller

if TYPE_CHECKING:
    from modernrpc.jsonrpc.handler import JsonRpcRequest, JsonRpcResult


class OrjsonBackend:
    """json-rpc serializer and deserializer based on the third-party orjson library"""

    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        if load_kwargs:
            warnings.warn(
                message="OrJSON backend does not support 'load_kwargs' argument, it will be ignored.",
                category=UserWarning,
                stacklevel=3,
            )

        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return Unmarshaller()

    @cached_property
    def marshaller(self):
        return Marshaller()

    def loads(self, data: str) -> JsonRpcRequest | list[JsonRpcRequest]:
        try:
            structured_data: list[dict] | dict[str, Any] = orjson.loads(data)
        except JSONDecodeError as exc:
            raise RPCParseError(exc.msg, data=exc) from exc

        return self.unmarshaller.dict_to_request(structured_data)

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str:
        structured_data = self.marshaller.result_to_dict(result)
        try:
            return orjson.dumps(structured_data, **self.dump_kwargs).decode("utf-8")
        except (JSONEncodeError, TypeError, UnicodeDecodeError) as exc:
            raise RPCMarshallingError(structured_data, exc) from exc
