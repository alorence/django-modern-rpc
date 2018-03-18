# coding: utf-8
import xml

from django.http.response import HttpResponse
from django.utils.six.moves import xmlrpc_client

from modernrpc.conf import settings
from modernrpc.core import XMLRPC_PROTOCOL
from modernrpc.exceptions import RPCParseError, RPCInvalidRequest, RPCInternalError
from modernrpc.handlers.base import RPCHandler


class XMLRPCHandler(RPCHandler):

    protocol = XMLRPC_PROTOCOL

    def __init__(self, request, entry_point):
        super(XMLRPCHandler, self).__init__(request, entry_point)
        # Marshaller is used to dumps data into valid XML-RPC response. See self.dumps() for more info
        self.marshaller = xmlrpc_client.Marshaller(encoding=settings.MODERNRPC_XMLRPC_DEFAULT_ENCODING,
                                                   allow_none=settings.MODERNRPC_XMLRPC_ALLOW_NONE)

    @staticmethod
    def valid_content_types():
        return [
            'text/xml',
        ]

    def loads(self, str_data):
        try:
            try:
                # Python 3
                return xmlrpc_client.loads(str_data, use_builtin_types=settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES)
            except TypeError:
                # Python 2
                return xmlrpc_client.loads(str_data, use_datetime=settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES)

        except xml.parsers.expat.ExpatError as e:
            raise RPCParseError(e)

        except xmlrpc_client.ResponseError:
            raise RPCInvalidRequest('Bad XML-RPC payload')

        except Exception as e:
            raise RPCInvalidRequest(e)

    def dumps(self, obj):

        try:
            # Marshaller has a specific handling of Fault instance. It is given without modification
            if isinstance(obj, xmlrpc_client.Fault):
                return self.marshaller.dumps(obj)

            # xmlrpc_client.Marshaller expects a list of objects to dumps.
            # It will output a '<params></params>' block and loops onto given objects to inject, for each one,
            # a '<param><value><type>X</type></value></param>' block.
            # This is not the return defined in XML-RPC standard, see http://xmlrpc.scripting.com/spec.html:
            # "The body of the response is a single XML structure, a <methodResponse>, which can contain
            # a single <params> which contains a single <param> which contains a single <value>."
            #
            # So, to make sure the return value always contain a single '<param><value><type>X</type></value></param>',
            # we dumps it as an array of a single value.
            return self.marshaller.dumps([obj])

        except Exception as e:
            raise RPCInternalError('Unable to serialize result as valid XML: ' + str(e))

    def process_request(self):

        encoding = self.request.encoding or 'utf-8'
        data = self.request.body.decode(encoding)

        params, method_name = self.loads(data)

        if method_name is None:
            raise RPCInvalidRequest('Missing methodName')

        return self.execute_procedure(method_name, args=params)

    @staticmethod
    def xml_http_response(data, http_response_cls=HttpResponse):
        response = http_response_cls(data)
        response['Content-Type'] = 'text/xml'
        return response

    def result_success(self, data):

        raw_response = '<?xml version="1.0"?>'
        raw_response += '<methodResponse>'
        raw_response += self.dumps(data)
        raw_response += '</methodResponse>'

        return self.xml_http_response(raw_response)

    def result_error(self, exception, http_response_cls=HttpResponse):

        raw_response = '<?xml version="1.0"?>'
        raw_response += '<methodResponse>'
        raw_response += self.dumps(xmlrpc_client.Fault(exception.code, exception.message))
        raw_response += '</methodResponse>'

        return self.xml_http_response(raw_response, http_response_cls=http_response_cls)
