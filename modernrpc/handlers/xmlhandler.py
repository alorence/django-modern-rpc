# coding: utf-8
import xmlrpc.client as xmlrpc_client
from pyexpat import ExpatError
from textwrap import dedent

from modernrpc.conf import settings
from modernrpc.core import XMLRPC_PROTOCOL, RpcRequest
from modernrpc.exceptions import RPCParseError, RPCInvalidRequest, RPC_INTERNAL_ERROR
from modernrpc.handlers.base import RPCHandler


class XMLRPCHandler(RPCHandler):
    protocol = XMLRPC_PROTOCOL

    def __init__(self, entry_point):
        super().__init__(entry_point)

        # Marshaller is used to dumps data into valid XML-RPC response. See self.dumps() for more info
        self.marshaller = xmlrpc_client.Marshaller(encoding=settings.MODERNRPC_XMLRPC_DEFAULT_ENCODING,
                                                   allow_none=settings.MODERNRPC_XMLRPC_ALLOW_NONE)
        self.use_builtin_types = settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES

    @staticmethod
    def valid_content_types():
        return [
            'text/xml',
        ]

    def parse_request(self, request_body):
        try:
            params, method_name = xmlrpc_client.loads(request_body, use_builtin_types=self.use_builtin_types)

        except ExpatError as exc:
            raise RPCParseError("Error while parsing XML-RPC request: {}".format(exc))

        except Exception:
            raise RPCInvalidRequest("The request appear to be invalid.")

        # Build an RPCRequest instance with parsed request data
        return RpcRequest(method_name, params)

    def validate_request(self, rpc_request):
        if not rpc_request.method_name:
            raise RPCInvalidRequest('Missing methodName')

    def build_response_data(self, res):
        """
        :param res:
        :type res: modernrpc.core.RpcResult
        :return:
        """
        if res.is_error():
            response_content = self.marshaller.dumps(xmlrpc_client.Fault(res.error_code, res.error_message))
        else:
            try:
                response_content = self.marshaller.dumps([res.success_data])
            except Exception as exc:
                fault = xmlrpc_client.Fault(RPC_INTERNAL_ERROR, "Unable to serialize result: {}".format(exc))
                response_content = self.marshaller.dumps(fault)

        return dedent(("""
            <?xml version="1.0"?>
            <methodResponse>
                %s
            </methodResponse>
        """ % response_content).strip())
