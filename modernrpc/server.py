from __future__ import annotations

import functools
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING, Any

from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from modernrpc import Protocol
from modernrpc.conf import settings
from modernrpc.constants import NOT_SET
from modernrpc.core import ProcedureWrapper
from modernrpc.exceptions import RPCException, RPCInternalError, RPCMethodNotFound
from modernrpc.helpers import check_flags_compatibility, first_true
from modernrpc.views import handle_rpc_request

if TYPE_CHECKING:
    from typing import Callable

    from django.http import HttpRequest

    from modernrpc.handlers.base import RpcHandler


logger = logging.getLogger(__name__)


class RegistryMixin:
    def __init__(self, auth: Any = NOT_SET) -> None:
        self._registry: dict[str, ProcedureWrapper] = {}
        self.auth = auth

    def register_procedure(
        self,
        procedure: Callable | None = None,
        name: str | None = None,
        protocol: Protocol = Protocol.ALL,
        auth: Any = NOT_SET,
        context_target: str | None = None,
    ) -> Callable:
        """Decorator..."""

        def decorated(func: Callable) -> Callable:
            if name and name.startswith("rpc."):
                raise ValueError(
                    'According to JSON-RPC specs, method names starting with "rpc." are reserved for system extensions '
                    "and must not be used. See https://www.jsonrpc.org/specification#extensions for more information."
                )

            wrapper = ProcedureWrapper(
                func,
                name,
                protocol=protocol,
                auth=self.auth if auth == NOT_SET else auth,
                context_target=context_target,
            )

            if wrapper.name in self._registry and wrapper != self._registry[wrapper.name]:
                raise ValueError(f"Procedure {wrapper.name} is already registered")

            self._registry[wrapper.name] = wrapper
            logger.debug(f"Registered procedure {wrapper.name}")
            return func

        # If @server.register_procedure() is used with parenthesis (with or without argument)
        if procedure is None:
            return decorated

        # If @server.register_procedure is used without parenthesis
        return decorated(procedure)

    @property
    def procedures(self) -> dict[str, ProcedureWrapper]:
        return self._registry


class RpcNamespace(RegistryMixin): ...


class RpcServer(RegistryMixin):
    def __init__(self, supported_protocol: Protocol = Protocol.ALL, auth: Any = NOT_SET) -> None:
        super().__init__(auth)
        self.supported_handlers = list(
            filter(
                lambda cls: check_flags_compatibility(cls.protocol, supported_protocol),
                (import_string(klass) for klass in settings.MODERNRPC_HANDLERS),
            )
        )

        # Register system procedures if enabled in settings
        if settings.MODERNRPC_REGISTER_SYSTEM_PROCEDURES:
            system = import_string("modernrpc.system_procedures.system")
            self.register_namespace(system, "system")

        self.error_handlers: OrderedDict[type, Callable] = OrderedDict()

    def register_namespace(self, namespace: RpcNamespace, name: str | None = None) -> None:
        prefix = f"{name}." if name else ""
        logger.debug(f"About to register {len(namespace.procedures)} procedures into namespace '{prefix}'")

        for procedure_name, wrapper in namespace.procedures.items():
            self.register_procedure(
                wrapper.function,
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

    def get_handler(self, request: HttpRequest) -> RpcHandler | None:
        klass = first_true(self.supported_handlers, pred=lambda cls: cls.can_handle(request))
        try:
            return klass()
        except TypeError:
            return None

    def error_handler(self, exception_klass: type[BaseException], handler: Callable) -> None:
        """Register a new error handler for a specific function"""
        self.error_handlers[exception_klass] = handler

    def on_error(self, exception: BaseException) -> RPCException:
        """Do something when an exception happen"""
        for klass, handler in self.error_handlers.items():
            if isinstance(exception, klass) and (result := handler(exception)):
                return result
        if isinstance(exception, RPCException):
            return exception
        return RPCInternalError(message=str(exception))

    @property
    def view(self) -> Callable:
        view = functools.partial(handle_rpc_request, server=self)
        return csrf_exempt(require_POST(view))
