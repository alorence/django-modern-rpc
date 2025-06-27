# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

import base64
import xml.parsers.expat
from collections import OrderedDict
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence

import defusedxml.ElementTree
import xmltodict

from modernrpc.exceptions import RPCInsecureRequest, RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.helpers import ensure_sequence, first
from modernrpc.types import RpcErrorResult
from modernrpc.xmlrpc.backends.constants import MAXINT, MININT
from modernrpc.xmlrpc.handler import XmlRpcRequest

# NoneType is available in types base module only from Python 3.10
try:
    from types import NoneType
except ImportError:
    NoneType = type(None)  # type: ignore[misc]


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

    def dict_to_request(self, data: OrderedDict[str, Any]) -> XmlRpcRequest:
        try:
            method_call = data["methodCall"]
        except KeyError as e:
            raise RPCInvalidRequest("missing methodCall tag", data=data) from e

        try:
            method_name = method_call["methodName"]
        except KeyError as e:
            raise RPCInvalidRequest("missing methodCall.methodName tag", data=data) from e

        params = method_call.get("params") or {}
        param_list: Sequence[dict[str, Any]] = params.get("param", [])

        args: list[Any] = []
        if len(param_list) == 0:
            args = []
        elif len(param_list) == 1:
            param_list = ensure_sequence(param_list)

        for param in param_list:
            _type, v = first(param.items())
            args.append(self.dispatch(_type, v))

        return XmlRpcRequest(method_name=method_name, args=args)

    def dispatch(self, _type: str, value: Any) -> Any:
        try:
            load_func = self.load_funcs[_type]
        except KeyError as e:
            raise RPCInvalidRequest(f"Unsupported type {_type}") from e

        return load_func(value)

    def load_value(self, data: dict) -> Any:
        _type, v = first(data.items())
        return self.dispatch(_type, v)

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

    def load_array(self, data: dict[str, dict[str, list[dict[str, Any]]]]):
        entries = []
        for element in ensure_sequence(data["data"]["value"]):
            _type, value = first(element.items())
            entries.append(self.dispatch(_type, value))
        return entries

    def load_struct(self, data: dict):
        members = ensure_sequence(data["member"])
        res = {}
        for member in members:
            value = member["value"]
            if len(value) > 1:
                raise ValueError
            _type, value = first(value.items())
            res[member["name"]] = self.dispatch(_type, value)
        return res


class Marshaller:
    def __init__(self) -> None:
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

    def result_to_dict(self, result: XmlRpcResult) -> dict[str, Any]:
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

    def dispatch(self, value: Any) -> dict[str, Any]:
        try:
            dump_func = self.dump_funcs[type(value)]
        except KeyError as e:
            raise TypeError(f"Unsupported type: {type(value)}") from e
        return dump_func(value)

    @staticmethod
    def dump_nil(_):
        # FIXME: allow_none config ?
        return {"nil": None}

    @staticmethod
    def dump_bool(value: bool) -> dict[str, Literal[1, 0]]:
        return {"boolean": 1 if value else 0}

    @staticmethod
    def dump_int(value: int) -> dict[str, int]:
        if value > MAXINT or value < MININT:
            raise OverflowError("int value exceeds XML-RPC limits")
        return {"int": value}

    @staticmethod
    def dump_float(value: float) -> dict[str, float]:
        return {"double": value}

    @staticmethod
    def dump_str(value: str) -> dict[str, str]:
        return {"string": value}

    @staticmethod
    def dump_datetime(value: datetime) -> dict[str, str]:
        return {"dateTime.iso8601": value.strftime("%04Y%02m%02dT%H:%M:%S")}

    @staticmethod
    def dump_bytearray(value: bytes | bytearray) -> dict[str, str]:
        return {"base64": base64.b64encode(value).decode()}

    def dump_dict(self, value: dict) -> dict[str, dict[str, list[dict[str, Any]]]]:
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

    def dump_list(self, value: list | tuple) -> dict[str, dict[str, dict[str, list[Any]]]]:
        return {
            "array": {
                "data": {
                    "value": [self.dispatch(val) for val in value],
                }
            },
        }


class XmlToDictBackend:
    """xml-rpc serializer and deserializer based on the third-party xmltodict library"""

    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def marshaller(self):
        return Marshaller()

    @cached_property
    def unmarshaller(self):
        return Unmarshaller()

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            # First parse the XML using defusedxml.ElementTree for security
            # This will raise appropriate exceptions for XML vulnerabilities
            root = defusedxml.ElementTree.fromstring(data)

            # Convert the parsed XML to a string and then parse it with xmltodict
            # This is safe because defusedxml has already validated the XML
            data = defusedxml.ElementTree.tostring(root, encoding="utf-8").decode("utf-8")
        except defusedxml.ElementTree.ParseError as e:
            raise RPCParseError(str(e)) from e
        except defusedxml.DefusedXmlException as e:
            raise RPCInsecureRequest(str(e)) from e

        try:
            structured_data: OrderedDict[str, Any] = xmltodict.parse(data, **self.load_kwargs)
        except xml.parsers.expat.ExpatError as e:
            raise RPCParseError(str(e)) from e

        try:
            return self.unmarshaller.dict_to_request(structured_data)
        except TypeError as e:
            raise RPCInvalidRequest(str(e)) from e

    def dumps(self, result: XmlRpcResult) -> str:
        try:
            structured_data = self.marshaller.result_to_dict(result)
        except Exception as e:
            raise RPCMarshallingError(result.data, e) from e

        return xmltodict.unparse(structured_data, **self.dump_kwargs)
