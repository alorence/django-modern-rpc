from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Union

from django.utils.module_loading import import_string

from modernrpc import Protocol
from modernrpc.conf import settings
from modernrpc.exceptions import RPCException
from modernrpc.handlers.base import GenericRpcErrorResult, GenericRpcSuccessResult, RpcHandler, RpcRequest

if TYPE_CHECKING:
    from typing import Any, ClassVar

    from modernrpc import RpcRequestContext
    from modernrpc.backends.base import XmlRpcDeserializer, XmlRpcSerializer

logger = logging.getLogger(__name__)


class XmlRpcRequest(RpcRequest): ...


XmlRpcSuccessResult = GenericRpcSuccessResult[XmlRpcRequest]
XmlRpcErrorResult = GenericRpcErrorResult[XmlRpcRequest]
XmlRpcResult = Union[XmlRpcSuccessResult, XmlRpcErrorResult]


class XmlRpcHandler(RpcHandler[XmlRpcRequest]):
    """Default XML-RPC handler implementation"""

    protocol = Protocol.XML_RPC
    valid_content_types: ClassVar[list[str]] = ["text/xml", "application/xml"]
    response_content_type = "application/xml"
    success_result_type = XmlRpcSuccessResult
    error_result_type = XmlRpcErrorResult

    def __init__(self) -> None:
        deserializer_klass: type[XmlRpcDeserializer] = import_string(settings.MODERNRPC_XML_DESERIALIZER["class"])
        deserializer_kwargs: dict[str, Any] = settings.MODERNRPC_XML_DESERIALIZER.get("kwargs", {})
        self.deserializer: XmlRpcDeserializer = deserializer_klass(**deserializer_kwargs)

        serializer_klass: type[XmlRpcSerializer] = import_string(settings.MODERNRPC_XML_SERIALIZER["class"])
        serializer_kwargs: dict[str, Any] = settings.MODERNRPC_XML_SERIALIZER.get("kwargs", {})
        self.serializer: XmlRpcSerializer = serializer_klass(**serializer_kwargs)

    def process_request(self, request_body: str, context: RpcRequestContext) -> str:
        """
        Parse request and delegates to process_single_request(), catching exceptions to handle errors.

        `system.multicall()` is implemented in `modernrpc.system_methods` module.
        """
        try:
            request = self.deserializer.loads(request_body)

        except RPCException as exc:
            exc = context.server.on_error(exc)
            return self.serializer.dumps(self.build_error_result(XmlRpcRequest(method_name=""), exc.code, exc.message))

        result = self.process_single_request(request, context)

        try:
            return self.serializer.dumps(result)
        except RPCException as exc:
            exc = context.server.on_error(exc)
            return self.serializer.dumps(self.build_error_result(request, exc.code, exc.message))
