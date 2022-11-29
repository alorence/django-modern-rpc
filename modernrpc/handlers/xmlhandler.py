# coding: utf-8
import logging
import xmlrpc.client as xmlrpc_client
from pyexpat import ExpatError
from textwrap import dedent
from typing import Any, Tuple

from modernrpc.conf import settings
from modernrpc.core import Protocol, RPCRequestContext
from modernrpc.exceptions import (
    RPCParseError,
    RPCInvalidRequest,
    RPC_INTERNAL_ERROR,
    RPCException,
)
from modernrpc.handlers.base import RPCHandler, BaseResult, SuccessResult, ErrorResult

RequestData = Tuple[Any, str]

logger = logging.getLogger(__name__)


class XmlSuccessResult(SuccessResult):
    """An XML-RPC success result"""

    def format(self):
        # xmlrpc_client.Marshaller expects a list of objects to dump.
        # It will output a '<params></params>' block and loops onto given objects to inject, for each one,
        # a '<param><value><type>X</type></value></param>' block.
        # This is not the return defined in XML-RPC standard, see http://xmlrpc.com/spec.md:
        # "The body of the response is a single XML structure, a <methodResponse>, which can contain
        # a single <params> which contains a single <param> which contains a single <value>."
        #
        # So, to make sure the return value always contain a single '<param><value><type>X</type></value></param>',
        # we dumps it as an array of a single value
        return [self.data]


class XmlErrorResult(ErrorResult):
    """An XML-RPC error result"""

    def format(self):
        return xmlrpc_client.Fault(self.code, self.message)


class XMLRPCHandler(RPCHandler):
    """Default XML-RPC handler implementation"""

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
            "application/xml",
        ]

    @staticmethod
    def response_content_type() -> str:
        return "application/xml"

    def process_request(self, request_body: str, context: RPCRequestContext) -> str:
        """
        Parse request and delegates to process_single_request(), catching exceptions to handle errors.

        `system.multicall()` is implemented in `modernrpc.system_methods` module.
        """
        try:
            params, method_name = self.parse_request(request_body)
        except RPCException as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            result = XmlErrorResult(exc.code, exc.message)  # type: BaseResult
        else:
            result = self.process_single_request((method_name, params), context)

        return self.dumps_result(result)

    def parse_request(self, request_body: str) -> RequestData:
        """
        Parse request body to extract `(params, methodName)` tuple, returned as `RequestData`
        """
        try:
            params, method = xmlrpc_client.loads(
                request_body, use_builtin_types=self.use_builtin_types
            )

        except ExpatError as exc:
            raise RPCParseError(
                "Error while parsing XML-RPC request: {}".format(exc)
            ) from exc

        except Exception as exc:
            raise RPCInvalidRequest("The request appear to be invalid.") from exc

        else:
            if not method:
                raise RPCInvalidRequest(
                    "Missing methodName. Please provide the name of the procedure you want to call"
                )
            return params, method

    def process_single_request(
        self, request_data: RequestData, context: RPCRequestContext
    ) -> BaseResult:
        """Check and call the RPC method, based on given tuple `(params, methodName)`"""
        method_name, params = request_data
        try:
            _method = self.get_method_wrapper(method_name)
            result_data = _method.execute(context, params)
            return XmlSuccessResult(result_data)

        except RPCException as exc:
            logger.warning(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            return XmlErrorResult(exc.code, exc.message)

        except Exception as exc:
            logger.error(exc, exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
            return XmlErrorResult(RPC_INTERNAL_ERROR, str(exc))

    def dumps_result(self, result: BaseResult) -> str:
        """Dumps result instance into a proper XML-RPC xml response"""
        try:
            # Dumps result without any check. Catch exception to handle dump errors
            dumped_result = self.marshaller.dumps(result.format())
        except Exception as exc:
            # Error on result serialization: result become an error...
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
