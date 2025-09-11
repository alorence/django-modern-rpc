from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import defusedxml
import defusedxml.ElementTree as DefusedElementTree
from django.utils.module_loading import import_string

from modernrpc.exceptions import RPCInsecureRequest, RPCInvalidRequest, RPCMarshallingError, RPCParseError

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from modernrpc.types import CustomKwargs
    from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


ETREE_DEFAULT_ELEMENT_TYPE = "xml.etree.ElementTree.Element"


class EtreeDeserializer:
    """xml-rpc deserializer based on python builtin module xml.etree"""

    def __init__(
        self,
        unmarshaller_klass="modernrpc.xmlrpc.backends.marshalling.EtreeElementUnmarshaller",
        unmarshaller_kwargs: CustomKwargs = None,
        element_type_klass=ETREE_DEFAULT_ELEMENT_TYPE,
        load_kwargs: CustomKwargs = None,
    ):
        self.unmarshaller_klass = import_string(unmarshaller_klass)
        self.unmarshaller_kwargs = unmarshaller_kwargs or {}

        self.element_type_klass = import_string(element_type_klass)

        self.load_kwargs = load_kwargs or {}
        self.load_kwargs.setdefault("forbid_dtd", True)

    @cached_property
    def unmarshaller(self):
        return self.unmarshaller_klass[self.element_type_klass](**self.unmarshaller_kwargs)

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            root_obj: Element = DefusedElementTree.XML(data, **self.load_kwargs)
        except DefusedElementTree.ParseError as exc:
            raise RPCParseError(str(exc)) from exc
        except (defusedxml.DTDForbidden, defusedxml.EntitiesForbidden, defusedxml.ExternalReferenceForbidden) as exc:
            raise RPCInsecureRequest(str(exc)) from exc

        try:
            return self.unmarshaller.element_to_request(root_obj)
        except Exception as exc:
            raise RPCInvalidRequest(str(exc)) from exc


class EtreeSerializer:
    """xml-rpc serializer based on python builtin module xml.etree"""

    def __init__(
        self,
        marshaller_klass="modernrpc.xmlrpc.backends.marshalling.EtreeElementMarshaller",
        marshaller_kwargs: CustomKwargs = None,
        element_type_klass=ETREE_DEFAULT_ELEMENT_TYPE,
        dump_kwargs: CustomKwargs = None,
    ):
        self.marshaller_klass = import_string(marshaller_klass)
        self.marshaller_kwargs = marshaller_kwargs or {}
        self.marshaller_kwargs.setdefault("element_factory", "xml.etree.ElementTree.Element")
        self.marshaller_kwargs.setdefault("sub_element_factory", "xml.etree.ElementTree.SubElement")

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

        return DefusedElementTree.tostring(root, encoding="unicode", **self.dump_kwargs)
