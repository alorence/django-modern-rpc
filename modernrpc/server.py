from __future__ import annotations

import functools
import logging
from typing import TYPE_CHECKING, Callable

from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from modernrpc.conf import settings
from modernrpc.core import ProcedureWrapper, Protocol
from modernrpc.exceptions import RPCMethodNotFound
from modernrpc.helpers import first_true
from modernrpc.views import run_procedure

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.handlers.base import RpcHandler


logger = logging.getLogger(__name__)


class RegistryMixin:
    def __init__(self) -> None:
        self._registry: dict[str, ProcedureWrapper] = {}

    def register_procedure(
        self,
        procedure: Callable | None = None,
        name: str | None = None,
        protocol: Protocol = Protocol.ALL,
        context_target: str | None = None,
    ):
        """Decorator..."""

        def decorated(func: Callable):
            wrapper = ProcedureWrapper(func, name, protocol, context_target)
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
    def __init__(self, supported_protocol: Protocol = Protocol.ALL):
        super().__init__()
        self.supported_handlers = list(
            filter(
                lambda cls: cls.protocol & supported_protocol,
                (import_string(klass) for klass in settings.MODERNRPC_HANDLERS),
            )
        )

        # TODO: allow to skip this using a specific config
        system = import_string("modernrpc.system_procedures.system")
        self.register_namespace(system, "system")

    def get_procedure(self, name: str) -> ProcedureWrapper:
        try:
            return self.procedures[name]
        except KeyError:
            raise RPCMethodNotFound(name) from None

    def get_handler(self, request: HttpRequest) -> RpcHandler | None:
        klass = first_true(self.supported_handlers, pred=lambda cls: cls.can_handle(request))
        try:
            return klass()
        except TypeError:
            return None

    @property
    def view(self):
        view = functools.partial(run_procedure, server=self)
        return csrf_exempt(require_POST(view))

    def register_namespace(self, namespace: RpcNamespace, name: str | None = None):
        prefix = f"{name}." if name else ""
        logger.debug(f"About to register {len(namespace.procedures)} procedures into namespace '{prefix}'")
        for procedure_name, wrapper in namespace.procedures.items():
            self.register_procedure(
                wrapper.function,
                name=f"{prefix}{procedure_name}",
                protocol=wrapper.protocol,
                context_target=wrapper.context_target,
            )
