from __future__ import annotations

import inspect
import logging
from importlib import import_module

from django.apps import AppConfig
from django.core import checks

from modernrpc.conf import settings
from modernrpc.core import registry

logger = logging.getLogger(__name__)


@checks.register()
def check_settings(app_configs, **kwargs):
    """Perform common checks on lib configuration, to notify for warning and errors. Uses
    Django "System check framework": see https://docs.djangoproject.com/en/3.2/topics/checks/
    """
    messages = []

    if not settings.MODERNRPC_METHODS_MODULES:
        msg = "settings.MODERNRPC_METHODS_MODULES is not set, django-modern-rpc cannot locate your RPC methods."
        hint = (
            "Please define settings.MODERNRPC_METHODS_MODULES to indicate which module(s) define your RPC methods. "
            "See https://django-modern-rpc.rtfd.io/en/latest/basics/settings.html#modernrpc-methods-modules"
        )
        messages.append(checks.Warning(msg, hint=hint, obj=settings, id="modernrpc.W001"))

    else:
        for module_name in settings.MODERNRPC_METHODS_MODULES:
            try:
                import_module(module_name)
            except ImportError as err:  # noqa: PERF203 try / except inside a loop is acceptable in such case
                # ModuleNotFoundError may be caught here, when library will require python 3.6+
                msg = f'ModuleNotFoundError exception when importing "{module_name}" module'
                hint = str(err)
                messages.append(checks.Error(msg, hint=hint, obj=settings, id="modernrpc.E001"))
            except Exception as exc:
                msg = f'{exc.__class__.__name__} exception when importing "{module_name}" module'
                hint = f"See exception info: {exc}"
                messages.append(checks.Error(msg, hint=hint, obj=settings, id="modernrpc.E002"))

    return messages


class ModernRpcConfig(AppConfig):
    name = "modernrpc"
    verbose_name = "Django Modern RPC"

    def ready(self):
        self.rpc_methods_registration()
        self.defusedxml_monkey_patch()

    def rpc_methods_registration(self) -> None:
        """Store all decorated RPC methods as well as builtin system methods into internal registry"""
        # For security (and unit tests), make sure the registry is empty before registering rpc methods
        registry.reset()

        if not settings.MODERNRPC_METHODS_MODULES:
            # settings.MODERNRPC_METHODS_MODULES is undefined or empty, but we already notified user
            # with a Django system-check. See http://docs.djangoproject.com/en/3.2/topics/checks/
            return

        self.import_modules(settings.MODERNRPC_METHODS_MODULES)
        self.import_modules(["modernrpc.system_methods"])

        logger.debug(
            "django-modern-rpc initialized: %d RPC methods registered",
            registry.total_count(),
        )

    @staticmethod
    def import_modules(modules_list: list[str]) -> None:
        """Loop on given modules_list, import each module and register
        functions annotated with @rpc_method in the internal registry"""
        for module_name in modules_list:
            # Import the module in current scope
            rpc_module = import_module(module_name)

            # Lookup all global functions in module
            for _, func in inspect.getmembers(rpc_module, inspect.isfunction):
                # And register only functions with attribute 'modernrpc_enabled' defined to True
                if getattr(func, "modernrpc_enabled", False):
                    registry.register_method(func)

    @staticmethod
    def defusedxml_monkey_patch():
        try:
            import defusedxml.xmlrpc
        except ImportError:
            msg = (
                "'defusedxml' package were not found. Your project may be vulnerable to various XML payloads based "
                "attacks. To secure the server against such malicious attacks, please install 'defusedxml' or install "
                "django-modern-rpc with extra 'defusedxml (`pip install django-modern-rpc[defusedxml]`"
            )
            logger.debug(msg)
            return

        defusedxml.xmlrpc.monkey_patch()
