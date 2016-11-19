# coding: utf-8
import logging

from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from modernrpc.core import ALL, get_method, get_all_methods, REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY, HANDLER_KEY
from modernrpc.exceptions import RPCInternalError, RPCException, RPCUnknownMethod, RPCInvalidParams
from modernrpc.config import settings

logger = logging.getLogger(__name__)


class RPCEntryPoint(TemplateView):
    """
    This is the main entry point class. It inherits standard Django View class.
    """

    template_name = 'modernrpc/doc_index.html'

    entry_point = settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
    protocol = ALL
    enable_doc = False
    enable_rpc = True

    def __init__(self, **kwargs):
        super(RPCEntryPoint, self).__init__(**kwargs)

        if not self.get_handler_classes():
            raise ImproperlyConfigured("At least 1 handler must be instantiated.")
        logger.debug('RPC entry point "{}" initialized'.format(self.entry_point))

    # This disable CRSF validation for POST requests
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Overrides the default dispatch method, for 2 reasons:
         1. Filter input requests methods to respect ``enable_doc`` and ``enable_rpc`` parameters
         2. Disable CSRF validation on post request, since this is irrelevant for RPC calls.
        """

        if request.method.lower() == 'get' and not self.enable_doc:
            return self.http_method_not_allowed(request, *args, **kwargs)
        elif request.method.lower() == 'post' and not self.enable_rpc:
            return self.http_method_not_allowed(request, *args, **kwargs)

        return super(RPCEntryPoint, self).dispatch(request, *args, **kwargs)

    def _allowed_methods(self):
        allowed_methods = super(RPCEntryPoint, self)._allowed_methods()
        if not self.enable_doc:
            allowed_methods.remove('GET')
        if not self.enable_rpc:
            allowed_methods.remove('POST')
        return allowed_methods

    def get_handler_classes(self):

        handler_classes = [import_string(handler_cls) for handler_cls in settings.MODERNRPC_HANDLERS]
        if self.protocol == ALL:
            return handler_classes
        else:
            valid_protocols = self.protocol if isinstance(self.protocol, list) else [self.protocol]
            return [cls for cls in handler_classes if cls.protocol in valid_protocols]

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

            try:
                if not handler.can_handle():
                    continue

                logger.debug('Request will be handled by {}'.format(handler_cls.__name__))

                method, params = handler.parse_request()
                rpc_method = get_method(method, self.entry_point, handler_cls.protocol)

                if not rpc_method:
                    logger.warning('Unknown RPC method: {}'.format(method))
                    raise RPCUnknownMethod(method)

                logger.debug('RPC method {} will be executed'.format(method))

                try:
                    # If the RPC method needs to access some internals:
                    kwargs = {
                        REQUEST_KEY: request,
                        ENTRY_POINT_KEY: self.entry_point,
                        PROTOCOL_KEY: self.protocol,
                        HANDLER_KEY: handler,
                    }

                    # Call the python function associated with the RPC method name
                    result = rpc_method.execute(*params, **kwargs)

                except TypeError as e:
                    # If given arguments cannot be passed correctly to python function,
                    # raise an Invalid Params exceptions
                    raise RPCInvalidParams(str(e))

                return handler.result_success(result)

            except RPCException as e:
                logger.warning('RPC exception raised: {}'.format(str(e)))
                return handler.result_error(e)

            except Exception as e:
                logger.error('Exception raised from an RPC method: {}'.format(str(e)))
                return handler.result_error(RPCInternalError(str(e)))

        logger.error('Received a request impossible to handle with available handlers.')

        return HttpResponse('Unable to handle your request. Please ensure you called the right entry point. If not, '
                            'this could be a server error.')

    def get_context_data(self, **kwargs):
        """Update context data with list of RPC methods of the current entry point"""
        ctx = super(RPCEntryPoint, self).get_context_data(**kwargs)
        ctx.update({
            'methods': get_all_methods(self.entry_point, sort_methods=True),
        })
        return ctx
