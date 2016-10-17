# coding: utf-8
import logging

from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from modernrpc.core import ALL, get_method
from modernrpc.exceptions import RPCInternalError, RPCException, RPCUnknownMethod, RPCInvalidParams
from modernrpc.modernrpc_settings import MODERNRPC_HANDLERS, MODERNRPC_DEFAULT_ENTRYPOINT_NAME

logger = logging.getLogger(__name__)


class RPCEntryPoint(View):
    """
    This is the main entry point class. It inherits standard Django View class.
    """

    entry_point = MODERNRPC_DEFAULT_ENTRYPOINT_NAME
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

        handler_classes = [import_string(handler_cls) for handler_cls in MODERNRPC_HANDLERS]
        if self.protocol == ALL:
            return handler_classes
        else:
            return [cls for cls in handler_classes if cls.protocol == self.protocol]

    def post(self, request, *args, **kwargs):
        """
        Handle any XML-RPC or JSON-RPC request.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        logger.debug('RPC request received on entry point "{}"'.format(self.entry_point))

        for handler_cls in self.get_handler_classes():

            handler = handler_cls(request, self.entry_point)

            if handler.can_handle():
                try:

                    method, params = handler.parse_request()

                    func = get_method(method, self.entry_point, self.protocol)

                    if not func:
                        raise RPCUnknownMethod(method)

                    try:
                        result = func(request, self.entry_point, self.protocol, *params)
                    except TypeError as e:
                        raise RPCInvalidParams(str(e))

                    return handler.result_success(result)

                except RPCException as e:
                    return handler.result_error(e)
                except Exception as e:
                    return handler.result_error(RPCInternalError(str(e)))

        return HttpResponse('Unable to handle your request. Please ensure you called the right entry point. If not, '
                            'this could be a server error.')
