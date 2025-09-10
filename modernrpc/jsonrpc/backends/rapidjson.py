# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Iterable

import rapidjson
from django.utils.module_loading import import_string
from rapidjson import JSONDecodeError

from modernrpc.exceptions import RPCMarshallingError, RPCParseError

if TYPE_CHECKING:
    from modernrpc.jsonrpc.handler import JsonRpcRequest, JsonRpcResult
    from modernrpc.types import CustomKwargs, DictStrAny


class RapidjsonDeserializer:
    """json-rpc deserializer based on the third-party simplejson library"""

    def __init__(
        self,
        unmarshaller_klass="modernrpc.jsonrpc.backends.marshalling.Unmarshaller",
        unmarshaller_kwargs: CustomKwargs = None,
        load_kwargs: CustomKwargs = None,
    ):
        self.unmarshaller_klass = import_string(unmarshaller_klass)
        self.unmarshaller_kwargs = unmarshaller_kwargs or {}

        self.load_kwargs = load_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return self.unmarshaller_klass(**self.unmarshaller_kwargs)

    def loads(self, data: str) -> JsonRpcRequest | list[JsonRpcRequest]:
        try:
            structured_data: list[DictStrAny] | DictStrAny = rapidjson.loads(data, **self.load_kwargs)
        except JSONDecodeError as exc:
            raise RPCParseError(str(exc), data=exc) from exc

        return self.unmarshaller.dict_to_request(structured_data)


class RapidjsonSerializer:
    """json-rpc serializer based on the third-party simplejson library"""

    def __init__(
        self,
        marshaller_klass="modernrpc.jsonrpc.backends.marshalling.Marshaller",
        marshaller_kwargs: CustomKwargs = None,
        dump_kwargs: CustomKwargs = None,
    ):
        self.marshaller_klass = import_string(marshaller_klass)
        self.marshaller_kwargs = marshaller_kwargs or {}

        self.dump_kwargs = dump_kwargs or {}
        self.dump_kwargs.setdefault("datetime_mode", rapidjson.DM_ISO8601)

    @cached_property
    def marshaller(self):
        return self.marshaller_klass(**self.marshaller_kwargs)

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str:
        structured_data = self.marshaller.result_to_dict(result)
        try:
            return rapidjson.dumps(structured_data, **self.dump_kwargs)
        except (TypeError, UnicodeDecodeError) as exc:
            raise RPCMarshallingError(structured_data, exc) from exc
