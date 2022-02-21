# coding: utf-8
import logging

from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View

from modernrpc.conf import settings
from modernrpc.core import registry, ALL, RpcRequest, RpcResult
from modernrpc.exceptions import RPCParseError, RPC_PARSE_ERROR, RPCInvalidRequest
from modernrpc.helpers import ensure_sequence

logger = logging.getLogger(__name__)


# This disables CSRF validation for POST requests
@method_decorator(csrf_exempt, name="dispatch")
class RPCEntryPoint(TemplateView):
    """
    This is the main entry point class. It inherits standard Django View class.
    """

    template_name = "modernrpc/default/index.html"

    entry_point = settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
    protocol = ALL
    enable_doc = False
    enable_rpc = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.handler_classes:
            raise ImproperlyConfigured("At least 1 handler must be instantiated.")

        # Copy static list http_method_names locally (in instance), so we can dynamically customize it
        self.http_method_names = list(View.http_method_names)

        # Customize allowed HTTP methods name to forbid access to GET when this EntryPoint
        # must not display docs...
        if not self.enable_doc:
            self.http_method_names.remove("get")

        # ... and also forbid access to POST when this EntryPoint must not support RPC request (docs only view)
        if not self.enable_rpc:
            self.http_method_names.remove("post")

        self.default_encoding = "utf-8"

        logger.debug('RPC entry point "%s" initialized', self.entry_point)

    @cached_property
    def handler_classes(self):
        """Return the list of handlers to use when receiving RPC requests."""
        handler_classes = [
            import_string(handler_cls) for handler_cls in settings.MODERNRPC_HANDLERS
        ]

        if self.protocol == ALL:
            return handler_classes

        return [
            cls
            for cls in handler_classes
            if cls.protocol in ensure_sequence(self.protocol)
        ]

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
        logger.debug("RPC request received...")

        if not request.content_type:
            return HttpResponse(
                "Unable to handle your request, the Content-Type header is mandatory to allow server "
                "to determine the right handler to interpret your request.."
            )

        # Retrieve the first RPC handler able to parse our request
        # This weird next(filter(iterable, predicate), default) structure is basically the more_itertools.first_true()
        # utility. This is written here to avoid dependency to more-itertools package
        handler = next(
            filter(lambda candidate: candidate.can_handle(request), self.handlers), None
        )

        if not handler:
            return HttpResponse(
                "Unable to handle your request. Please ensure you called "
                "the right entry point. If not, this could be a server error."
            )

        request_body = request.body.decode(request.encoding or self.default_encoding)

        try:
            rpc_request = handler.parse_request(request_body)

        except (RPCParseError, RPCInvalidRequest) as err:
            result = RpcResult()
            result.set_error(err.code, err.message)

        except Exception:
            result = RpcResult()
            result.set_error(RPC_PARSE_ERROR, "Unable to parse incoming request")

        else:
            if isinstance(rpc_request, list):
                result = []
                for single_request in rpc_request:
                    result.append(handler.process_request(request, single_request))

            elif isinstance(rpc_request, RpcRequest):
                result = handler.process_request(request, rpc_request)

            else:
                # TODO: return an error here
                pass

        result_data = handler.build_response_data(result)
        return HttpResponse(result_data)

    def get_context_data(self, **kwargs):
        """Update context data with list of RPC methods of the current entry point.
        Will be used to display methods documentation page"""
        kwargs.update(
            {
                "methods": registry.get_all_methods(
                    self.entry_point, sort_methods=True
                ),
            }
        )
        return super().get_context_data(**kwargs)
