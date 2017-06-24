# coding: utf-8
import inspect
import warnings
from importlib import import_module

import django.core.checks
import django.utils.version
from django.apps import AppConfig

from modernrpc.conf import settings
from modernrpc.core import register_rpc_method, reset_registry, clean_old_cache_content


@django.core.checks.register()
def check_required_settings_defined(app_configs, **kwargs):  # noqa
    result = []
    if not settings.MODERNRPC_METHODS_MODULES:
        result.append(
            django.core.checks.Warning(
                'settings.MODERNRPC_METHODS_MODULES is not set, django-modern-rpc cannot locate your RPC methods.',
                hint='Please define MODERNRPC_METHODS_MODULES in your settings.py to indicate modules containing your '
                     'methods. See http://django-modern-rpc.rtfd.io/en/latest/basic_usage/methods_registration.html '
                     'for more info',
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

    @staticmethod
    def rpc_methods_registration():
        """Look into each module listed in settings.MODERNRPC_METHODS_MODULES, import each module and register
        functions annotated with @rpc_method decorator in the registry"""

        # In previous version, django-modern-rpc used the django cache system to store methods registry.
        # It is useless now, so clean the cache from old data
        clean_old_cache_content()
        # For security (and unit tests), make sure the registry is empty before registering rpc methods
        reset_registry()

        if not settings.MODERNRPC_METHODS_MODULES:
            # settings.MODERNRPC_METHODS_MODULES is undefined or empty, but we already notified user
            # with check_required_settings_defined() function. See http://docs.djangoproject.com/en/1.10/topics/checks/
            return

        # Lookup content of MODERNRPC_METHODS_MODULES, and add the module containing system methods
        for module_name in settings.MODERNRPC_METHODS_MODULES + ['modernrpc.system_methods']:

            try:
                # Import the module in current scope
                rpc_module = import_module(module_name)

            except ImportError:
                msg = 'Unable to load module "{}" declared in settings.MODERNRPC_METHODS_MODULES. Please ensure ' \
                      'it is available and doesn\'t contains any error'.format(module_name)
                warnings.warn(msg, category=Warning)
                continue

            # Lookup all global functions in module
            for _, func in inspect.getmembers(rpc_module, inspect.isfunction):
                # And register only functions with attribute 'modernrpc_enabled' defined to True
                if getattr(func, 'modernrpc_enabled', False):
                    register_rpc_method(func)
