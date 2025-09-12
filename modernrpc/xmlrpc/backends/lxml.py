from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import lxml.etree
from django.utils.module_loading import import_string

from modernrpc.exceptions import RPCInvalidRequest, RPCMarshallingError, RPCParseError

if TYPE_CHECKING:
    from lxml.etree import _Element

    from modernrpc.types import CustomKwargs
    from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


LXML_DEFAULT_ELEMENT_TYPE = "lxml.etree._Element"


class LxmlDeserializer:
    """xml-rpc deserializer based on the third-party lxml library"""

    def __init__(
        self,
        unmarshaller_klass="modernrpc.xmlrpc.backends.marshalling.EtreeElementUnmarshaller",
        unmarshaller_kwargs: CustomKwargs = None,
        element_type_klass=LXML_DEFAULT_ELEMENT_TYPE,
        load_parser_kwargs: CustomKwargs = None,
        load_kwargs: CustomKwargs = None,
    ):
        self.unmarshaller_klass = import_string(unmarshaller_klass)
        self.unmarshaller_kwargs = unmarshaller_kwargs or {}

        self.element_type_klass = import_string(element_type_klass)

        self.load_parser_kwargs = load_parser_kwargs or {}
        self.load_parser_kwargs.setdefault("resolve_entities", False)  # Prevent entity expansion
        self.load_parser_kwargs.setdefault("no_network", True)  # Prevent network access
        self.load_parser_kwargs.setdefault("dtd_validation", False)  # Disable DTD validation
        self.load_parser_kwargs.setdefault("load_dtd", False)  # Disable DTD loading
        self.load_parser_kwargs.setdefault("huge_tree", False)  # Prevent the billion-laugh attack

        self.load_kwargs = load_kwargs or {}

    @cached_property
    def unmarshaller(self):
        return self.unmarshaller_klass[self.element_type_klass](**self.unmarshaller_kwargs)

    def loads(self, data: str) -> XmlRpcRequest:
        if "parser" not in self.load_kwargs:
            # Create a custom parser, with default secure params, configurable from settings
            parser = lxml.etree.XMLParser(**self.load_parser_kwargs)
            self.load_kwargs["parser"] = parser

        try:
            root_obj: _Element = lxml.etree.fromstring(data, **self.load_kwargs)
        except lxml.etree.XMLSyntaxError as exc:
            raise RPCParseError(str(exc)) from exc

        try:
            return self.unmarshaller.element_to_request(root_obj)
        except Exception as exc:
            raise RPCInvalidRequest(str(exc)) from exc


class LxmlSerializer:
    """xml-rpc serializer based on the third-party lxml library"""

    def __init__(
        self,
        marshaller_klass="modernrpc.xmlrpc.backends.marshalling.EtreeElementMarshaller",
        marshaller_kwargs: CustomKwargs = None,
        element_type_klass=LXML_DEFAULT_ELEMENT_TYPE,
        dump_kwargs: CustomKwargs = None,
    ):
        self.marshaller_klass = import_string(marshaller_klass)
        self.marshaller_kwargs = marshaller_kwargs or {}
        self.marshaller_kwargs.setdefault("element_factory", "lxml.etree.Element")
        self.marshaller_kwargs.setdefault("sub_element_factory", "lxml.etree.SubElement")

        self.element_type_klass = import_string(element_type_klass)

        self.dump_kwargs = dump_kwargs or {}

    @cached_property
    def marshaller(self):
        elt_factory = import_string(self.marshaller_kwargs.pop("element_factory"))
        sub_elt_factory = import_string(self.marshaller_kwargs.pop("sub_element_factory"))
        return self.marshaller_klass[self.element_type_klass](elt_factory, sub_elt_factory, **self.marshaller_kwargs)

    def dumps(self, result: XmlRpcResult) -> str:
        """Serialize an XmlRpcResult to an XML string."""
        try:
            root = self.marshaller.result_to_element(result)
        except Exception as exc:
            raise RPCMarshallingError(result.data, exc) from exc

        return lxml.etree.tostring(root, encoding="unicode", **self.dump_kwargs)
