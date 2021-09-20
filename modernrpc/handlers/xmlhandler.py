# coding: utf-8
import xml
from textwrap import dedent

import six
from django.http.response import HttpResponse
from six.moves import xmlrpc_client

from modernrpc.conf import settings
from modernrpc.core import XMLRPC_PROTOCOL, RPCRequest
from modernrpc.exceptions import RPCParseError, RPCInvalidRequest, RPCInternalError
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

    def parse_request(self, data):
        if six.PY3:
            kwargs = {"use_builtin_types": self.use_builtin_types}
        else:
            kwargs = {"use_datetime": self.use_builtin_types}

        try:
            params, method_name = xmlrpc_client.loads(data, **kwargs)
        except:
            # TODO: handle parse errors
            raise

        # Build an RPCRequest instance with parsed request data
        return RPCRequest(method_name, params)

    def build_result_success(self, data, **kwargs):
        # xmlrpc_client.Marshaller expects a list of objects to dumps.
        # It will output a '<params></params>' block and loops onto given objects to inject, for each one,
        # a '<param><value><type>X</type></value></param>' block.
        # This is not the return defined in XML-RPC standard, see http://xmlrpc.scripting.com/spec.html:
        # "The body of the response is a single XML structure, a <methodResponse>, which can contain
        # a single <params> which contains a single <param> which contains a single <value>."
        #
        # So, to make sure the return value always contain a single '<param><value><type>X</type></value></param>',
        # we dumps it as an array of a single value.
        result = """
            <?xml version="1.0"?>
            <methodResponse>
                %s
            </methodResponse>
        """ % self.marshaller.dumps([data])

        return dedent(result.strip())

    def build_result_error(self, code, message, **kwargs):
        result = """
            <?xml version="1.0"?>
            <methodResponse>
                %s
            </methodResponse>
        """ % self.marshaller.dumps(xmlrpc_client.Fault(code, message))
        return dedent(result.strip())
