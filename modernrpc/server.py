from __future__ import annotations

import functools
import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable

from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.utils.log import log_response
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt

from modernrpc import Protocol, RpcRequestContext
from modernrpc.compat import async_csrf_exempt
from modernrpc.config import settings
from modernrpc.constants import NOT_SET, SYSTEM_NAMESPACE_DOTTED_PATH
from modernrpc.core import ProcedureWrapper
from modernrpc.exceptions import RPCException, RPCInternalError, RPCMethodNotFound
from modernrpc.helpers import check_flags_compatibility, first_true
from modernrpc.views import handle_rpc_request, handle_rpc_request_async

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.shortcuts import SupportsGetAbsoluteUrl

    from modernrpc.handler import RpcHandler
    from modernrpc.types import AuthPredicateType, FuncOrCoro

logger = logging.getLogger(__name__)

RpcErrorHandler = Callable[[BaseException, RpcRequestContext], None]


class RegistryMixin:
    """
    Common logic for both RpcNamespace and RpcServer classes.
    Provide methods to register RPC procedures into an internal registry.
    """

    def __init__(self, auth: AuthPredicateType = NOT_SET) -> None:
        self._registry: dict[str, ProcedureWrapper] = {}
        self.auth = auth

    def register_procedure(
        self,
        procedure: FuncOrCoro | None = None,
        name: str | None = None,
        protocol: Protocol = Protocol.ALL,
        auth: AuthPredicateType = NOT_SET,
        context_target: str | None = None,
    ) -> Callable:
        """
        Registers a procedure for handling RPC (Remote Procedure Call) requests. This function can be used as a
        decorator to register the given callable function as an RPC procedure.

        :param procedure: A callable function to be registered as an RPC procedure
        :param name: A custom name for the procedure. If not provided, the callable function's name is used by default.
        :param protocol: Specifies the protocol (e.g., JSON-RPC, XML-RPC) under which the procedure can be executed.
                         Defaults: Protocol.ALL
        :param auth: Defines user authentication settings or access rules for the procedure. Defaults to NOT_SET, in
                     which case the server's authentication settings will be used.
        :param context_target: Specify the procedure argument name for accessing the RPC request context.

        :raises ValueError: If a procedure can't be registered
        """

        def decorated(func: FuncOrCoro) -> FuncOrCoro:
            if name and name.startswith("rpc."):
                raise ValueError(
                    'According to JSON-RPC specs, method names starting with "rpc." are reserved for system extensions '
                    "and must not be used. See https://www.jsonrpc.org/specification#extensions for more information."
                )

            auth_predicate = self.auth if auth == NOT_SET else auth
            wrapper = ProcedureWrapper(
                func, name, protocol=protocol, auth=auth_predicate, context_target=context_target
            )

            if wrapper.name in self._registry and wrapper != self._registry[wrapper.name]:
                raise ValueError(f"Procedure {wrapper.name} is already registered")

            self._registry[wrapper.name] = wrapper
            logger.debug(f"Registered procedure {wrapper.name} into {self.__class__.__name__} instance")
            return func

        # If @server.register_procedure() is used with parenthesis (with or without argument)
        if procedure is None:
            return decorated

        # If @server.register_procedure is used without a parenthesis
        return decorated(procedure)

    @property
    def procedures(self) -> dict[str, ProcedureWrapper]:
        return self._registry


class RpcNamespace(RegistryMixin):
    """Registry for RPC procedures belonging to a given namespace."""


class RpcServer(RegistryMixin):
    """Base class to store all remote procedures for a given entry point"""

    def __init__(
        self,
        register_system_procedures: bool = True,
        supported_protocol: Protocol = Protocol.ALL,
        auth: AuthPredicateType = NOT_SET,
        error_handler: RpcErrorHandler | None = None,
        redirect_get_request_to: str | Callable[..., Any] | SupportsGetAbsoluteUrl | None = None,
        default_encoding: str = settings.MODERNRPC_DEFAULT_ENCODING,
    ) -> None:
        super().__init__(auth)
        self.handler_klasses = list(
            filter(
                lambda cls: check_flags_compatibility(cls.protocol, supported_protocol),
                (import_string(klass) for klass in settings.MODERNRPC_HANDLERS),
            )
        )

        if register_system_procedures:
            system_namespace = import_string(SYSTEM_NAMESPACE_DOTTED_PATH)
            self.register_namespace(system_namespace, "system")

        self.error_handler = error_handler
        self.redirect_get_request_target = redirect_get_request_to
        self.default_encoding = default_encoding

    def register_namespace(self, namespace: RpcNamespace, name: str | None = None) -> None:
        """Register all procedures from given namespace into the top-level server."""
        if name:
            prefix = name + "."
            logger.debug(
                f"About to register {len(namespace.procedures)} procedure(s) "
                f"from namespace '{name}' into the top-level server"
            )
        else:
            prefix = ""
            logger.debug(
                f"About to register {len(namespace.procedures)} procedure(s) "
                f"from unnamed namespace into the top-level server"
            )

        for procedure_name, wrapper in namespace.procedures.items():
            self.register_procedure(
                wrapper.func_or_coro,
                name=f"{prefix}{procedure_name}",
                protocol=wrapper.protocol,
                auth=wrapper.auth,
                context_target=wrapper.context_target,
            )

    def get_procedure_wrapper(self, name: str, protocol: Protocol) -> ProcedureWrapper:
        """Return the procedure wrapper with given name compatible with given protocol, or raise RPCMethodNotFound"""
        try:
            wrapper = self.procedures[name]
        except KeyError:
            raise RPCMethodNotFound(name) from None

        if check_flags_compatibility(wrapper.protocol, protocol):
            return wrapper

        raise RPCMethodNotFound(name) from None

    def get_request_handler(self, request: HttpRequest) -> RpcHandler | None:
        """Return the first handler that can handle the given request, or None if no handler can handle it."""
        handler_klass = first_true(self.handler_klasses, pred=lambda cls: cls.can_handle(request))
        try:
            return handler_klass()
        except TypeError:
            # first_true() returned None -> TypeError: 'NoneType' object is not callable
            return None

    def on_error(self, exception: BaseException, context: RpcRequestContext) -> RPCException:
        """
        If an error handler is defined, call it to run arbitrary code and return its not-None result.
        Else, check the given exception type and return it if it is a subclass of RPCException.
        Convert any other exception into RPCInternalError.
        """
        if self.error_handler:
            try:
                self.error_handler(exception, context)
            except Exception as exc:
                exception = exc

        if isinstance(exception, RPCException):
            return exception
        return RPCInternalError(message=str(exception))

    def build_method_not_allowed_reponse(self, request: HttpRequest) -> HttpResponseNotAllowed:
        """
        Build an HttpResponseNotAllowed instance with the correct list of allowed methods.
        """
        allowed_methods = ["GET", "POST"] if self.redirect_get_request_target else ["POST"]
        response = HttpResponseNotAllowed(allowed_methods)
        log_response(f"Method Not Allowed ({request.method}): {request.path}", response=response, request=request)
        return response

    def check_request(self, request: HttpRequest) -> HttpResponse | None:
        """
        Check incoming request for common issues. When everything is fine, return None. Else, return the appropriate
        HttpResponse instance.

        :param request: Request instance as received by Django
        :return: A response instance (HttpResponsePermanentRedirect, HttpResponseNotAllowed, HttpResponse) or None
        """
        if request.method == "GET":
            if self.redirect_get_request_target:
                return redirect(to=self.redirect_get_request_target, permanent=True)

            return self.build_method_not_allowed_reponse(request)

        if request.method != "POST":
            return self.build_method_not_allowed_reponse(request)

        if not request.content_type:
            return HttpResponse(
                "Unable to handle your request, the Content-Type header is mandatory to allow server "
                "to determine which handler can interpret your request.",
                status=HTTPStatus.BAD_REQUEST,
                content_type="text/plain",
            )
        return None

    @staticmethod
    def build_response(handler: RpcHandler, result_data: str | tuple[int, str]) -> HttpResponse:
        """Build an HttpResponse instance from the given handler and result data."""
        if isinstance(result_data, tuple) and len(result_data) == 2:
            status, result_data = result_data
        else:
            status = HTTPStatus.OK

        return HttpResponse(result_data, status=status, content_type=handler.response_content_type)

    @property
    def view(self) -> Callable:
        """
        Returns a synchronous view function that can be used in Django URL patterns.
        The view is decorated with csrf_exempt and require_POST.

        :return: A callable view function
        """
        view_func = functools.partial(handle_rpc_request, server=self)
        return csrf_exempt(view_func)

    @property
    def async_view(self) -> Callable:
        """
        Returns an asynchronous view function that can be used in Django URL patterns.
        The view is decorated with csrf_exempt and require_POST.

        :return: An awaitable async view function
        """
        view_func = functools.partial(handle_rpc_request_async, server=self)
        return async_csrf_exempt(view_func)
