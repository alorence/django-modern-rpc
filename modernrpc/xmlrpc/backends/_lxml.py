from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

import lxml.etree
from lxml.etree import Element, SubElement, _Element

from modernrpc.exceptions import RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.xmlrpc.backends.marshalling import EtreeElementMarshaller, EtreeElementUnmarshaller

if TYPE_CHECKING:
    from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


class LxmlBackend:
    """xml-rpc serializer and deserializer based on the third-party lxml library"""

    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return EtreeElementUnmarshaller[_Element]()

    @cached_property
    def marshaller(self):
        return EtreeElementMarshaller[_Element](Element, SubElement)

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            root_obj: _Element = lxml.etree.fromstring(data)  # noqa: S320 (lxml is NOT vulnerable anymore)
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
