# coding: utf-8
import functools
import logging
from collections import OrderedDict
from enum import Enum
from types import FunctionType
from typing import TYPE_CHECKING, Any, Optional, List, Dict, Iterable

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils.functional import cached_property

from modernrpc.conf import settings
from modernrpc.exceptions import (
    AuthenticationFailed,
    RPCInvalidParams,
    RPCInternalError,
    RPCException,
)
from modernrpc.helpers import ensure_sequence
from modernrpc.introspection import Introspector, DocstringParser

if TYPE_CHECKING:
    from modernrpc.handlers.base import RPCHandler

# Special constant meaning "all protocols" or "all entry points"
GENERIC_ALL = ALL = "__all__"

# Keys used in kwargs dict given to RPC methods
REQUEST_KEY = settings.MODERNRPC_KWARGS_REQUEST_KEY
ENTRY_POINT_KEY = settings.MODERNRPC_KWARGS_ENTRY_POINT_KEY
PROTOCOL_KEY = settings.MODERNRPC_KWARGS_PROTOCOL_KEY
HANDLER_KEY = settings.MODERNRPC_KWARGS_HANDLER_KEY

logger = logging.getLogger(__name__)


class Protocol(str, Enum):
    """Define a custom type to use everywhere a protocol (JSON-RPC or XML-RPC) is expected"""

    ALL = GENERIC_ALL
    JSON_RPC = "__json_rpc"
    XML_RPC = "__xml_rpc"


class RPCRequestContext:
    """Wraps all information needed to call a procedure. Instances of this class are created before call,
    and may be used to populate kwargs dict in rpc method."""

    def __init__(
        self,
        request: HttpRequest,
        # Double quotes will prevent circular import, as this
        # is the only place RPCHandler is used in core module
        handler: "RPCHandler",
        protocol: Protocol,
        entry_point: str,
    ):
        self.request = request
        self.handler = handler
        self.protocol = protocol
        self.entry_point = entry_point


class RPCMethod:
    """
    Wraps a python global function to be used to extract information and call the concrete procedure.
    """

    def __init__(self, func: FunctionType):
        # Store the reference to the registered function
        self.function = func

        # @rpc_method decorator parameters
        self.entry_point = getattr(func, "modernrpc_entry_point")
        self.protocol = getattr(func, "modernrpc_protocol")

        # Authentication related attributes
        self.predicates = getattr(func, "modernrpc_auth_predicates", None)
        self.predicates_params = getattr(func, "modernrpc_auth_predicates_params", ())

        # Introspection:
        self.introspector = Introspector(self.function)
        self.doc_parser = DocstringParser(self.function)

    @property
    def name(self) -> str:
        return getattr(self.function, "modernrpc_name", self.function.__name__)

    def __repr__(self) -> str:
        return "RPC Method " + self.name

    def __str__(self) -> str:
        return "{}({})".format(self.name, ", ".join(self.introspector.args))

    def __eq__(self, other) -> bool:
        return (
            self.function == other.function
            and self.name == other.name
            and self.entry_point == other.entry_point
            and self.protocol == other.protocol
            and self.predicates == other.predicates
            and self.predicates_params == other.predicates_params
        )

    def check_permissions(self, request: HttpRequest) -> bool:
        """Call the predicate(s) associated with the RPC method, to check if the current request
        can actually call the method.
        Return a boolean indicating if the method should be executed (True) or not (False)"""
        if not self.predicates:
            return True

        # All registered authentication predicates must return True
        return all(
            predicate(request, *self.predicates_params[i])
            for i, predicate in enumerate(self.predicates)
        )

    def execute(
        self,
        context: RPCRequestContext,
        args: Iterable[Any],
        kwargs: Optional[dict] = None,
    ) -> Any:

        kwargs = kwargs or {}

        if not self.check_permissions(context.request):
            raise AuthenticationFailed(self.name)

        # If the RPC method needs to access some configuration, update kwargs dict
        if self.accept_kwargs:
            kwargs.update(
                {
                    REQUEST_KEY: context.request,
                    ENTRY_POINT_KEY: context.entry_point,
                    PROTOCOL_KEY: context.protocol,
                    HANDLER_KEY: context.handler,
                }
            )

        logger.debug("Params: args = %s - kwargs = %s", args, kwargs)

        # Call the procedure, or raise an exception
        try:
            return self.function(*args, **kwargs)
        except TypeError as exc:
            # If given params cannot be transmitted properly to python function
            raise RPCInvalidParams(str(exc))
        except RPCException:
            raise
        except Exception as exc:
            # Any exception raised from the remote procedure
            raise RPCInternalError(str(exc))

    def available_for_protocol(self, protocol: Protocol) -> bool:
        """Check if the current function can be executed from a request through the given protocol"""
        if Protocol.ALL in (self.protocol, protocol):
            return True
        return protocol in ensure_sequence(self.protocol)

    def available_for_entry_point(self, entry_point: str) -> bool:
        """Check if the current function can be executed from a request to the given entry point"""
        if ALL in (self.entry_point, entry_point):
            return True
        return entry_point in ensure_sequence(self.entry_point)

    def is_valid_for(self, entry_point: str, protocol: Protocol) -> bool:
        """Check if the current function can be executed from a request to the given entry point
        and with the given protocol"""
        return self.available_for_entry_point(
            entry_point
        ) and self.available_for_protocol(protocol)

    is_available_in_json_rpc = functools.partialmethod(
        available_for_protocol, Protocol.JSON_RPC
    )
    is_available_in_xml_rpc = functools.partialmethod(
        available_for_protocol, Protocol.XML_RPC
    )

    @cached_property
    def accept_kwargs(self) -> bool:
        return self.introspector.accept_kwargs

    @cached_property
    def args(self) -> List[str]:
        """Method arguments"""
        return self.introspector.args

    @cached_property
    def raw_docstring(self) -> str:
        """Method docstring, as raw text"""
        return self.doc_parser.raw_docstring

    @cached_property
    def html_doc(self) -> str:
        """Methods docstring, as HTML"""
        return self.doc_parser.html_doc

    @cached_property
    def args_doc(self) -> OrderedDict:
        """Build an OrderedDict mapping each method argument with its
        corresponding type (from typehint or doctype) and documentation."""
        result = OrderedDict()
        for arg in self.introspector.args:
            result[arg] = {
                "type": self.doc_parser.args_types.get(arg, "")
                or self.introspector.args_types.get(arg, ""),
                "text": self.doc_parser.args_doc.get(arg, ""),
            }
        return result

    @cached_property
    def return_doc(self) -> Dict[str, str]:
        """Build a dict for method's return type and documentation"""
        return {
            "type": self.doc_parser.return_type or self.introspector.return_type,
            "text": self.doc_parser.return_doc,
        }


class _RPCRegistry:
    def __init__(self):
        self._registry = {}

    def reset(self) -> None:
        self._registry.clear()

    def register_method(self, func: FunctionType) -> str:
        """
        Register a function to be available as RPC method.

        The given function will be inspected to find external_name, protocol and entry_point values set by the decorator
        @rpc_method.
        :param func: A function previously decorated using @rpc_method
        :return: The name of registered method
        """
        if not getattr(func, "modernrpc_enabled", False):
            raise ImproperlyConfigured(
                "Error: trying to register {} as RPC method, but it has not been decorated.".format(
                    func.__name__
                )
            )

        # Define the external name of the function
        name = getattr(func, "modernrpc_name", func.__name__)

        logger.debug('Register RPC method "%s"', name)

        if name.startswith("rpc."):
            raise ImproperlyConfigured(
                'According to RPC standard, method names starting with "rpc." are reserved for system extensions and '
                "must not be used. See https://www.jsonrpc.org/specification#extensions for more information."
            )

        # Encapsulate the function in a RPCMethod object
        method = RPCMethod(func)

        # Ensure method names are unique in the registry
        existing_method = self.get_method(method.name, ALL, Protocol.ALL)
        if existing_method is not None:
            # Trying to register many times the same function is OK, because if a method is decorated
            # with @rpc_method(), it could be imported in different places of the code
            if method == existing_method:
                return method.name

            # But if we try to use the same name to register 2 different methods, we
            # must inform the developer there is an error in the code
            raise ImproperlyConfigured(
                "A RPC method with name {} has already been registered".format(
                    method.name
                )
            )

        # Store the method
        self._registry[method.name] = method
        logger.debug("Method registered. len(registry): %d", len(self._registry))

        return method.name

    def total_count(self) -> int:
        return len(self._registry)

    def get_all_method_names(
        self, entry_point=ALL, protocol: Protocol = Protocol.ALL, sort_methods=False
    ) -> List[str]:
        """Return the names of all RPC methods registered supported by the given entry_point / protocol pair"""
        method_names = [
            name
            for name, method in self._registry.items()
            if method.is_valid_for(entry_point, protocol)
        ]

        if sort_methods:
            method_names = sorted(method_names)

        return method_names

    def get_all_methods(
        self,
        entry_point: str = ALL,
        protocol: Protocol = Protocol.ALL,
        sort_methods=False,
    ) -> List[RPCMethod]:
        """Return a list of all methods in the registry supported by the given entry_point / protocol pair"""

        items = (
            sorted(self._registry.items()) if sort_methods else self._registry.items()
        )
        return [
            method
            for (_, method) in items
            if method.is_valid_for(entry_point, protocol)
        ]

    def get_method(
        self, name: str, entry_point: str, protocol: Protocol
    ) -> Optional[RPCMethod]:
        """Retrieve a method from the given name"""

        if name in self._registry and self._registry[name].is_valid_for(
            entry_point, protocol
        ):
            return self._registry[name]

        return None


registry = _RPCRegistry()


def rpc_method(
    func=None,
    name: str = None,
    entry_point: str = ALL,
    protocol: Protocol = Protocol.ALL,
):
    """
    Mark a standard python function as RPC method.

    All arguments are optional

    :param func: A standard function
    :param name: Used as RPC method name instead of original function name
    :param entry_point: Default: ALL. Used to limit usage of the RPC method for a specific set of entry points
    :param protocol: Default: ALL. Used to limit usage of the RPC method for a specific protocol (JSONRPC or XMLRPC)
    """

    def decorated(_func):
        _func.modernrpc_enabled = True
        _func.modernrpc_name = name or _func.__name__
        _func.modernrpc_entry_point = entry_point
        _func.modernrpc_protocol = protocol

        return _func

    # If @rpc_method() is used with parenthesis (with or without argument)
    if func is None:
        return decorated

    # If @rpc_method is used without parenthesis
    return decorated(func)


# Backward compatibility.
# In release 0.11.0, following global functions have been moved to a proper _RPCRegistry class,
# instantiated as a global "registry". For backward compatibility
def register_rpc_method(func):
    """For backward compatibility. Use registry.register_method() instead (with same arguments)"""
    return registry.register_method(func)


def get_all_method_names(entry_point=ALL, protocol=Protocol.ALL, sort_methods=False):
    """For backward compatibility. Use registry.get_all_method_names() instead (with same arguments)"""
    return registry.get_all_method_names(
        entry_point=entry_point, protocol=protocol, sort_methods=sort_methods
    )


def get_all_methods(entry_point=ALL, protocol=Protocol.ALL, sort_methods=False):
    """For backward compatibility. Use registry.get_all_methods() instead (with same arguments)"""
    return registry.get_all_methods(
        entry_point=entry_point, protocol=protocol, sort_methods=sort_methods
    )


def get_method(name, entry_point, protocol):
    """For backward compatibility. Use registry.get_method() instead (with same arguments)"""
    return registry.get_method(name, entry_point, protocol)


def reset_registry():
    """For backward compatibility. Use registry.reset() instead"""
    return registry.reset()


# In 1.0.0, following constants were replaced by Protocol enum class
# Redefine them for backward compatibility
JSONRPC_PROTOCOL, XMLRPC_PROTOCOL = Protocol.JSON_RPC, Protocol.XML_RPC
