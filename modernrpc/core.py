# coding: utf-8
import importlib
import logging

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

RPC_REGISTRY_KEY = '__rpc_registry__'
DEFAULT_REGISTRY_TIMEOUT = None
ALL = "__all__"


class RPCMethod(object):

    def __init__(self, name, function, entry_point=ALL, rpc_type=ALL):
        self.name = name
        self.module = function.__module__
        self.func_name = function.__name__
        self.entry_point = entry_point
        if rpc_type != ALL and not isinstance(rpc_type, list):
            self.rpc_type = [rpc_type]
        else:
            self.rpc_type = rpc_type

    def __call__(self, *args, **kwargs):
        """
        Call the function encapsulated by the current instance
        :param args:
        :param kwargs:
        :return:
        """
        module = importlib.import_module(self.module)
        func = getattr(module, self.func_name)
        return func(*args, **kwargs)

    def available_for_type(self, rpc_type):
        return self.rpc_type == ALL or rpc_type in self.rpc_type

    def available_for_entry_point(self, group):
        return self.entry_point == ALL or group == self.entry_point

    def is_valid_for(self, group, rpc_type):
        return self.available_for_entry_point(group) and self.available_for_type(rpc_type)


def get_method(name, entry_point, rpc_type):
    """Retrieve a method from the given name"""
    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    # Try to find the given method in cache
    if name in registry:
        method = registry.get(name)
        # Ensure the method can be returned for given entry_point and rpc_type
        if method and method.is_valid_for(entry_point, rpc_type):
            return method

    return None


def register_method(method):
    """Register a RPC method"""
    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    # Ensure method names are unique in the registry
    if method.name in registry:
        raise ImproperlyConfigured("A RPC method with same has already been registered")

    # Store the method
    registry[method.name] = method
    # Update the registry in internal cache
    cache.set(RPC_REGISTRY_KEY, registry, timeout=DEFAULT_REGISTRY_TIMEOUT)


def get_all_methods(entry_point=ALL, rpc_type=ALL):
    """Return a list of all methods in the registry supported by the given entry_point / rpc_type pair"""
    # Get the current RPC registry from internal cache
    registry = cache.get_or_set(RPC_REGISTRY_KEY, default={}, timeout=DEFAULT_REGISTRY_TIMEOUT)

    return [
        method_name for method_name, method in registry if method.is_valid_for(entry_point, rpc_type)
    ]


def rpc_method(**kwargs):

    def __register(function):

        name = kwargs.get('name', getattr(function, '__name__'))
        entry_point = kwargs.get('entry_point', ALL)
        rpc_type = kwargs.get('rpc_type', ALL)

        logger.debug('Register method {}'.format(name))
        register_method(RPCMethod(name, function, entry_point, rpc_type))

        return function

    return __register
