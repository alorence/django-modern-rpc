# coding: utf-8
import logging

from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from modernrpc.core import get_all_methods, ALL, get_method
from modernrpc.exceptions import RPCInternalError, RPCException, RPCUnknownMethod, RPCInvalidParams
from modernrpc.handlers import JSONRPCHandler, XMLRPCHandler

DEFAULT_ENTRYPOINT_NAME = '__default_entry_point__'

SYSTEM_LIST_METHODS = 'system.listMethods'
SYSTEM_GET_SIGNATURE = 'system.getSignature'

logger = logging.getLogger(__name__)


class RPCEntryPoint(View):
    """
    This is the main entry point class. It inherits standard Django View class.
    """

    entry_point = DEFAULT_ENTRYPOINT_NAME
    protocol = ALL

    def __init__(self, **kwargs):
        super(RPCEntryPoint, self).__init__(**kwargs)

        if not self.get_handler_classes():
            raise ImproperlyConfigured("At least 1 handler must be instantiated.")
        logger.debug('Create "{}" RPCEntryPoint view'.format(self.entry_point))

    # This disable CRSF validation for POST requests
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RPCEntryPoint, self).dispatch(request, *args, **kwargs)

    def get_handler_classes(self):

        default_hdlr_classes = [JSONRPCHandler, XMLRPCHandler]
        if self.protocol == ALL:
            return default_hdlr_classes
        else:
            return [cls for cls in default_hdlr_classes if cls.protocol == self.protocol]

    def post(self, request, *args, **kwargs):
        """
        Handle any XML-RPC or JSON-RPC request.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        logger.debug('RPC request received on entry point "{}"'.format(self.entry_point))

        handlers = []
        for handler_cls in self.get_handler_classes():

            handler = handler_cls(request, self.entry_point)
            handlers.append(handler)

            if handler.can_handle():
                try:

                    method, params = handler.parse_request()

                    if method.startswith('system.'):
                        result = self.call_system_method(handler, method, params)
                        return handler.result_success(result)

                    result = handler.call_method(method, params)

                    return handler.result_success(result)

                except RPCException as e:
                    return handler.result_error(e)
                except Exception as e:
                    return handler.result_error(RPCInternalError(str(e)))

        return HttpResponse('Unable to handle your request. Please ensure you called the right entry point. If not, '
                            'this could be a server error.')

    def call_system_method(self, handler, method_name, params):
        """
        Call a pre-defined system method

        :param handler: The handler that decoded RPC call
        :param method_name: The name of the system method to call
        :param params: Optional arguments to given with the RPC call
        :type handler: RPCHandler
        :type method_name: str
        :type params: list
        :return: Various type, depending on the method called
        """
        if method_name == SYSTEM_LIST_METHODS:

            methods = [
                SYSTEM_LIST_METHODS,
                SYSTEM_GET_SIGNATURE,
            ]
            methods += get_all_methods(self.entry_point, handler.protocol)

            return methods

        elif method_name == SYSTEM_GET_SIGNATURE:
            method_name = params[0]
            method = get_method(method_name, self.entry_point, handler.protocol)
            if method is None:
                raise RPCInvalidParams('The method {} is not found in the system. Unable to retrieve signature.')
            return method.signature

        raise RPCUnknownMethod(method_name)
