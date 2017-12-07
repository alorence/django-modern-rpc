# coding: utf-8

from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView

from modernrpc.conf import settings
from modernrpc.core import ALL, registry
from modernrpc.exceptions import RPCInternalError, RPCException, AuthenticationFailed
from modernrpc.utils import ensure_sequence, get_modernrpc_logger

logger = get_modernrpc_logger(__name__)


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

        # Copy static list http_method_names locally (in instance), so we can dynamically customize it
        self.http_method_names = list(View.http_method_names)

        # Customize allowed HTTP methods name to forbid access to GET when this EntryPoint
        # must not display docs...
        if not self.enable_doc:
            self.http_method_names.remove('get')

        # ... and also forbid access to POST when this EntryPoint must not support RPC request (docs only view)
        if not self.enable_rpc:
            self.http_method_names.remove('post')

        logger.debug('RPC entry point "{}" initialized'.format(self.entry_point))

    # This disable CSRF validation for POST requests
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Overrides the default dispatch method, to disable CSRF validation on POST requests. This
        is mandatory to ensure RPC calls wil be correctly handled"""
        return super(RPCEntryPoint, self).dispatch(request, *args, **kwargs)

    def get_handler_classes(self):
        """Return the list of handlers to use when receiving RPC requests."""

        handler_classes = [import_string(handler_cls) for handler_cls in settings.MODERNRPC_HANDLERS]

        if self.protocol == ALL:
            return handler_classes
        else:
            return [cls for cls in handler_classes if cls.protocol in ensure_sequence(self.protocol)]

    def post(self, request, *args, **kwargs):
        """
        Handle a XML-RPC or JSON-RPC request.

        :param request: Incoming request
        :param args: Additional arguments
        :param kwargs: Additional named arguments
        :return: A HttpResponse containing XML-RPC or JSON-RPC response, depending on the incoming request
        """

        logger.debug('RPC request received...')

        for handler_cls in self.get_handler_classes():

            handler = handler_cls(request, self.entry_point)

            try:
                if not handler.can_handle():
                    continue

                logger.debug('Request will be handled by {}'.format(handler_cls.__name__))

                result = handler.process_request()

                return handler.result_success(result)

            except AuthenticationFailed as e:
                # Customize HttpResponse instance used when AuthenticationFailed was raised
                logger.warning(e)
                return handler.result_error(e, HttpResponseForbidden)

            except RPCException as e:
                logger.warning('RPC exception: {}'.format(e), exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
                return handler.result_error(e)

            except Exception as e:
                logger.error('Exception raised from a RPC method: "{}"'.format(e),
                             exc_info=settings.MODERNRPC_LOG_EXCEPTIONS)
                return handler.result_error(RPCInternalError(str(e)))

        logger.error('Unable to handle incoming request.')

        return HttpResponse('Unable to handle your request. Please ensure you called the right entry point. If not, '
                            'this could be a server error.')

    def get_context_data(self, **kwargs):
        """Update context data with list of RPC methods of the current entry point.
        Will be used to display methods documentation page"""
        kwargs.update({
            'methods': registry.get_all_methods(self.entry_point, sort_methods=True),
        })
        return super(RPCEntryPoint, self).get_context_data(**kwargs)
