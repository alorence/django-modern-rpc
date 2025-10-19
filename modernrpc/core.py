from __future__ import annotations

import importlib
import logging
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterable

from asgiref.sync import async_to_sync, iscoroutinefunction, sync_to_async
from django.utils.functional import cached_property

from modernrpc import Protocol
from modernrpc.config import settings
from modernrpc.constants import NOT_SET
from modernrpc.exceptions import (
    AuthenticationError,
    RPCInvalidParams,
)
from modernrpc.helpers import check_flags_compatibility, ensure_sequence
from modernrpc.introspection import DocstringParser, Introspector

if TYPE_CHECKING:
    from django.http import HttpRequest

    from modernrpc.handler import RpcHandler
    from modernrpc.server import RpcServer
    from modernrpc.types import AuthPredicateType

logger = logging.getLogger(__name__)


@dataclass
class RpcRequestContext:
    """
    Represents the context of an RPC request.

    This class serves as a container for the components involved in the processing of an RPC request.
    It holds references to the original http request, server, handler, protocol, and optionally, the authentication
    result, providing access to contextual information needed during the RPC's lifecycle.

    :ivar request: The HTTP request associated with the RPC context.
    :ivar server: The RPC server handling the request.
    :ivar handler: The handler responsible for processing the RPC request.
    :ivar protocol: The protocol used for the RPC.
    :ivar auth_result: The result of authentication for this RPC context, if applicable.
    """

    request: HttpRequest
    server: RpcServer
    handler: RpcHandler
    protocol: Protocol
    auth_result: Any = None


@dataclass
class ProcedureArgDocs:
    docstring: str = ""
    doc_type: str = ""
    type_hint: type | None = None

    @property
    def type_hint_as_str(self) -> str:
        return self.type_hint.__name__ if self.type_hint else ""

    @property
    def documented_type(self) -> str:
        return self.type_hint_as_str or self.doc_type


class ProcedureWrapper:
    """
    Wraps a python global function to be used to extract information and call the concrete procedure.
    """

    def __init__(
        self,
        func_or_coro: Callable,
        name: str | None = None,
        protocol: Protocol = Protocol.ALL,
        auth: AuthPredicateType = NOT_SET,
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
    def introspector(self) -> Introspector:
        return Introspector(self.func_or_coro)

    @cached_property
    def docstring_parser(self) -> DocstringParser:
        return DocstringParser(self.func_or_coro)

    def __repr__(self) -> str:
        return f'ModernRPC Procedure "{self.name}"'

    def __str__(self) -> str:
        return f"{self.name}({', '.join(self.arguments.keys())})"

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
        """
        Call each predicate associated with the procedure to check authentication.
        If any of the predicate returns a truthy value, it is returned as result.
        In other cases, raise an AuthenticationFailed exception.
        """
        if self.auth == NOT_SET or not self.auth:
            return True

        for callback in ensure_sequence(self.auth):
            if result := callback(request):
                return result

        raise AuthenticationError(self.name)

    def execute(
        self,
        context: RpcRequestContext,
        args: Iterable[Any] | None = None,
        kwargs: dict | None = None,
    ) -> Any:
        args = args or []
        kwargs = kwargs or {}

        try:
            context.auth_result = self.check_permissions(context.request)
        except Exception as exc:
            raise AuthenticationError(self.name) from exc

        # If the remote procedure requested access to context data, provide it into proper kwargs key
        if self.context_target:
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
        except Exception as exc:
            raise AuthenticationError(self.name) from exc

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
    def is_available_in_xml_rpc(self):
        return check_flags_compatibility(self.protocol, Protocol.XML_RPC)

    @cached_property
    def is_available_in_json_rpc(self):
        return check_flags_compatibility(self.protocol, Protocol.JSON_RPC)

    @cached_property
    def text_doc(self) -> str:
        """Method docstring, as raw text"""
        return self.docstring_parser.docstring

    @cached_property
    def html_doc(self) -> str:
        """Convert the text part of the docstring to an HTML representation, using the parser set in settings"""
        if not self.text_doc:
            return ""

        if settings.MODERNRPC_DOC_FORMAT.lower() in ("rst", "restructured", "restructuredtext"):
            docutils = importlib.import_module("docutils.core")
            return docutils.publish_parts(self.text_doc, writer_name="html")["body"]

        if settings.MODERNRPC_DOC_FORMAT.lower() in ("md", "markdown"):
            markdown_module = importlib.import_module("markdown")
            return markdown_module.markdown(self.text_doc)

        html_content = self.text_doc.replace("\n\n", "</p><p>").replace("\n", " ")
        return f"<p>{html_content}</p>"

    @cached_property
    def arguments_names(self) -> list[str]:
        """
        List of arguments of the wrapped function.

        If you need to access the documentation for each argument, use the `arguments` property instead.
        """
        return [arg for arg in self.introspector.signature.parameters if arg != self.context_target]

    @cached_property
    def arguments(self) -> OrderedDict[str, ProcedureArgDocs]:
        result: defaultdict[str, ProcedureArgDocs] = defaultdict(ProcedureArgDocs)
        for param in self.arguments_names:
            result[param].doc_type = self.docstring_parser.args_types.get(param, "")
            result[param].docstring = self.docstring_parser.args_docstrings.get(param, "")
            result[param].type_hint = self.introspector.get_arg_type_hint(param)

        return OrderedDict(result)

    @cached_property
    def returns(self) -> ProcedureArgDocs:
        return ProcedureArgDocs(
            docstring=self.docstring_parser.return_doc,
            doc_type=self.docstring_parser.return_type,
            type_hint=self.introspector.get_return_type_hint(),
        )
