from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import ProcedureWrapper, Protocol, RpcRequestContext
from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPCException
from modernrpc.handlers.base import RpcHandler, XmlRpcErrorResult, XmlRpcRequest, XmlRpcResult, XmlRpcSuccessResult

if TYPE_CHECKING:
    from modernrpc.backends.base import XmlRpcDeserializer, XmlRpcSerializer


logger = logging.getLogger(__name__)


class XMLRPCHandler(RpcHandler):
    """Default XML-RPC handler implementation"""

    protocol = Protocol.XML_RPC

    def __init__(self):
        deserializer_klass = import_string(settings.MODERNRPC_XML_DESERIALIZER["class"])
        deserializer_kwargs = settings.MODERNRPC_XML_DESERIALIZER.get("kwargs", {})
        self.deserializer: XmlRpcDeserializer = deserializer_klass(**deserializer_kwargs)

        serializer_klass = import_string(settings.MODERNRPC_XML_SERIALIZER["class"])
        serializer_kwargs = settings.MODERNRPC_XML_SERIALIZER.get("kwargs", {})
        self.serializer: XmlRpcSerializer = serializer_klass(**serializer_kwargs)

    @classmethod
    def valid_content_types(cls):
        return [
            "text/xml",
            "application/xml",
        ]

    @classmethod
    def response_content_type(cls) -> str:
        return "application/xml"

    def process_request(self, request_body: str, context: RpcRequestContext) -> str:
        """
        Parse request and delegates to process_single_request(), catching exceptions to handle errors.

        `system.multicall()` is implemented in `modernrpc.system_methods` module.
        """
        try:
            request = self.deserializer.loads(request_body)

        except RPCException as exc:
            logger.exception(exc)
            result = XmlRpcErrorResult(context.request, exc.code, exc.message)

        else:
            result = self.process_single_request(request, context)

        return self.serializer.dumps(result)

    def process_single_request(self, rpc_request: XmlRpcRequest, context: RpcRequestContext) -> XmlRpcResult:
        try:
            wrapper: ProcedureWrapper = context.server.get_procedure(rpc_request.method_name)
            result_data = wrapper.execute(context, rpc_request.args)
            result = XmlRpcSuccessResult(request=rpc_request, data=result_data)

        except RPCException as exc:
            logger.exception(exc)
            result = XmlRpcErrorResult(request=rpc_request, code=exc.code, message=exc.message, data=exc.data)

        except Exception as exc:
            logger.exception(exc)
            result = XmlRpcErrorResult(request=rpc_request, code=RPC_INTERNAL_ERROR, message=str(exc))

        return result
