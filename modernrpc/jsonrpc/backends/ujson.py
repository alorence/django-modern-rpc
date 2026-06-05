from collections.abc import Iterable
from functools import cached_property, partial
from typing import TYPE_CHECKING

import ujson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.module_loading import import_string
from ujson import JSONDecodeError

from modernrpc.exceptions import RPCMarshallingError, RPCParseError
from modernrpc.jsonrpc.handler import JsonRpcRequest, JsonRpcResult
from modernrpc.types import CustomKwargs

if TYPE_CHECKING:
    from modernrpc.types import DictStrAny


class UjsonDeserializer:
    """json-rpc deserializer based on the third-party ujson library"""

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
            structured_data: list[DictStrAny] | DictStrAny = ujson.loads(data, **self.load_kwargs)
        except JSONDecodeError as exc:
            raise RPCParseError(str(exc), data=exc) from exc

        return self.unmarshaller.dict_to_request(structured_data)


class UjsonSerializer:
    """json-rpc serializer based on the third-party ujson library"""

    def __init__(
        self,
        marshaller_klass="modernrpc.jsonrpc.backends.marshalling.Marshaller",
        marshaller_kwargs: CustomKwargs = None,
        dump_kwargs: CustomKwargs = None,
    ):
        self.marshaller_klass = import_string(marshaller_klass)
        self.marshaller_kwargs = marshaller_kwargs or {}

        self.dump_kwargs = dump_kwargs or {}
        # ujson.dumps() does not support the 'cls' argument but accepts a 'default' callable, like simplejson.
        # Build one from DjangoJSONEncoder.default to transparently serialize date, time and datetime objects.
        self.dump_kwargs.setdefault("default", partial(DjangoJSONEncoder.default, DjangoJSONEncoder()))

    @cached_property
    def marshaller(self):
        return self.marshaller_klass(**self.marshaller_kwargs)

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str:
        structured_data = self.marshaller.result_to_dict(result)
        try:
            return ujson.dumps(structured_data, **self.dump_kwargs)
        except (TypeError, UnicodeDecodeError, OverflowError) as exc:
            raise RPCMarshallingError(structured_data, exc) from exc
