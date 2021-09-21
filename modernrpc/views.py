# coding: utf-8
import logging

import six
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.http.response import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from more_itertools import first_true

import modernrpc.compat
from modernrpc.conf import settings
from modernrpc.core import ALL, registry, REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY, HANDLER_KEY
from modernrpc.exceptions import (AuthenticationFailed, RPCException,
                                  RPCInternalError, RPCUnknownMethod, RPCInvalidParams, RPC_INVALID_REQUEST,
                                  RPC_METHOD_NOT_FOUND, RPC_INTERNAL_ERROR)
from modernrpc.handlers.base import RPCHandler
from modernrpc.helpers import ensure_sequence

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

        if not self.handler_classes:
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

        self.default_encoding = "utf-8"

        logger.debug('RPC entry point "%s" initialized', self.entry_point)

    # This disable CSRF validation for POST requests
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Overrides the default dispatch method, to disable CSRF validation on POST requests. This
        is mandatory to ensure RPC calls wil be correctly handled"""
        return super(RPCEntryPoint, self).dispatch(request, *args, **kwargs)

    @cached_property
    def handler_classes(self):
        """Return the list of handlers to use when receiving RPC requests."""
        handler_classes = [
            import_string(handler_cls) for handler_cls in settings.MODERNRPC_HANDLERS
        ]

        if self.protocol == ALL:
            return handler_classes
        else:
            return [cls for cls in handler_classes if cls.protocol in ensure_sequence(self.protocol)]

    @cached_property
    def handlers(self):
        for cls in self.handler_classes:
            yield cls(self.protocol)

    def post(self, request, *args, **kwargs):
        """
        Handle a XML-RPC or JSON-RPC request.

        :param request: Incoming request
        :param args: Additional arguments
        :param kwargs: Additional named arguments
        :return: A HttpResponse containing XML-RPC or JSON-RPC response, depending on the incoming request
        """
        logger.debug('RPC request received...')

        response_klass = HttpResponse

        # Retrieve the first RPC handler able to parse our request
        handler: RPCHandler = first_true(self.handlers, pred=lambda candidate: candidate.can_handle(request))

        if not handler:
            return HttpResponse(
                'Unable to handle your request. Please ensure you called '
                'the right entry point. If not, this could be a server error.'
            )

        request_body = request.body.decode(request.encoding or self.default_encoding)

        rpc_request = None

        try:
            rpc_request = handler.parse_request(request_body)
            handler.validate_request(rpc_request)

            call_result = rpc_request.call(request, handler, self.entry_point, handler.protocol)
            response_data = handler.format_success_data(call_result)

        except AuthenticationFailed as exc:
            response_klass = HttpResponseForbidden
            response_data = handler.format_error_data(exc.code, exc.message)

        except RPCException as exc:
            response_data = handler.format_error_data(exc.code, exc.message, error_data=exc.data)

        except Exception as exc:
            response_data = handler.format_error_data(
                RPC_INTERNAL_ERROR,
                "Unknown error when executing rpc method: {}".format(str(exc))
            )

        try:
            final_response = handler.build_full_result(rpc_request, response_data)
        except Exception as exc:
            response_data = handler.format_error_data(
                RPC_INTERNAL_ERROR, "Unable to serialize result: {}".format(str(exc))
            )
            final_response = handler.build_full_result(rpc_request, response_data)

        return response_klass(final_response)


    def get_context_data(self, **kwargs):
        """Update context data with list of RPC methods of the current entry point.
        Will be used to display methods documentation page"""
        kwargs.update({
            'methods': registry.get_all_methods(self.entry_point, sort_methods=True),
        })
        return super(RPCEntryPoint, self).get_context_data(**kwargs)
