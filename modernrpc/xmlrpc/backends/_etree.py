from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, SubElement

import defusedxml
import defusedxml.ElementTree as DefusedElementTree

from modernrpc.exceptions import RPCInsecureRequest, RPCInvalidRequest, RPCMarshallingError, RPCParseError
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
            root_obj: Element = DefusedElementTree.XML(data)
        except DefusedElementTree.ParseError as exc:
            raise RPCParseError(str(exc)) from exc
        except (defusedxml.DTDForbidden, defusedxml.EntitiesForbidden, defusedxml.ExternalReferenceForbidden) as exc:
            raise RPCInsecureRequest(str(exc)) from exc

        try:
            return self.unmarshaller.element_to_request(root_obj)
        except Exception as exc:
            raise RPCInvalidRequest(str(exc)) from exc

    def dumps(self, result: XmlRpcResult) -> str:
        """Serialize an XmlRpcResult to an XML string."""
        try:
            root = self.marshaller.result_to_element(result)
        except Exception as exc:
            raise RPCMarshallingError(result.data, exc) from exc

        return DefusedElementTree.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
