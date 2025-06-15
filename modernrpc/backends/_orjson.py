from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Iterable

import orjson
from orjson import JSONDecodeError, JSONEncodeError

from modernrpc.backends.base_json import Marshaller, Unmarshaller
from modernrpc.exceptions import RPCMarshallingError, RPCParseError

if TYPE_CHECKING:
    from modernrpc.handlers.jsonhandler import JsonRpcRequest, JsonRpcResult


class OrJSON:
    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        if load_kwargs:
            warnings.warn(
                message="OrJSON backend does not support 'load_kwargs' argument, it will be ignored.",
                category=UserWarning,
                stacklevel=3,
            )

        self.dump_kwargs = dump_kwargs or {}

    @staticmethod
    def loads(data: str) -> JsonRpcRequest | list[JsonRpcRequest]:
        try:
            structured_data: list[dict] | dict[str, Any] = orjson.loads(data)
        except JSONDecodeError as e:
            raise RPCParseError(e.msg, data=e) from e

        return Unmarshaller().dict_to_request(structured_data)

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str:
        structured_data = Marshaller().result_to_dict(result)
        try:
            return orjson.dumps(structured_data, **self.dump_kwargs).decode("utf-8")
        except (JSONEncodeError, TypeError, UnicodeDecodeError) as e:
            raise RPCMarshallingError(structured_data, e) from e
