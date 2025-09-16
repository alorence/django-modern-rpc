# PEP 585: use of list[Any] instead of List[Any] is available since Python 3.9, enable it for older versions
# PEP 604: use of typeA | typeB is available since Python 3.10, enable it for older versions
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from django.utils.module_loading import import_string

from modernrpc import Protocol
from modernrpc.config import settings
from modernrpc.exceptions import RPCException
from modernrpc.handler import RpcHandler
from modernrpc.types import DictStrAny, RpcErrorResult, RpcRequest, RpcSuccessResult

if TYPE_CHECKING:
    from typing import ClassVar

    from modernrpc import RpcRequestContext
    from modernrpc.xmlrpc.backends import XmlRpcDeserializer, XmlRpcSerializer

logger = logging.getLogger(__name__)


@dataclass
class XmlRpcRequest(RpcRequest): ...


XmlRpcSuccessResult = RpcSuccessResult[XmlRpcRequest]
XmlRpcErrorResult = RpcErrorResult[XmlRpcRequest]
XmlRpcResult = Union[XmlRpcSuccessResult, XmlRpcErrorResult]


class XmlRpcHandler(RpcHandler[XmlRpcRequest]):
    """Default XML-RPC handler implementation"""

    protocol = Protocol.XML_RPC
    valid_content_types: ClassVar[list[str]] = ["text/xml", "application/xml"]
    response_content_type = "application/xml"
    success_result_type = XmlRpcSuccessResult
    error_result_type = XmlRpcErrorResult

    def __init__(self) -> None:
        deserializer_config = settings.MODERNRPC_XML_DESERIALIZER
        deserializer_klass: type[XmlRpcDeserializer] = import_string(deserializer_config["class"])
        deserializer_kwargs: DictStrAny = deserializer_config.get("kwargs", {})
        self.deserializer: XmlRpcDeserializer = deserializer_klass(**deserializer_kwargs)

        serializer_config = settings.MODERNRPC_XML_SERIALIZER
        serializer_klass: type[XmlRpcSerializer] = import_string(serializer_config["class"])
        serializer_kwargs: DictStrAny = serializer_config.get("kwargs", {})
        self.serializer: XmlRpcSerializer = serializer_klass(**serializer_kwargs)

    def process_request(self, request_body: str, context: RpcRequestContext) -> str:
        """
        Parse request and delegates to process_single_request(), catching exceptions to handle errors.

        `system.multicall()` is implemented in the `modernrpc.system_procedures` module.
        """
        try:
            request = self.deserializer.loads(request_body)

        except RPCException as exc:
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(XmlRpcRequest(method_name=""), exc.code, exc.message))

        result = self.process_single_request(request, context)

        try:
            return self.serializer.dumps(result)

        except RPCException as exc:
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(request, exc.code, exc.message))

    async def aprocess_request(self, request_body: str, context: RpcRequestContext) -> str:
        """
        Parse request and delegates to process_single_request(), catching exceptions to handle errors.

        `system.multicall()` is implemented in the `modernrpc.system_procedures` module.
        """
        try:
            request = self.deserializer.loads(request_body)

        except RPCException as exc:
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(XmlRpcRequest(method_name=""), exc.code, exc.message))

        result = await self.aprocess_single_request(request, context)

        try:
            return self.serializer.dumps(result)

        except RPCException as exc:
            exc = context.server.on_error(exc, context)
            return self.serializer.dumps(self.build_error_result(request, exc.code, exc.message))
