# coding: utf-8
import inspect
import warnings
from importlib import import_module

import django.core.checks
from django.apps import AppConfig

from modernrpc.conf import settings
from modernrpc.core import register_rpc_method, get_all_method_names, unregister_rpc_method


@django.core.checks.register()
def check_required_settings_defined(app_configs, **kwargs):
    result = []
    if not settings.MODERNRPC_METHODS_MODULES:
        result.append(
            django.core.checks.Warning(
                'settings.MODERNRPC_METHODS_MODULES is not set, django-modern-rpc cannot '
                'determine which python modules define your RPC methods.',
                hint='Please define settings.MODERNRPC_METHODS_MODULES to indicate modules containing your methods.',
                obj=settings,
                id='modernrpc.E001',
            )
        )
    return result


class ModernRpcConfig(AppConfig):

    name = 'modernrpc'
    verbose_name = 'Django Modern RPC'

    def ready(self):
        self.rpc_methods_registration()

    def rpc_methods_registration(self):
        """Look into each module listed in settings.MODERNRPC_METHODS_MODULES, import each module and register
        functions annotated with @rpc_method decorator in the registry"""

        if not settings.MODERNRPC_METHODS_MODULES:
            # settings.MODERNRPC_METHODS_MODULES is undefined or empty, but we already notified user
            # with check_required_settings_defined() function. See http://docs.djangoproject.com/en/1.10/topics/checks/
            return

        # When project use a persistant cache system (Redis, memcached, etc.), it may contains old data from
        # previous runs. Compute the list now, so later we can remove useless RPC methods from registry
        needs_removal = get_all_method_names()

        # Lookup content of MODERNRPC_METHODS_MODULES, and add the module containing system methods
        for module_name in settings.MODERNRPC_METHODS_MODULES + ['modernrpc.system_methods']:

            try:
                # Import the module in current scope
                module = import_module(module_name)

            except ImportError:
                msg = 'Unable to load module "{}" declared in settings.MODERNRPC_METHODS_MODULES. Please ensure ' \
                      'it is available and doesn\'t contains any error'.format(module_name)
                warnings.warn(msg, category=Warning)
                continue

            # Lookup all global functions in module
            for _, func in inspect.getmembers(module, inspect.isfunction):
                # And register only functions with attribute 'modernrpc_enabled' defined to True
                if getattr(func, 'modernrpc_enabled', False):
                    registered_name = register_rpc_method(func)
                    try:
                        # Remove the registered method from the previously known list
                        needs_removal.remove(registered_name)
                    except ValueError:
                        pass

        # Now, all methods remaining in needs_removal can be deleted from cache.
        # The corresponding functions have been renamed, deleted or undecorated
        for name in needs_removal:
            unregister_rpc_method(name)
