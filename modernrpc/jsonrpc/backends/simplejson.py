# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

from functools import cached_property, partial
from typing import TYPE_CHECKING, Iterable

import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.module_loading import import_string
from simplejson import JSONDecodeError

from modernrpc.exceptions import RPCMarshallingError, RPCParseError

if TYPE_CHECKING:
    from modernrpc.jsonrpc.handler import JsonRpcRequest, JsonRpcResult
    from modernrpc.types import CustomKwargs, DictStrAny


class SimplejsonDeserializer:
    """json-rpc serializer based on the third-party simplejson library"""

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
            structured_data: list[DictStrAny] | DictStrAny = simplejson.loads(data, **self.load_kwargs)
        except JSONDecodeError as exc:
            raise RPCParseError(exc.msg, data=exc) from exc

        return self.unmarshaller.dict_to_request(structured_data)


class SimplejsonSerializer:
    """json-rpc deserializer based on the third-party simplejson library"""

    def __init__(
        self,
        marshaller_klass="modernrpc.jsonrpc.backends.marshalling.Marshaller",
        marshaller_kwargs: CustomKwargs = None,
        dump_kwargs: CustomKwargs = None,
    ):
        self.marshaller_klass = import_string(marshaller_klass)
        self.marshaller_kwargs = marshaller_kwargs or {}

        self.dump_kwargs = dump_kwargs or {}
        # Since DjangoJSONEncoder inherit from json.JSONEncoder, it cannot be used in 'cls' argument
        # We could redefine a custom class inheriting from simplejson.JSONEncoder, but it's not necessary here
        # simplejson.dumps() doc says "NOTE: You should use default instead of subclassing whenever possible"
        # So let's define a custom function based on DjangoJSONEncoder.default using functools.partial
        self.dump_kwargs.setdefault("default", partial(DjangoJSONEncoder.default, DjangoJSONEncoder()))

    @cached_property
    def marshaller(self):
        return self.marshaller_klass(**self.marshaller_kwargs)

    def dumps(self, result: JsonRpcResult | Iterable[JsonRpcResult]) -> str:
        structured_data = self.marshaller.result_to_dict(result)
        try:
            return simplejson.dumps(structured_data, **self.dump_kwargs)
        except (TypeError, UnicodeDecodeError) as exc:
            raise RPCMarshallingError(structured_data, exc) from exc
