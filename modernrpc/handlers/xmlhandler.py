# coding: utf-8
from textwrap import dedent

import six
from six.moves import xmlrpc_client

from modernrpc.conf import settings
from modernrpc.core import XMLRPC_PROTOCOL, SingleRPCRequest
from modernrpc.exceptions import RPCInvalidRequest, RPCException
from modernrpc.handlers.base import RPCHandler


class XMLRPCHandler(RPCHandler):
    protocol = XMLRPC_PROTOCOL

    def __init__(self, entry_point):
        super(XMLRPCHandler, self).__init__(entry_point)

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
        if six.PY3:
            kwargs = {"use_builtin_types": self.use_builtin_types}
        else:
            kwargs = {"use_datetime": self.use_builtin_types}

        try:
            params, method_name = xmlrpc_client.loads(request_body, **kwargs)
        except Exception as exc:
            raise RPCInvalidRequest("Error while parsing XML-RPC request: {}".format(str(exc)))

        # Build an RPCRequest instance with parsed request data
        return SingleRPCRequest(method_name, params)

    # def format_success_data(self, data, **kwargs):
    #     # xmlrpc_client.Marshaller expects a list of objects to dumps.
    #     # It will output a '<params></params>' block and loops onto given objects to inject, for each one,
    #     # a '<param><value><type>X</type></value></param>' block.
    #     # This is not the return defined in XML-RPC standard, see http://xmlrpc.scripting.com/spec.html:
    #     # "The body of the response is a single XML structure, a <methodResponse>, which can contain
    #     # a single <params> which contains a single <param> which contains a single <value>."
    #     #
    #     # So, to make sure the return value always contain a single '<param><value><type>X</type></value></param>',
    #     # we dumps it as an array of a single value.
    #     return self.marshaller.dumps([data])
    #
    # def format_error_data(self, code, message, **kwargs):
    #     return self.marshaller.dumps(xmlrpc_client.Fault(code, message))
    #
    # def build_full_result(self, rpc_request, response_content, **kwargs):
    #     return dedent(("""
    #         <?xml version="1.0"?>
    #         <methodResponse>
    #             %s
    #         </methodResponse>
    #     """ % response_content).strip())

    def build_response_data(self, res, rpc_request):
        if isinstance(res, RPCException):
            response_content = self.marshaller.dumps(xmlrpc_client.Fault(res.code, res.message))
        else:
            response_content = self.marshaller.dumps([res])

        return dedent(("""
            <?xml version="1.0"?>
            <methodResponse>
                %s
            </methodResponse>
        """ % response_content).strip())
