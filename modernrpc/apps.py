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


def check_logging_configuration(app_configs, **kwargs):  # noqa

    # Lookup current user settings, and analyze the LOGGING configuration to check if
    # loggers have been configured for 'modernrpc' or 'modernrpc.<module>'
    is_modernrpc_logging_configured = False
    modernrpc_loggers = settings.LOGGING.get('loggers', {})
    for name, config in modernrpc_loggers.items():
        if name.startswith('modernrpc'):
            if len(config.get('handlers', [])) > 0:
                is_modernrpc_logging_configured = True
                break

    if is_modernrpc_logging_configured and not settings.MODERNRPC_ENABLE_LOGGING:

        return [
            django.core.checks.Info(
                'Logging is disabled in django-modern-rpc',
                hint='You properly configured logging for "modernrpc.*" in project settings, but use of configured '
                     'loggers is disabled by default. Set settings.MODERNRPC_ENABLE_LOGGING to True to correctly '
                     'propagate logs to the handlers.',
                obj=settings,
                id='modernrpc.E003',
            )
        ]

    elif settings.MODERNRPC_ENABLE_LOGGING and not is_modernrpc_logging_configured:
        django_version = '.'.join(str(x) for x in django.utils.version.get_complete_version()[:2])
        return [
            django.core.checks.Warning(
                'settings.MODERNRPC_ENABLE_LOGGING set to True, but no handler is attached to "modernrpc.* loggers". ',
                hint='You may disable modernrpc logging capabilities by setting settings.MODERNRPC_ENABLE_LOGGING to '
                     'False, or configure your project to handle logs from "modernrpc.* modules. See '
                     'https://docs.djangoproject.com/en/{version}/topics/logging/" for more info'
                     .format(version=django_version),
                obj=settings,
                id='modernrpc.E002',
            )
        ]

    return []


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
