# coding: utf-8
import inspect
import logging
from importlib import import_module

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

from modernrpc.core import register_rpc_method
from modernrpc.modernrpc_settings import MODERNRPC_ENTRY_POINTS_MODULES

logger = logging.getLogger(__name__)


class ModernRpcConfig(AppConfig):

    name = 'modernrpc'
    verbose_name = 'Django Modern RPC'

    def ready(self):

        if MODERNRPC_ENTRY_POINTS_MODULES:
            modules_to_scan = MODERNRPC_ENTRY_POINTS_MODULES
            # Add internal system methods to the registry
            modules_to_scan.append('modernrpc.system_methods')

            for module_name in modules_to_scan:

                try:
                    module = import_module(module_name)

                except ImportError:
                    logger.warning('Unable to load module "{}". Please check MODERNRPC_ENTRY_POINTS_MODULES for invalid'
                                   ' names'.format(module_name))
                    continue

                for _, func in inspect.getmembers(module, inspect.isfunction):
                    if getattr(func, 'modernrpc_enabled', False):
                        register_rpc_method(func)

        else:
            raise ImproperlyConfigured("Please declare which modules contains your RPC entry points, using "
                                       "MODERNRPC_ENTRY_POINTS_MODULES setting")
