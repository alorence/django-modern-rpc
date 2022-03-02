# coding: utf-8
import logging
import xmlrpc.client as xmlrpc_client
from pyexpat import ExpatError
from textwrap import dedent
from typing import Any, Optional, Tuple

from modernrpc.conf import settings
from modernrpc.core import Protocol, RPCRequestContext
from modernrpc.exceptions import (
    RPCParseError,
    RPCInvalidRequest,
    RPC_INTERNAL_ERROR,
    RPCException,
)
from modernrpc.handlers.base import RPCHandler, BaseResult, SuccessResult, ErrorResult

logger = logging.getLogger(__name__)


class XmlSuccessResult(SuccessResult):
    def format(self):
        # blahblah pourquoi liste toussa
        return [self.data]


class XmlErrorResult(ErrorResult):
    def format(self):
        return xmlrpc_client.Fault(self.code, self.message)


class XMLRPCHandler(RPCHandler):
    protocol = Protocol.XML_RPC

    def __init__(self, entry_point):
        super().__init__(entry_point)

        # Marshaller is used to dumps data into valid XML-RPC response. See self.dumps() for more info
        self.marshaller = xmlrpc_client.Marshaller(
            encoding=settings.MODERNRPC_XMLRPC_DEFAULT_ENCODING,
            allow_none=settings.MODERNRPC_XMLRPC_ALLOW_NONE,
        )
        self.use_builtin_types = settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES

    @staticmethod
    def valid_content_types():
        return [
            "text/xml",
        ]

    def parse_request(self, request_body: str) -> Tuple[Any, Optional[str]]:
        try:
            params, method = xmlrpc_client.loads(
                request_body, use_builtin_types=self.use_builtin_types
            )
            return params, method

        except ExpatError as exc:
            raise RPCParseError("Error while parsing XML-RPC request: {}".format(exc))

        except Exception:
            raise RPCInvalidRequest("The request appear to be invalid.")

    def dumps_result(self, result: BaseResult) -> str:  # type: ignore[override]

        # First, format result instance into something compatible with XML-RPC Marshaller
        try:
            dumped_result = self.marshaller.dumps(result.format())
        except Exception as exc:
            # Error on result serialization: serialize an error instead
            error_msg = "Unable to serialize result: {}".format(exc)
            logger.error(error_msg, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            error_result = XmlErrorResult(RPC_INTERNAL_ERROR, error_msg)
            dumped_result = self.marshaller.dumps(error_result.format())

        # Finally, dumps the result into full response content
        final_content = (
            """
                    <?xml version="1.0"?>
                    <methodResponse>
                        %s
                    </methodResponse>
                """
            % dumped_result
        )
        return dedent(final_content).strip()

    def process_single_request(
        self, request_data: Tuple[Optional[str], Any], context
    ) -> BaseResult:
        method_name, params = request_data
        try:
            _method = self._get_called_method(method_name)
            result_data = _method.execute(context, params)
            return XmlSuccessResult(result_data)

        except RPCException as exc:
            logger.warning(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            return XmlErrorResult(exc.code, exc.message)

        except Exception as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            return XmlErrorResult(RPC_INTERNAL_ERROR, str(exc))

    def process_request(self, request_body: str, context: RPCRequestContext) -> str:

        try:
            params, method_name = self.parse_request(request_body)
        except RPCException as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = XmlErrorResult(exc.code, exc.message)  # type: BaseResult
        else:
            result = self.process_single_request((method_name, params), context)

        return self.dumps_result(result)
