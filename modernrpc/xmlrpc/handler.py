import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, TypeAlias

from django.utils.module_loading import import_string

from modernrpc import Protocol, RpcRequestContext
from modernrpc.config import settings
from modernrpc.exceptions import RPCException
from modernrpc.handler import RpcHandler
from modernrpc.types import DictStrAny, RpcErrorResult, RpcRequest, RpcSuccessResult

if TYPE_CHECKING:
    from modernrpc.xmlrpc.backends import XmlRpcDeserializer, XmlRpcSerializer

logger = logging.getLogger(__name__)


@dataclass
class XmlRpcRequest(RpcRequest): ...


XmlRpcSuccessResult: TypeAlias = RpcSuccessResult[XmlRpcRequest]
XmlRpcErrorResult: TypeAlias = RpcErrorResult[XmlRpcRequest]
XmlRpcResult: TypeAlias = XmlRpcSuccessResult | XmlRpcErrorResult


class XmlRpcHandler(RpcHandler[XmlRpcRequest]):
    """Default XML-RPC handler implementation"""

    protocol = Protocol.XML_RPC
    valid_content_types: ClassVar[list[str]] = ["text/xml", "application/xml"]
    response_content_type = "application/xml"

    def __init__(self) -> None:
        deserializer_config = settings.MODERNRPC_XML_DESERIALIZER
        deserializer_klass: type[XmlRpcDeserializer] = import_string(deserializer_config["class"])
        deserializer_kwargs: DictStrAny = deserializer_config.get("kwargs", {})
        self.deserializer: XmlRpcDeserializer = deserializer_klass(**deserializer_kwargs)

        serializer_config = settings.MODERNRPC_XML_SERIALIZER
        serializer_klass: type[XmlRpcSerializer] = import_string(serializer_config["class"])
        serializer_kwargs: DictStrAny = serializer_config.get("kwargs", {})
        self.serializer: XmlRpcSerializer = serializer_klass(**serializer_kwargs)

    def build_dummy_request(self) -> XmlRpcRequest:
        return XmlRpcRequest(method_name="")

    def serialize_result(self, result: XmlRpcResult) -> str:
        return self.serializer.dumps(result)

    def process_request(self, request_body: str, context: RpcRequestContext) -> str:
        """
        Parse request and delegates to process_single_request(), catching exceptions to handle errors.

        `system.multicall()` is implemented in the `modernrpc.system_procedures` module.
        """
        try:
            rpc_request = self.deserializer.loads(request_body)

        except RPCException as exc:
            return self.serialize_request_error(exc, context)

        result = self.process_single_request(rpc_request, context)
        return self.serialize_result_safely(result, context)

    async def aprocess_request(self, request_body: str, context: RpcRequestContext) -> str:
        """
        Asynchronous version of process_request().

        `system.multicall()` is implemented in the `modernrpc.system_procedures` module.
        """
        try:
            rpc_request = self.deserializer.loads(request_body)

        except RPCException as exc:
            return self.serialize_request_error(exc, context)

        result = await self.aprocess_single_request(rpc_request, context)
        return self.serialize_result_safely(result, context)
