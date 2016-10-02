# coding: utf-8
import logging

from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from modernrpc.exceptions import RPCInternalError
from modernrpc.handlers.jsonhandler import JSONRPCHandler
from modernrpc.handlers.xmlhandler import XMLRPCHandler

logger = logging.getLogger(__name__)


class RPCEntryPoint(View):

    type = ''

    def __init__(self, entry_point="default", **kwargs):
        super(RPCEntryPoint, self).__init__(**kwargs)
        self.entry_point = entry_point
        # Create handlers instances, based on the list of classes returned by self.get_handler_classes
        self.handlers = [
            handler_cls(entry_point) for handler_cls in self.get_handler_classes()
        ]
        if not self.handlers:
            raise ImproperlyConfigured("At least 1 handler must be instantiated.")

        self.type = ''

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

        for handler in self.handlers:
            if handler.can_handle(request):
                return handler.handle(request)

        return self.handlers[0].result_error(RPCInternalError('Unknown error'))
