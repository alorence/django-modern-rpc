from __future__ import annotations

import base64
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable

import lxml.etree

from modernrpc.exceptions import RPCInvalidRequest, RPCParseError
from modernrpc.helpers import first
from modernrpc.xmlrpc.handler import XmlRpcRequest

if TYPE_CHECKING:
    from lxml.etree import _Element


class Unmarshaller:
    def __init__(self) -> None:
        self.__dispatch: dict[str, Callable] = {
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
            load_func = self.__dispatch[elt.tag]
            return load_func(elt)

        except KeyError as e:
            raise RPCInvalidRequest(f"Unsupported type {elt.tag}") from e

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


class LxmlBackend:
    """xml-rpc serializer and deserializer based on the third-party xmltodict library"""

    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return Unmarshaller()

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            root_obj: _Element = lxml.etree.fromstring(data)  # noqa: S320 - Deprecated Ruff rule
        except lxml.etree.XMLSyntaxError as e:
            raise RPCParseError(str(e)) from e

        try:
            return self.unmarshaller.element_to_request(root_obj)
        except Exception as e:
            raise RPCInvalidRequest(str(e)) from e
