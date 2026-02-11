from __future__ import annotations

import base64
import xml.parsers.expat
from collections import OrderedDict
from collections.abc import Callable
from datetime import datetime
from functools import cached_property
from io import StringIO
from types import NoneType
from typing import TYPE_CHECKING, Any, Literal

import defusedxml.ElementTree
import xmltodict
from django.utils.module_loading import import_string

from modernrpc.exceptions import RPCInsecureRequest, RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.helpers import first
from modernrpc.types import CustomKwargs, DictStrAny, RpcErrorResult
from modernrpc.xmlrpc.backends.constants import MAXINT, MININT
from modernrpc.xmlrpc.handler import XmlRpcRequest

if TYPE_CHECKING:
    from modernrpc.xmlrpc.handler import XmlRpcResult


LoadFuncType = Callable[[Any], Any]
DumpFuncType = Callable[[Any], dict]


class Unmarshaller:
    def __init__(self) -> None:
        self.load_funcs: dict[str, LoadFuncType] = {
            "value": self.load_value,
            "nil": self.load_nil,
            "boolean": self.load_bool,
            "int": self.load_int,
            "i4": self.load_int,
            "double": self.load_float,
            "string": self.load_str,
            "dateTime.iso8601": self.load_datetime,
            "base64": self.load_base64,
            "array": self.load_array,
            "struct": self.load_struct,
        }

    @classmethod
    def do_force_list(cls, path, key, value):
        """Indicate to xmltodict parser when a specific tag MUST return a list even for a single element"""
        if path:
            # <param> is expected only as child of <params>
            # <member> is expected as child of <struct>
            # These tags does not appear elsewhere
            if key in ("param", "member"):
                return True

            upper_tag, _ = path[-1]
            # <value> tag may appear in various places.
            # Consider it as a list of values only when direct child of <array> or <data> (struct)
            if key == "value" and upper_tag in ("array", "data"):
                return True

        return False

    def dict_to_request(self, data: DictStrAny) -> XmlRpcRequest:
        try:
            method_call = data["methodCall"]
        except KeyError as exc:
            raise RPCInvalidRequest("missing methodCall tag", data=data) from exc

        try:
            method_name = method_call["methodName"]
        except KeyError as exc:
            raise RPCInvalidRequest("missing methodCall.methodName tag", data=data) from exc

        # We don't use method_call.get("params", default={}) here because if <params> tag is present but empty,
        # the default won't be used and the function will actually return None
        params_root = method_call.get("params") or {}
        params = params_root.get("param", [])

        args: list[Any] = []
        for param in params:
            _type, v = first(param.items())
            args.append(self.dispatch(_type, v))

        return XmlRpcRequest(method_name=method_name, args=args)

    def dispatch(self, _type: str, value: Any) -> Any:
        try:
            load_func = self.load_funcs[_type]
        except KeyError as exc:
            raise RPCInvalidRequest(f"Unsupported type {_type}") from exc

        return load_func(value)

    def load_value(self, data: dict) -> Any:
        _type, value = first(data.items())
        return self.dispatch(_type, value)

    @staticmethod
    def load_nil(_) -> None:
        return None

    @staticmethod
    def load_int(data: str) -> int:
        return int(data)

    @staticmethod
    def load_bool(data: str) -> bool:
        if data not in ("0", "1"):
            raise TypeError("Invalid boolean value: only 0 and 1 are allowed")
        return data == "1"

    @staticmethod
    def load_float(data: str) -> float:
        return float(data)

    @staticmethod
    def load_str(data: str) -> str:
        return str(data)

    @staticmethod
    def load_datetime(data: str) -> datetime:
        return datetime.strptime(data, "%Y%m%dT%H:%M:%S")

    @staticmethod
    def load_base64(data: str) -> bytes:
        return base64.b64decode(data)

    def load_array(self, data: dict[str, dict[str, list[DictStrAny]]]):
        values = []
        for element in data["data"].get("value", []):
            _type, value = first(element.items())
            values.append(self.dispatch(_type, value))
        return values

    def load_struct(self, data: dict):
        res = {}
        for member in data["member"]:
            value = member["value"]
            if len(value) > 1:
                raise ValueError
            _type, value = first(value.items())
            res[member["name"]] = self.dispatch(_type, value)
        return res


class Marshaller:
    def __init__(self, allow_none=True) -> None:
        self.allow_none = allow_none

        self.dump_funcs: dict[type, DumpFuncType] = {
            NoneType: self.dump_nil,
            bool: self.dump_bool,
            int: self.dump_int,
            float: self.dump_float,
            str: self.dump_str,
            bytes: self.dump_bytearray,
            bytearray: self.dump_bytearray,
            datetime: self.dump_datetime,
            list: self.dump_list,
            tuple: self.dump_list,
            dict: self.dump_dict,
            OrderedDict: self.dump_dict,
        }

    def result_to_dict(self, result: XmlRpcResult) -> DictStrAny:
        if isinstance(result, RpcErrorResult):
            return {
                "methodResponse": {
                    "fault": {
                        "value": self.dispatch(
                            {
                                "faultCode": result.code,
                                "faultString": result.message,
                            }
                        ),
                    }
                }
            }

        return {
            "methodResponse": {
                "params": [
                    {"param": {"value": self.dispatch(result.data)}},
                ]
            }
        }

    def dispatch(self, value: Any) -> DictStrAny:
        try:
            dump_func = self.dump_funcs[type(value)]
        except KeyError as e:
            raise TypeError(f"Unsupported type: {type(value)}") from e
        return dump_func(value)

    def dump_nil(self, _) -> dict[Literal["nil"], None]:
        if self.allow_none:
            return {"nil": None}
        raise ValueError("cannot marshal None unless allow_none is enabled")

    @staticmethod
    def dump_bool(value: bool) -> dict[str, Literal[1, 0]]:
        return {"boolean": 1 if value else 0}

    @staticmethod
    def dump_int(value: int) -> dict[Literal["int"], int]:
        if value > MAXINT or value < MININT:
            raise OverflowError("int value exceeds XML-RPC limits")
        return {"int": value}

    @staticmethod
    def dump_float(value: float) -> dict[Literal["double"], float]:
        return {"double": value}

    @staticmethod
    def dump_str(value: str) -> dict[Literal["string"], str]:
        return {"string": value}

    @staticmethod
    def dump_datetime(value: datetime) -> dict[Literal["dateTime.iso8601"], str]:
        return {"dateTime.iso8601": value.strftime("%04Y%02m%02dT%H:%M:%S")}

    @staticmethod
    def dump_bytearray(value: bytes | bytearray) -> dict[Literal["base64"], str]:
        return {"base64": base64.b64encode(value).decode()}

    def dump_dict(self, value: dict) -> dict[Literal["struct"], dict[Literal["member"], list[DictStrAny]]]:
        return {
            "struct": {
                "member": [
                    {
                        "name": key,
                        "value": self.dispatch(val),
                    }
                    for key, val in value.items()
                ],
            },
        }

    def dump_list(
        self, value: list | tuple
    ) -> dict[Literal["array"], dict[Literal["data"], dict[Literal["value"], list[Any]]]]:
        return {
            "array": {
                "data": {
                    "value": [self.dispatch(val) for val in value],
                }
            },
        }


class XmlToDictDeserializer:
    """xml-rpc deserializer based on the third-party xmltodict library"""

    def __init__(
        self,
        unmarshaller_klass="modernrpc.xmlrpc.backends.xmltodict.Unmarshaller",
        unmarshaller_kwargs: CustomKwargs = None,
        load_kwargs: CustomKwargs = None,
    ):
        self.unmarshaller_klass = import_string(unmarshaller_klass)
        self.unmarshaller_kwargs = unmarshaller_kwargs or {}
        self.load_kwargs = load_kwargs or {}
        self.load_kwargs["force_list"] = Unmarshaller.do_force_list

    @cached_property
    def unmarshaller(self):
        return self.unmarshaller_klass(**self.unmarshaller_kwargs)

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            # First, parse the XML using defusedxml.ElementTree for security
            # This will raise appropriate exceptions for XML vulnerabilities
            root = defusedxml.ElementTree.fromstring(data)

            # Convert the parsed XML to a string and then parse it with xmltodict
            # This is safe because defusedxml has already validated the XML
            data = defusedxml.ElementTree.tostring(root, encoding="utf-8").decode("utf-8")
        except defusedxml.ElementTree.ParseError as exc:
            raise RPCParseError(str(exc)) from exc
        except defusedxml.DefusedXmlException as exc:
            raise RPCInsecureRequest(str(exc)) from exc

        try:
            structured_data: DictStrAny = xmltodict.parse(data, **self.load_kwargs)
        except xml.parsers.expat.ExpatError as exc:
            raise RPCParseError(str(exc)) from exc

        try:
            return self.unmarshaller.dict_to_request(structured_data)
        except TypeError as exc:
            raise RPCInvalidRequest(str(exc)) from exc


class XmlToDictSerializer:
    """xml-rpc serializer based on the third-party xmltodict library"""

    def __init__(
        self,
        marshaller_klass="modernrpc.xmlrpc.backends.xmltodict.Marshaller",
        marshaller_kwargs: CustomKwargs = None,
        dump_kwargs: CustomKwargs = None,
    ):
        self.marshaller_klass = import_string(marshaller_klass)
        self.marshaller_kwargs = marshaller_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def marshaller(self):
        return self.marshaller_klass(**self.marshaller_kwargs)

    def dumps(self, result: XmlRpcResult) -> str:
        try:
            structured_data = self.marshaller.result_to_dict(result)
        except Exception as e:
            raise RPCMarshallingError(result.data, e) from e

        output_stream = StringIO()
        xmltodict.unparse(structured_data, output=output_stream, **self.dump_kwargs)
        return output_stream.getvalue()
