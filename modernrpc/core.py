from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterable

from asgiref.sync import async_to_sync, iscoroutinefunction, sync_to_async
from django.utils.functional import cached_property

from modernrpc import Protocol
from modernrpc.constants import NOT_SET
from modernrpc.exceptions import (
    AuthenticationFailed,
    RPCInvalidParams,
)
from modernrpc.helpers import ensure_sequence
from modernrpc.introspection import DocstringParser, Introspector

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.handler import RpcHandler
    from modernrpc.server import RpcServer

# Keys used in kwargs dict given to RPC methods
# REQUEST_KEY = settings.MODERNRPC_KWARGS_REQUEST_KEY
# ENTRY_POINT_KEY = settings.MODERNRPC_KWARGS_ENTRY_POINT_KEY
# PROTOCOL_KEY = settings.MODERNRPC_KWARGS_PROTOCOL_KEY
# HANDLER_KEY = settings.MODERNRPC_KWARGS_HANDLER_KEY


logger = logging.getLogger(__name__)


@dataclass
class RpcRequestContext:
    """Wraps all information needed to call a procedure. Instances of this class are created before call
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
        func_or_coro: Callable,
        name: str | None = None,
        protocol: Protocol = Protocol.ALL,
        auth: Any = NOT_SET,
        context_target: str | None = None,
    ) -> None:
        # Store the reference to the registered function
        self.func_or_coro = func_or_coro

        # @decorator parameters
        self.name = name or func_or_coro.__name__
        self.protocol = protocol
        self.context_target = context_target

        self.auth = auth

    @cached_property
    def doc_parser(self) -> DocstringParser:
        return DocstringParser(self.func_or_coro)

    @cached_property
    def introspector(self) -> Introspector:
        return Introspector(self.func_or_coro)

    def __repr__(self) -> str:
        return f'ModernRPC Procedure "{self.name}"'

    def __str__(self) -> str:
        return f"{self.name}({', '.join(self.introspector.args)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcedureWrapper):
            return NotImplemented
        return (
            self.func_or_coro == other.func_or_coro
            and self.name == other.name
            and self.protocol == other.protocol
            and self.auth == other.auth
        )

    def __hash__(self):
        return hash(self.func_or_coro)

    def check_permissions(self, request: HttpRequest) -> Any:
        """Call the predicate(s) associated with the RPC method to check if the current request
        can actually call the method.
        Return a boolean indicating if the method should be executed (True) or not (False),
        or any other value that can be used by the caller.
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
        args: Iterable[Any] | None = None,
        kwargs: dict | None = None,
    ) -> Any:
        args = args or []
        kwargs = kwargs or {}

        try:
            auth_result = self.check_permissions(context.request)
        except Exception as e:
            raise AuthenticationFailed(self.name) from e

        if not auth_result:
            raise AuthenticationFailed(self.name)

        # If the remote procedure requested access to context data, provide it into proper kwargs key
        if self.context_target:
            context.auth_result = auth_result
            kwargs[self.context_target] = context

        logger.debug("Params: args = %s - kwargs = %s", args, kwargs)

        function = async_to_sync(self.func_or_coro) if iscoroutinefunction(self.func_or_coro) else self.func_or_coro

        try:
            return function(*args, **kwargs)

        except TypeError as exc:
            # If given params cannot be transmitted properly to the procedure function
            raise RPCInvalidParams(str(exc)) from None

    async def aexecute(
        self,
        context: RpcRequestContext,
        args: Iterable[Any] | None = None,
        kwargs: dict | None = None,
    ) -> Any:
        args = args or []
        kwargs = kwargs or {}

        try:
            auth_result = self.check_permissions(context.request)
        except Exception as e:
            raise AuthenticationFailed(self.name) from e

        if not auth_result:
            raise AuthenticationFailed(self.name)

        # If the remote procedure requested access to context data, provide it into proper kwargs key
        if self.context_target:
            context.auth_result = auth_result
            kwargs[self.context_target] = context

        logger.debug("Params: args = %s - kwargs = %s", args, kwargs)

        coro = self.func_or_coro if iscoroutinefunction(self.func_or_coro) else sync_to_async(self.func_or_coro)

        try:
            return await coro(*args, **kwargs)
        except TypeError as exc:
            # If given params cannot be transmitted properly to the procedure function
            raise RPCInvalidParams(str(exc)) from None

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
        """Build a dict for the method's return type and documentation"""
        return {
            "type": self.introspector.return_type or self.doc_parser.return_type,
            "text": self.doc_parser.return_doc,
        }
