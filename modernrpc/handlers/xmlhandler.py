# coding: utf-8
try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module

from django.http.response import HttpResponse

from modernrpc.exceptions import RPCInternalError, RPCException
from modernrpc.handlers.base import RPCHandler

XMLRPC = '__xml_rpc'


class XMLRPCHandler(RPCHandler):

    def __init__(self,entry_point):
        super(XMLRPCHandler, self).__init__(entry_point, XMLRPC)

        self.marshaller = xmlrpc_module.Marshaller()

    @staticmethod
    def valid_content_types():
        return [
            'text/xml',
        ]

    def loads(self, data):
        return xmlrpc_module.loads(data)

    def dumps(self, obj):

        # Marshaller has a specific handling of Fault instance. It is given without modification
        if isinstance(obj, xmlrpc_module.Fault):
            return self.marshaller.dumps(obj)

        # xmlrpc.client.Marshaller (or the Python equivalent) expects a list of objects to dumps.
        # It will loop over these objects, will output a <param><value>X</value></param> for each element.
        # This is not the return defined in XML-RPC standard, see http://xmlrpc.scripting.com/spec.html:
        # > The body of the response is a single XML structure, a <methodResponse>, which can contain
        # > a single <params> which contains a single <param> which contains a single <value>.
        # For any type to dump, we need to give a list of only 1 element:
        return self.marshaller.dumps([obj])

    def handle(self, request):

        try:
            encoding = request.encoding or 'utf-8'

            data = request.body.decode(encoding)
            params, method_name = self.loads(data)

            result = self.call_method(method_name, params)

            return self.result_success(result)
        except RPCException as e:
            return self.result_error(e)
        except Exception as e:
            return self.result_error(RPCInternalError(str(e)))

    @staticmethod
    def xml_http_response(data):
        response = HttpResponse(data)
        response['Content-Type'] = 'text/xml'
        return response

    def result_success(self, data):

        raw_response = '<?xml version="1.0"?>'
        raw_response += '<methodResponse>'
        raw_response += self.dumps(data)
        raw_response += '</methodResponse>'

        return self.xml_http_response(raw_response)

    def result_error(self, exception):

        raw_response = '<?xml version="1.0"?>'
        raw_response += '<methodResponse>'
        raw_response += self.dumps(xmlrpc_module.Fault(exception.code, exception.message))
        raw_response += '</methodResponse>'

        return self.xml_http_response(raw_response)
