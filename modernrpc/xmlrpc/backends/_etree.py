from __future__ import annotations

import xml.etree.ElementTree as ET
from functools import cached_property
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, SubElement

from modernrpc.exceptions import RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.xmlrpc.backends.marshalling import EtreeElementMarshaller, EtreeElementUnmarshaller

if TYPE_CHECKING:
    from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


class EtreeBackend:
    """xml-rpc serializer and deserializer based on python builtin module xml.etree"""

    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return EtreeElementUnmarshaller[Element]()

    @cached_property
    def marshaller(self):
        return EtreeElementMarshaller[Element](Element, SubElement)

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            root_obj: Element = ET.XML(data)
        except ET.ParseError as e:
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

        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
