from __future__ import annotations

import base64
from collections import OrderedDict
from datetime import datetime
from functools import cached_property
from types import NoneType
from typing import TYPE_CHECKING, Any, Callable

import lxml.etree

from modernrpc.exceptions import RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.helpers import first
from modernrpc.typing import RpcErrorResult
from modernrpc.xmlrpc.backends.constants import MAXINT, MININT
from modernrpc.xmlrpc.handler import XmlRpcRequest

if TYPE_CHECKING:
    from lxml.etree import _Element

    from modernrpc.xmlrpc.handler import XmlRpcResult


class Unmarshaller:
    def __init__(self) -> None:
        self.load_funcs: dict[str, Callable] = {
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

    def element_to_request(self, root: _Element) -> XmlRpcRequest:
        if root.tag != "methodCall":
            raise RPCInvalidRequest("missing methodCall tag", data=root)

        method_name = root.find("./methodName")
        if method_name is None:
            raise RPCInvalidRequest("missing methodCall.methodName tag", data=root)

        params = root.find("./params")
        if params is None:
            return XmlRpcRequest(method_name=self.stripped_text(method_name))

        param_list = params.findall("./param")

        args = [self.dispatch(self.first_child(param)) for param in param_list]
        return XmlRpcRequest(method_name=self.stripped_text(method_name), args=args)

    @staticmethod
    def stripped_text(elt: _Element) -> str:
        return elt.text.strip() if elt.text else ""

    @staticmethod
    def first_child(elt: _Element) -> _Element:
        try:
            return first(elt)
        except IndexError as ie:
            raise RPCInvalidRequest("missing child element", data=elt) from ie

    def dispatch(self, elt: _Element) -> Any:
        try:
            load_func = self.load_funcs[elt.tag]
        except KeyError as e:
            raise RPCInvalidRequest(f"Unsupported type {elt.tag}") from e

        return load_func(elt)

    def load_value(self, element: _Element) -> Any:
        return self.dispatch(self.first_child(element))

    @staticmethod
    def load_nil(_: _Element) -> Any:
        return None

    def load_int(self, elt: _Element) -> Any:
        return int(self.stripped_text(elt))

    def load_bool(self, elt: _Element) -> Any:
        value = self.stripped_text(elt)
        if value not in ("0", "1"):
            raise TypeError(f"Invalid boolean value: only 0 and 1 are allowed, found {value}")
        return value == "1"

    def load_float(self, elt: _Element) -> float:
        return float(self.stripped_text(elt))

    def load_str(self, elt: _Element) -> str:
        return str(self.stripped_text(elt))

    def load_datetime(self, elt: _Element) -> datetime:
        return datetime.strptime(self.stripped_text(elt), "%Y%m%dT%H:%M:%S")

    def load_base64(self, elt: _Element) -> bytes:
        return base64.b64decode(self.stripped_text(elt))

    def load_array(self, elt: _Element) -> list[Any]:
        return [self.dispatch(value_elt) for value_elt in elt.findall("./data/value")]

    def load_struct(self, elt: _Element):
        member_names_and_values = [self.load_struct_member(member) for member in elt.findall("./member")]
        return dict(member_names_and_values)

    def load_struct_member(self, member_elt: _Element):
        member_name = member_elt.find("./name")
        if member_name is None:
            raise RPCInvalidRequest("missing member.name tag", data=member_elt)
        value = member_elt.find("./value")
        if value is None:
            raise RPCInvalidRequest("missing member.value tag", data=member_elt)

        return self.stripped_text(member_name), self.dispatch(value)


class Marshaller:
    def __init__(self):
        self.dump_funcs = {
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

    def result_to_element(self, result: XmlRpcResult) -> _Element:
        """Convert an XmlRpcResult to an XML element."""
        root = lxml.etree.Element("methodResponse")

        if isinstance(result, RpcErrorResult):
            fault = lxml.etree.SubElement(root, "fault")
            value = lxml.etree.SubElement(fault, "value")

            struct = lxml.etree.SubElement(value, "struct")

            # Add faultCode member
            member = lxml.etree.SubElement(struct, "member")
            name = lxml.etree.SubElement(member, "name")
            name.text = "faultCode"
            value = lxml.etree.SubElement(member, "value")
            int_el = lxml.etree.SubElement(value, "int")
            int_el.text = str(result.code)

            # Add faultString member
            member = lxml.etree.SubElement(struct, "member")
            name = lxml.etree.SubElement(member, "name")
            name.text = "faultString"
            value = lxml.etree.SubElement(member, "value")
            string = lxml.etree.SubElement(value, "string")
            string.text = result.message
        else:
            params = lxml.etree.SubElement(root, "params")
            param = lxml.etree.SubElement(params, "param")
            value = lxml.etree.SubElement(param, "value")

            # Add the result data
            value.append(self.dispatch(result.data))

        return root

    def dispatch(self, value: Any) -> _Element:
        """Dispatch a value to the appropriate dump method."""
        try:
            dump_func = self.dump_funcs[type(value)]
        except KeyError as e:
            raise TypeError(f"Unsupported type: {type(value)}") from e

        return dump_func(value)

    @staticmethod
    def dump_nil(_: None) -> _Element:
        return lxml.etree.Element("nil")

    @staticmethod
    def dump_bool(value: bool) -> _Element:
        boolean = lxml.etree.Element("boolean")
        boolean.text = "1" if value else "0"
        return boolean

    @staticmethod
    def dump_int(value: int) -> _Element:
        if value > MAXINT or value < MININT:
            raise OverflowError("int value exceeds XML-RPC limits")
        int_el = lxml.etree.Element("int")
        int_el.text = str(value)
        return int_el

    @staticmethod
    def dump_float(value: float) -> _Element:
        double = lxml.etree.Element("double")
        double.text = str(value)
        return double

    @staticmethod
    def dump_str(value: str) -> _Element:
        string = lxml.etree.Element("string")
        string.text = value
        return string

    @staticmethod
    def dump_datetime(value: datetime) -> _Element:
        dt = lxml.etree.Element("dateTime.iso8601")
        dt.text = value.strftime("%04Y%02m%02dT%H:%M:%S")
        return dt

    @staticmethod
    def dump_bytearray(value: bytes | bytearray) -> _Element:
        b64 = lxml.etree.Element("base64")
        b64.text = base64.b64encode(value).decode()
        return b64

    def dump_dict(self, value: dict) -> _Element:
        struct = lxml.etree.Element("struct")
        for key, val in value.items():
            member = lxml.etree.SubElement(struct, "member")
            name = lxml.etree.SubElement(member, "name")
            name.text = str(key)
            value_el = lxml.etree.SubElement(member, "value")
            value_el.append(self.dispatch(val))
        return struct

    def dump_list(self, value: list | tuple) -> _Element:
        array = lxml.etree.Element("array")
        data = lxml.etree.SubElement(array, "data")
        for val in value:
            value_el = lxml.etree.SubElement(data, "value")
            value_el.append(self.dispatch(val))
        return array


class LxmlBackend:
    """xml-rpc serializer and deserializer based on lxml"""

    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return Unmarshaller()

    @cached_property
    def marshaller(self):
        return Marshaller()

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            root_obj: _Element = lxml.etree.fromstring(data)  # noqa: S320 - Deprecated Ruff rule
        except lxml.etree.XMLSyntaxError as e:
            raise RPCParseError(str(e)) from e

        try:
            return self.unmarshaller.element_to_request(root_obj)
        except Exception as e:
            raise RPCInvalidRequest(str(e)) from e

    def dumps(self, result: XmlRpcResult) -> str:
        """Serialize an XmlRpcResult to an XML string."""
        try:
            root = self.marshaller.result_to_element(result)
        except Exception as e:
            raise RPCMarshallingError(result.data, e) from e

        return lxml.etree.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
