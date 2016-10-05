# coding: utf-8
import logging

from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from modernrpc.core import get_all_methods, ALL
from modernrpc.exceptions import RPCInternalError, RPCException, RPCUnknownMethod
from modernrpc.handlers import JSONRPCHandler, XMLRPCHandler

logger = logging.getLogger(__name__)


class RPCEntryPoint(View):

    type = ''

    def __init__(self, entry_point="default", protocol=ALL, **kwargs):
        super(RPCEntryPoint, self).__init__(**kwargs)

        if not self.get_handler_classes():
            raise ImproperlyConfigured("At least 1 handler must be instantiated.")

        self.entry_point = entry_point
        self.protocol = protocol
        logger.debug('Create "{}" RPCEntryPoint view'.format(self.entry_point))

    # This disable CRSF validation for POST requests
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RPCEntryPoint, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get_handler_classes():
        return [
            JSONRPCHandler,
            XMLRPCHandler
        ]

    def post(self, request, *args, **kwargs):

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

        return handlers[0].result_error(RPCInternalError('Unknown error'))

    def call_system_method(self, handler, method_name, params):

        if method_name == 'system.listMethods':

            methods = [
                'system.listMethods',
            ]
            methods += get_all_methods(self.entry_point, handler.protocol)

            return methods

        raise RPCUnknownMethod(method_name)
