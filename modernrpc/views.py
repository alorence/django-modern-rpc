# coding: utf-8
import logging
from typing import Sequence, Generator, Type

from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View

from modernrpc.conf import settings
from modernrpc.core import registry, RPCRequestContext, Protocol
from modernrpc.handlers.base import RPCHandler
from modernrpc.helpers import ensure_sequence

logger = logging.getLogger(__name__)


# Disables CSRF validation for POST requests
@method_decorator(csrf_exempt, name="dispatch")
class RPCEntryPoint(TemplateView):
    """
    This is the main entry point class. It inherits standard Django View class.
    """

    template_name = "modernrpc/default/index.html"

    entry_point = settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
    protocol = Protocol.ALL
    enable_doc = False
    enable_rpc = True

    default_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.handler_classes:
            raise ImproperlyConfigured("At least 1 handler must be instantiated.")

        # Copy static list http_method_names locally (in instance), so we can dynamically customize it
        self.http_method_names = list(View.http_method_names)

        # Customize allowed HTTP methods name to forbid access to GET when this EntryPoint
        # must not display documentation...
        if not self.enable_doc:
            self.http_method_names.remove("get")

        # ... and also forbid access to POST when this EntryPoint must not support RPC request (docs only view)
        if not self.enable_rpc:
            self.http_method_names.remove("post")
        logger.debug('RPC entry point "%s" initialized', self.entry_point)

    @cached_property
    def handler_classes(self) -> Sequence[Type[RPCHandler]]:
        """Return the list of handlers to use when receiving RPC requests."""
        handler_classes = [
            import_string(handler_cls) for handler_cls in settings.MODERNRPC_HANDLERS
        ]

        if self.protocol == Protocol.ALL:
            return handler_classes

        return [
            cls
            for cls in handler_classes
            if cls.protocol in ensure_sequence(self.protocol)
        ]

    @cached_property
    def handlers(self) -> Generator[RPCHandler, None, None]:
        for cls in self.handler_classes:
            yield cls(self.protocol)

    def post(self, request, *args, **kwargs):
        """
        Handle an XML-RPC or JSON-RPC request.

        :param request: Incoming request
        :param args: Unused
        :param kwargs: Unused
        :return: A HttpResponse containing XML-RPC or JSON-RPC response with the result of procedure call
        """
        logger.debug(
            "RPC request received... Content-Type=%s",
            request.content_type or "<unspecified>",
        )

        if not request.content_type:
            return HttpResponse(
                "Unable to handle your request, the Content-Type header is mandatory to allow server "
                "to determine which handler can interpret your request.."
            )

        # Retrieve the first RPC handler able to parse our request
        # This weird next(filter(predicate, iterable), default) structure is basically the more_itertools.first_true()
        # utility. This is written here to avoid dependency to more-itertools package
        handler = next(
            filter(lambda candidate: candidate.can_handle(request), self.handlers), None
        )

        if not handler:
            return HttpResponse(
                "Unable to handle your request. Please ensure you called "
                "the right entry point. If not, this could be a server error."
            )

        context = RPCRequestContext(
            request, handler, handler.protocol, handler.entry_point
        )
        request_body = request.body.decode(request.encoding or self.default_encoding)

        result_data = handler.process_request(request_body, context)
        return HttpResponse(result_data, content_type=handler.response_content_type())

    def get_context_data(self, **kwargs):
        """Update context data with list of RPC methods of the current entry point.
        Will be used to display methods documentation page"""
        kwargs.setdefault(
            "methods", registry.get_all_methods(self.entry_point, sort_methods=True)
        )
        return super().get_context_data(**kwargs)
