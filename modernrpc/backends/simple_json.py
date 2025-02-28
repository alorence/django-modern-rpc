# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

import simplejson
from simplejson import JSONDecodeError

from modernrpc.backends.base_json import Marshaller, Unmarshaller
from modernrpc.exceptions import RPCMarshallingError, RPCParseError

if TYPE_CHECKING:
    from modernrpc.handlers.jsonhandler import JsonRpcRequest, JsonRpcResult


class SimpleJSON:
    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    def loads(self, data: str) -> JsonRpcRequest | list[JsonRpcRequest]:
        try:
            structured_data: list[dict] | dict[str, Any] = simplejson.loads(data, **self.load_kwargs)
        except JSONDecodeError as e:
            raise RPCParseError(e.msg, data=e) from e

        return Unmarshaller().dict_to_request(structured_data)

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str:
        structured_data = Marshaller().result_to_dict(result)
        try:
            return simplejson.dumps(structured_data, **self.dump_kwargs)
        except (TypeError, UnicodeDecodeError) as e:
            raise RPCMarshallingError(structured_data, e) from e
