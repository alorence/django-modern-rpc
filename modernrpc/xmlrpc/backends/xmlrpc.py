# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

import xml.parsers.expat
import xmlrpc.client
from xmlrpc.client import Fault, ResponseError

import defusedxml.xmlrpc

from modernrpc.exceptions import RPCInsecureRequest, RPCInvalidRequest, RPCMarshallingError, RPCParseError
from modernrpc.types import CustomKwargs, RpcErrorResult
from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcResult


class PythonXmlRpcDeserializer:
    """xml-rpc deserializer based on python builtin xmlrpc module"""

    def __init__(self, load_kwargs: CustomKwargs = None):
        defusedxml.xmlrpc.monkey_patch()

        self.load_kwargs = load_kwargs or {}
        self.load_kwargs.setdefault("use_datetime", True)
        self.load_kwargs.setdefault("use_builtin_types", True)

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            params, method_name = xmlrpc.client.loads(data, **self.load_kwargs)
        except xml.parsers.expat.ExpatError as exc:
            raise RPCParseError(str(exc)) from exc
        except (ResponseError, TypeError) as exc:
            raise RPCInvalidRequest(str(exc)) from exc
        except defusedxml.DefusedXmlException as exc:
            raise RPCInsecureRequest(str(exc)) from exc

        if not method_name:
            raise RPCInvalidRequest("Unable to find method name", data=data)

        return XmlRpcRequest(method_name.strip(), list(params))


class PythonXmlRpcSerializer:
    """xml-rpc serializer and deserializer based on python builtin xmlrpc module"""

    def __init__(self, dump_kwargs: CustomKwargs = None):
        self.dump_kwargs = dump_kwargs or {}
        self.dump_kwargs.setdefault("allow_none", True)

    def dumps(self, result: XmlRpcResult) -> str:
        result_data = Fault(result.code, result.message) if isinstance(result, RpcErrorResult) else (result.data,)
        try:
            return xmlrpc.client.dumps(result_data, methodresponse=True, **self.dump_kwargs)
        except Exception as exc:
            raise RPCMarshallingError(result.data, exc) from exc
