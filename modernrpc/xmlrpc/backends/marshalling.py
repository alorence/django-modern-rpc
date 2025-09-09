from __future__ import annotations

import base64
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable, Generic, Iterable, Protocol, TypeVar

from modernrpc.exceptions import RPCInvalidRequest
from modernrpc.helpers import first
from modernrpc.types import DictStrAny, RpcErrorResult
from modernrpc.xmlrpc.backends.constants import MAXINT, MININT
from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult

# Self is available in typing base module only from Python 3.11
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

try:
    # types.NoneType is available only with Python 3.10+
    from types import NoneType
except ImportError:
    NoneType = type(None)  # type: ignore[misc]


class ElementTypeProtocol(Protocol, Iterable):
    """
    Base protocol for XML element types. This reflects the API of both the xml.etree and the lxml library.
    Unfortunately, since both libraries share the same interface without inheriting a common base class, we
    have to define our own.
    """

    tag: str
    text: str

    def find(self, path: str, namespaces=None) -> Self | None: ...
    def findall(self, path: str, namespaces=None) -> list[Self]: ...
    def append(self, sub_element: Self) -> None: ...


ElementType = TypeVar("ElementType", bound=ElementTypeProtocol)

LoadFuncType = Callable[[ElementType], Any]
DumpFuncType = Callable[[Any], ElementType]


class EtreeElementUnmarshaller(Generic[ElementType]):
    def __init__(self, allow_none=True) -> None:
        self.allow_none = allow_none

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

    def element_to_request(self, root: ElementType) -> XmlRpcRequest:
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
    def stripped_text(elt: ElementType) -> str:
        return elt.text.strip() if elt.text else ""

    @staticmethod
    def first_child(elt: ElementType) -> ElementType:
        try:
            return first(elt)
        except IndexError as ie:
            raise RPCInvalidRequest("missing child element", data=elt) from ie

    def dispatch(self, elt: ElementType) -> Any:
        try:
            load_func = self.load_funcs[elt.tag]
        except KeyError as exc:
            raise RPCInvalidRequest(f"Unsupported type {elt.tag}") from exc

        return load_func(elt)

    def load_value(self, element: ElementType) -> Any:
        return self.dispatch(self.first_child(element))

    def load_nil(self, _: ElementType) -> None:
        if self.allow_none:
            return
        raise ValueError("cannot marshal None unless allow_none is enabled")

    def load_int(self, elt: ElementType) -> int:
        return int(self.stripped_text(elt))

    def load_bool(self, elt: ElementType) -> bool:
        value = self.stripped_text(elt)
        if value not in ("0", "1"):
            raise TypeError(f"Invalid boolean value: only 0 and 1 are allowed, found {value}")
        return value == "1"

    def load_float(self, elt: ElementType) -> float:
        return float(self.stripped_text(elt))

    def load_str(self, elt: ElementType) -> str:
        return str(self.stripped_text(elt))

    def load_datetime(self, elt: ElementType) -> datetime:
        return datetime.strptime(self.stripped_text(elt), "%Y%m%dT%H:%M:%S")

    def load_base64(self, elt: ElementType) -> bytes:
        return base64.b64decode(self.stripped_text(elt))

    def load_array(self, elt: ElementType) -> list[Any]:
        return [self.dispatch(value_elt) for value_elt in elt.findall("./data/value")]

    def load_struct(self, elt: ElementType) -> DictStrAny:
        member_names_and_values = [self.load_struct_member(member) for member in elt.findall("./member")]
        return dict(member_names_and_values)

    def load_struct_member(self, member_elt: ElementType) -> tuple[str, Any]:
        member_name = member_elt.find("./name")
        if member_name is None:
            raise RPCInvalidRequest("missing member.name tag", data=member_elt)
        value = member_elt.find("./value")
        if value is None:
            raise RPCInvalidRequest("missing member.value tag", data=member_elt)

        return self.stripped_text(member_name), self.dispatch(value)


class EtreeElementMarshaller(Generic[ElementType]):
    def __init__(
        self,
        element_factory: Callable[[str], ElementType],
        sub_element_factory: Callable[[ElementType, str], ElementType],
        allow_none=True,
    ) -> None:
        self.element_factory = element_factory
        self.sub_element_factory = sub_element_factory

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

    def result_to_element(self, result: XmlRpcResult) -> ElementType:
        """Convert an XmlRpcResult to an XML element."""
        root = self.element_factory("methodResponse")

        if isinstance(result, RpcErrorResult):
            fault = self.sub_element_factory(root, "fault")
            value = self.sub_element_factory(fault, "value")

            struct = self.sub_element_factory(value, "struct")

            # Add faultCode member
            member = self.sub_element_factory(struct, "member")
            name = self.sub_element_factory(member, "name")
            name.text = "faultCode"
            value = self.sub_element_factory(member, "value")
            int_el = self.sub_element_factory(value, "int")
            int_el.text = str(result.code)

            # Add faultString member
            member = self.sub_element_factory(struct, "member")
            name = self.sub_element_factory(member, "name")
            name.text = "faultString"
            value = self.sub_element_factory(member, "value")
            string = self.sub_element_factory(value, "string")
            string.text = result.message
        else:
            params = self.sub_element_factory(root, "params")
            param = self.sub_element_factory(params, "param")
            value = self.sub_element_factory(param, "value")

            # Add the result data
            value.append(self.dispatch(result.data))

        return root

    def dispatch(self, value: Any) -> ElementType:
        """Dispatch a value to the appropriate dump method."""
        try:
            dump_func = self.dump_funcs[type(value)]
        except KeyError as exc:
            raise TypeError(f"Unsupported type: {type(value)}") from exc

        return dump_func(value)

    def dump_nil(self, _: None) -> ElementType:
        if self.allow_none:
            return self.element_factory("nil")
        raise ValueError("cannot marshal None unless allow_none is enabled")

    def dump_bool(self, value: bool) -> ElementType:
        boolean = self.element_factory("boolean")
        boolean.text = "1" if value else "0"
        return boolean

    def dump_int(self, value: int) -> ElementType:
        if value > MAXINT or value < MININT:
            raise OverflowError("int value exceeds XML-RPC limits")
        int_el = self.element_factory("int")
        int_el.text = str(value)
        return int_el

    def dump_float(self, value: float) -> ElementType:
        double = self.element_factory("double")
        double.text = str(value)
        return double

    def dump_str(self, value: str) -> ElementType:
        string = self.element_factory("string")
        string.text = value
        return string

    def dump_datetime(self, value: datetime) -> ElementType:
        dt = self.element_factory("dateTime.iso8601")
        dt.text = value.strftime("%04Y%02m%02dT%H:%M:%S")
        return dt

    def dump_bytearray(self, value: bytes | bytearray) -> ElementType:
        b64 = self.element_factory("base64")
        b64.text = base64.b64encode(value).decode()
        return b64

    def dump_dict(self, value: dict) -> ElementType:
        struct = self.element_factory("struct")
        for key, val in value.items():
            member = self.sub_element_factory(struct, "member")
            name = self.sub_element_factory(member, "name")
            name.text = str(key)
            value_el = self.sub_element_factory(member, "value")
            value_el.append(self.dispatch(val))
        return struct

    def dump_list(self, value: list | tuple) -> ElementType:
        array = self.element_factory("array")
        data = self.sub_element_factory(array, "data")
        for val in value:
            value_el = self.sub_element_factory(data, "value")
            value_el.append(self.dispatch(val))
        return array
