# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

import xml.parsers.expat
import xmlrpc.client
from typing import TYPE_CHECKING, Any
from xmlrpc.client import Fault, ResponseError

from modernrpc.exceptions import RPCInternalError, RPCInvalidRequest, RPCParseError
from modernrpc.handlers.base import XmlRpcErrorResult, XmlRpcRequest

if TYPE_CHECKING:
    from modernrpc.handlers.base import XmlRpcResult


class BuiltinXmlRpc:
    def __init__(self, load_kwargs: dict[str, Any] | None = None, dump_kwargs: dict[str, Any] | None = None):
        self.load_kwargs = load_kwargs or {}
        self.load_kwargs.setdefault("use_datetime", True)
        self.load_kwargs.setdefault("use_builtin_types", True)

        self.dump_kwargs = dump_kwargs or {}
        self.dump_kwargs.setdefault("allow_none", True)

    def loads(self, data: str) -> XmlRpcRequest:
        try:
            params, method_name = xmlrpc.client.loads(data, **self.load_kwargs)
        except xml.parsers.expat.ExpatError as e:
            raise RPCParseError(str(e)) from e
        except (ResponseError, TypeError) as e:
            raise RPCInvalidRequest(str(e)) from e

        if not method_name:
            raise RPCInvalidRequest("Unable to find method name", data=data)

        return XmlRpcRequest(method_name.strip(), list(params))

    def dumps(self, result: XmlRpcResult) -> str:
        result_data = Fault(result.code, result.message) if isinstance(result, XmlRpcErrorResult) else (result.data,)
        try:
            return xmlrpc.client.dumps(result_data, methodresponse=True, **self.dump_kwargs)
        except Exception as e:
            raise RPCInternalError(str(e)) from e
