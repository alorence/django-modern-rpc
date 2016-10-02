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

    def __init__(self, function, external_name, entry_point=ALL, protocol=ALL):
        self.module = function.__module__
        self.func_name = function.__name__
        self.external_name = external_name
        self.entry_point = entry_point
        if protocol != ALL and not isinstance(protocol, list):
            self.protocol = [protocol]
        else:
            self.protocol = protocol

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

    def __eq__(self, other):
        return \
            self.external_name == other.external_name and \
            self.module == other.module and \
            self.func_name == other.func_name and \
            self.entry_point == other.entry_point and \
            self.protocol == other.protocol

    def available_for_type(self, protocol):
        return self.protocol == ALL or protocol in self.protocol

    def available_for_entry_point(self, entry_point):
        return self.entry_point == ALL or entry_point == self.entry_point

    def is_valid_for(self, entry_point, protocol):
        return self.available_for_entry_point(entry_point) and self.available_for_type(protocol)


def get_method(name, entry_point, protocol):
    """Retrieve a method from the given name"""
    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    # Try to find the given method in cache
    if name in registry:
        method = registry.get(name)
        # Ensure the method can be returned for given entry_point and protocol
        if method and method.is_valid_for(entry_point, protocol):
            return method

    return None


def register_method(function, name=None, entry_point=ALL, protocol=ALL):
    """Register a RPC method"""
    # Define the external name of the function
    if not name:
        name = getattr(function, '__name__')
    logger.debug('Register method {}'.format(name))

    # Encapsulate the function in a RPCMethod object
    method = RPCMethod(function, name, entry_point, protocol)

    # Get the current RPC registry from internal cache
    registry = cache.get(RPC_REGISTRY_KEY, default={})

    # Ensure method names are unique in the registry
    if method.external_name in registry:
        # Trying to register many times the same function is OK, because if a method is decorated
        # with @rpc_method(), it could be imported in different places of the code
        if method == registry[method.external_name]:
            return
        # But if we try to use the same name to register 2 different methods, we
        # must inform the developer there is an error in the code
        else:
            raise ImproperlyConfigured("A RPC method with name {} has already been registered"
                                       .format(method.external_name))

    # Store the method
    registry[method.external_name] = method
    # Update the registry in internal cache
    cache.set(RPC_REGISTRY_KEY, registry, timeout=DEFAULT_REGISTRY_TIMEOUT)


def get_all_methods(entry_point=ALL, protocol=ALL):
    """Return a list of all methods in the registry supported by the given entry_point / protocol pair"""
    # Get the current RPC registry from internal cache
    registry = cache.get_or_set(RPC_REGISTRY_KEY, default={}, timeout=DEFAULT_REGISTRY_TIMEOUT)

    return [
        method_name for method_name, method in registry if method.is_valid_for(entry_point, protocol)
    ]


def rpc_method(**kwargs):

    def __register(function):

        name = kwargs.get('name')
        entry_point = kwargs.get('entry_point', ALL)
        protocol = kwargs.get('protocol', ALL)

        register_method(function, name, entry_point, protocol)

        return function

    return __register
