# coding: utf-8
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
    result = []
    if not settings.MODERNRPC_METHODS_MODULES:
        msg = 'settings.MODERNRPC_METHODS_MODULES is not set, django-modern-rpc cannot locate your RPC methods.'
        # TODO: put link to correct docs target page here
        hint = 'Please define MODERNRPC_METHODS_MODULES in your settings.py to indicate modules containing your ' \
               'methods. See documentation for more info'
        result.append(checks.Warning(msg, hint=hint, obj=settings, id="modernrpc.W001"))

    else:
        for module_name in settings.MODERNRPC_METHODS_MODULES:
            try:
                import_module(module_name)
            except ImportError as err:
                # ModuleNotFoundError may be catched here, when library will require python 3.6+
                msg = 'ModuleNotFoundError exception when importing "{}" module'.format(module_name)
                hint = str(err)
                result.append(checks.Error(msg, hint=hint, obj=settings, id="modernrpc.E001"))
            except Exception as exc:
                msg = '{} exception when importing "{}" module'.format(exc.__class__.__name__, module_name)
                hint = "See exception info: {}".format(exc)
                result.append(checks.Error(msg, hint=hint, obj=settings, id="modernrpc.E002"))

    return result


class ModernRpcConfig(AppConfig):
    name = 'modernrpc'
    verbose_name = 'Django Modern RPC'

    def ready(self):
        self.rpc_methods_registration()

    def rpc_methods_registration(self):
        """Loop over each module listed in settings.MODERNRPC_METHODS_MODULES, import each one and register
        functions annotated with @rpc_method in the internal registry"""

        # For security (and unit tests), make sure the registry is empty before registering rpc methods
        registry.reset()

        if not settings.MODERNRPC_METHODS_MODULES:
            # settings.MODERNRPC_METHODS_MODULES is undefined or empty, but we already notified user
            # with a Django system-check. See http://docs.djangoproject.com/en/1.11/topics/checks/
            return

        self.import_modules(settings.MODERNRPC_METHODS_MODULES)
        self.import_modules(['modernrpc.system_methods'])

        logger.info('django-modern-rpc initialized: %d RPC methods registered', registry.total_count())

    @staticmethod
    def import_modules(modules_list):
        for module_name in modules_list:
            # Import the module in current scope
            rpc_module = import_module(module_name)

            # Lookup all global functions in module
            for _, func in inspect.getmembers(rpc_module, inspect.isfunction):
                # And register only functions with attribute 'modernrpc_enabled' defined to True
                if getattr(func, 'modernrpc_enabled', False):
                    registry.register_method(func)
