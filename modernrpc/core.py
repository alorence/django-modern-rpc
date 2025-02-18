from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterable

from django.utils.functional import cached_property

from modernrpc import Protocol
from modernrpc.constants import NOT_SET
from modernrpc.exceptions import (
    AuthenticationFailed,
    RPCException,
    RPCInternalError,
    RPCInvalidParams,
)
from modernrpc.helpers import ensure_sequence
from modernrpc.introspection import DocstringParser, Introspector

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.handlers.base import RpcHandler
    from modernrpc.server import RpcServer


# Keys used in kwargs dict given to RPC methods
# REQUEST_KEY = settings.MODERNRPC_KWARGS_REQUEST_KEY
# ENTRY_POINT_KEY = settings.MODERNRPC_KWARGS_ENTRY_POINT_KEY
# PROTOCOL_KEY = settings.MODERNRPC_KWARGS_PROTOCOL_KEY
# HANDLER_KEY = settings.MODERNRPC_KWARGS_HANDLER_KEY


logger = logging.getLogger(__name__)

# In 1.0.0, following constants were replaced by Protocol enum class
# Redefine them for backward compatibility
JSONRPC_PROTOCOL, XMLRPC_PROTOCOL = Protocol.JSON_RPC, Protocol.XML_RPC
GENERIC_ALL = ALL = Protocol.ALL


@dataclass
class RpcRequestContext:
    """Wraps all information needed to call a procedure. Instances of this class are created before call,
    and may be used to populate kwargs dict in rpc method."""

    request: HttpRequest
    server: RpcServer
    handler: RpcHandler
    protocol: Protocol
    auth_result: Any = None


class ProcedureWrapper:
    """
    Wraps a python global function to be used to extract information and call the concrete procedure.
    """

    def __init__(
        self,
        func: Callable,
        name: str | None = None,
        protocol: Protocol = Protocol.ALL,
        auth=NOT_SET,
        context_target: str | None = None,
    ) -> None:
        # Store the reference to the registered function
        self.function = func

        # @decorator parameters
        self.name = name or func.__name__
        self.protocol = protocol
        self.context_target = context_target

        self.auth = auth

    @cached_property
    def doc_parser(self):
        return DocstringParser(self.function)

    @cached_property
    def introspector(self):
        return Introspector(self.function)

    def __repr__(self) -> str:
        return f'ModernRPC Procedure "{self.name}"'

    def __str__(self) -> str:
        return f"{self.name}({', '.join(self.introspector.args)})"

    def __eq__(self, other) -> bool:
        return (
            self.function == other.function
            and self.name == other.name
            and self.protocol == other.protocol
            and self.auth == other.auth
        )

    def check_permissions(self, request: HttpRequest) -> Any:
        """Call the predicate(s) associated with the RPC method, to check if the current request
        can actually call the method.
        Return a boolean indicating if the method should be executed (True) or not (False)
        """
        if self.auth == NOT_SET or not self.auth:
            return True

        for callback in ensure_sequence(self.auth):
            if result := callback(request):
                return result

        return False

    def execute(
        self,
        context: RpcRequestContext,
        args: Iterable[Any],
        kwargs: dict | None = None,
    ) -> Any:
        kwargs = kwargs or {}

        # FIXME: handle exceptions raised from here...
        auth_result = self.check_permissions(context.request)

        if not auth_result:
            raise AuthenticationFailed(self.name)

        context.auth_result = auth_result

        # If the RPC method needs to access some configuration, inject it in kwargs
        if self.context_target:
            kwargs[self.context_target] = context

        logger.debug("Params: args = %s - kwargs = %s", args, kwargs)

        # Call the procedure, or raise an exception
        try:
            return self.function(*args, **kwargs)

        except TypeError as exc:
            # If given params cannot be transmitted properly to python function
            raise RPCInvalidParams(str(exc)) from None

        except RPCException:
            raise

        except Exception as exc:
            # Any exception raised from the remote procedure
            raise RPCInternalError(str(exc)) from exc

    @cached_property
    def args(self) -> list[str]:
        """Method arguments"""
        return [arg for arg in self.introspector.args if arg != self.context_target]

    @cached_property
    def raw_docstring(self) -> str:
        """Method docstring, as raw text"""
        return self.doc_parser.text_documentation

    @cached_property
    def html_doc(self) -> str:
        """Methods docstring, as HTML"""
        return self.doc_parser.html_documentation

    @cached_property
    def args_doc(self) -> OrderedDict[str, dict[str, str]]:
        """Build an OrderedDict mapping each method argument with its
        corresponding type (from typehint or doctype) and documentation."""
        return OrderedDict(
            {
                arg: {
                    "type": self.introspector.args_types.get(arg, "") or self.doc_parser.args_types.get(arg, ""),
                    "text": self.doc_parser.args_doc.get(arg, ""),
                }
                for arg in self.introspector.args
                if arg != self.context_target
            }
        )

    @cached_property
    def return_doc(self) -> dict[str, str]:
        """Build a dict for method's return type and documentation"""
        return {
            "type": self.introspector.return_type or self.doc_parser.return_type,
            "text": self.doc_parser.return_doc,
        }


# class _RPCRegistry:
#     def __init__(self):
#         self._registry: defaultdict[str, dict[str, ProcedureWrapper]] = defaultdict(dict)
#         self.reset()
#
#     def reset(self) -> None:
#         self._registry.clear()
#
#     def register_method(self, func: Callable) -> str:
#         """
#         Register a function to be available as RPC method.
#
#         The given function will be inspected to find external_name, protocol and entry_point
#         values set by the decorator @rpc_method.
#         :param func: A function previously decorated using @rpc_method
#         :return: The name of registered method
#         """
#         if not getattr(func, "modernrpc_enabled", False):
#             raise ImproperlyConfigured(
#                 f"Error: trying to register {func.__name__} as RPC method, but it has not been decorated."
#             )
#
#         # Define the external name of the function
#         name = getattr(func, "modernrpc_name", func.__name__)
#
#         logger.debug('Register RPC method "%s"', name)
#
#         if name.startswith("rpc."):
#             raise ImproperlyConfigured(
#                 'According to RPC standard, method names starting with "rpc." are reserved for system extensions and '
#                 "must not be used. See https://www.jsonrpc.org/specification#extensions for more information."
#             )
#
#         # Encapsulate the function in a RPCMethod object
#         wrapper = ProcedureWrapper(func)
#         entry_point = wrapper.entry_point
#
#         # Ensure method names are unique in the registry
#         existing_method = self.get_method(wrapper.name, entry_point, Protocol.ALL)
#         if existing_method is not None:
#             # Trying to register many times the same function is OK, because if a method is decorated
#             # with @rpc_method(), it could be imported in different places of the code
#             if wrapper == existing_method:
#                 return wrapper.name
#
#             # But if we try to use the same name to register 2 different methods, we
#             # must inform the developer there is an error in the code
#             raise ImproperlyConfigured(f"A RPC method with name {wrapper.name} has already been registered")
#
#         # Store the method
#         self._registry[entry_point][wrapper.name] = wrapper
#
#         return wrapper.name
#
#     def get_methods_for_entry_point(self, entry_point=ALL) -> dict[str, ProcedureWrapper]:
#         entry_points = self._registry.keys() if entry_point == ALL else [ALL, entry_point]
#
#         return {
#             name: wrapper
#             for entry_point in entry_points
#             for name, wrapper in self._registry.get(entry_point, {}).items()
#         }
#
#     def total_count(self) -> int:
#         return len(self.get_methods_for_entry_point(entry_point=ALL))
#
#     def get_all_method_names(
#         self, entry_point=ALL, protocol: Protocol = Protocol.ALL, sort_methods=False
#     ) -> list[str]:
#         """Return the names of all RPC methods registered supported by the given entry_point / protocol pair"""
#         method_names = [
#             name
#             for name, wrapper in self.get_methods_for_entry_point(entry_point).items()
#             if wrapper.available_for_protocol(protocol)
#         ]
#
#         return sorted(method_names) if sort_methods else method_names
#
#     def get_all_methods(
#         self,
#         entry_point: str = ALL,
#         protocol: Protocol = Protocol.ALL,
#         sort_methods=False,
#     ) -> list[ProcedureWrapper]:
#         """Return a list of all methods in the registry supported by the given entry_point / protocol pair"""
#         methods = self.get_methods_for_entry_point(entry_point)
#         if sort_methods:
#             methods = dict(sorted(methods.items()))
#         return [wrapper for (_, wrapper) in methods.items() if wrapper.available_for_protocol(protocol)]
#
#     def get_method(self, name: str, entry_point: str, protocol: Protocol) -> ProcedureWrapper | None:
#         """Retrieve a method from the given name"""
#         _registry = self.get_methods_for_entry_point(entry_point)
#
#         try:
#             candidate = _registry[name]
#             if candidate.available_for_protocol(protocol):
#                 return candidate
#         except KeyError:
#             logger.debug(f'Unable to retrieve RPCMethod with name "{name}" in entry_point "{entry_point}"')
#             return None
#
#         return None
