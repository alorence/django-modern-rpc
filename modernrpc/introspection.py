"""Handle all introspection-related features on rpc_methods:
- Help text
- Signature
"""

from __future__ import annotations

import importlib
import inspect
import re
from typing import Callable

from django.utils.functional import cached_property

from modernrpc.config import settings

# Define regular expressions used to parse docstring
PARAM_REXP = re.compile(r"^[:@]param (\w+): ?(.*(?:\n[^:@].+)?)$", flags=re.MULTILINE)
RETURN_REXP = re.compile(r"^[:@]return: ?(.*(?:\n[^:@].+)?)$", flags=re.MULTILINE)

PARAM_TYPE_REXP = re.compile(r"^[:@]type (\w+): ?(.*)$", flags=re.MULTILINE)
RETURN_TYPE_REXP = re.compile(r"^[:@]rtype ?: ?(.*)$", flags=re.MULTILINE)

MULTI_SPACES = re.compile(r"\s+")


class Introspector:
    """Helper to extract the signature and type hint for the given function"""

    def __init__(self, function: Callable):
        self.func = function

    @cached_property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

    @cached_property
    def accept_kwargs(self) -> bool:
        """Determine if function signature contains **kwargs special argument"""
        if self.signature.parameters:
            last_param = next(reversed(list(self.signature.parameters.values())))
            return last_param.kind == inspect.Parameter.VAR_KEYWORD
        return False

    @cached_property
    def args(self) -> list[str]:
        """List all function arguments"""
        args = list(self.signature.parameters.keys())
        if self.accept_kwargs:
            return args[:-1]
        return args

    @cached_property
    def return_type(self) -> str:
        """Return the return type as defined from the signature typehint"""
        return (
            ""
            if self.signature.return_annotation == self.signature.empty
            else getattr(
                self.signature.return_annotation,
                "__name__",
                str(self.signature.return_annotation),
            )
        )

    @cached_property
    def args_types(self) -> dict[str, str]:
        if not self.signature.parameters:
            return {}
        return {
            name: getattr(param.annotation, "__name__", str(param.annotation))
            for name, param in self.signature.parameters.items()
            if param.annotation != param.empty
        }


class DocstringParser:
    """Parse docstring to extract documentation (type and text) for parameters and return. It also converts
    the docstring text part to an HTML representation using Markdown or Restructured parser (depending on settings)
    """

    def __init__(self, function: Callable):
        self.func = function

    @cached_property
    def raw_docstring(self) -> str:
        """Return full content of function docstring, as extracted by inspect.getdoc()"""
        return inspect.getdoc(self.func) or ""

    @staticmethod
    def cleanup_spaces(subject: str) -> str:
        """Basically, replaces any number of consecutive space chars (space, newline, tab, etc.) to a single space"""
        return MULTI_SPACES.sub(" ", subject)

    @cached_property
    def text_documentation(self) -> str:
        """Return the text part of the docstring block, excluding legacy typehints, parameters and return docs"""
        content = self.raw_docstring
        for pattern in [PARAM_REXP, PARAM_TYPE_REXP, RETURN_REXP, RETURN_TYPE_REXP]:
            content = pattern.sub("", content)
        return content.strip()

    @cached_property
    def html_documentation(self) -> str:
        """Convert the text part of the docstring to an HTML representation, using the parser set in settings"""
        if not self.text_documentation:
            return ""

        if settings.MODERNRPC_DOC_FORMAT.lower() in ("rst", "restructured", "restructuredtext"):
            docutils = importlib.import_module("docutils.core")
            return docutils.publish_parts(self.text_documentation, writer_name="html")["body"]

        if settings.MODERNRPC_DOC_FORMAT.lower() in ("md", "markdown"):
            markdown_module = importlib.import_module("markdown")
            return markdown_module.markdown(self.text_documentation)

        html_content = self.text_documentation.replace("\n\n", "</p><p>").replace("\n", " ")
        return f"<p>{html_content}</p>"

    @cached_property
    def args_doc(self) -> dict[str, str]:
        """Return a dict with, for each argument, its name as key and documentation text as value. The dict
        will contain only documented arguments.
        Basically this method parses and extracts reST documented arguments:

            :param <argname>: Documentation for <argname>

        Alternatively, it also supports the @param format:

            @param <argname>: Documentation for <argname>
        """
        return {param: self.cleanup_spaces(text) for param, text in PARAM_REXP.findall(self.raw_docstring)}

    @cached_property
    def args_types(self) -> dict[str, str]:
        """Return a dict with, for each argument, its name as key and documented type as value. The dict
        will contain only documented arguments.
        Basically this method parses and extracts reST doctype documentation:

            :type <argname>: int or str

        Alternatively, it also supports the @type format:

            @type <argname>: int or str
        """
        return dict(PARAM_TYPE_REXP.findall(self.raw_docstring))

    @cached_property
    def return_doc(self) -> str:
        """Return the documentation for method return value, as found in docstring:

            :return: Documentation on return value

        Alternatively, it also supports @return format:

            @return: Documentation on return value

        Return an empty string if return documentation is not found
        """
        res = RETURN_REXP.search(self.raw_docstring)
        return self.cleanup_spaces(res.group(1)) if res else ""

    @cached_property
    def return_type(self) -> str:
        """Return the documentation for the method return type, as found in docstring:

            :rtype: list

        Alternatively, it also supports the @rtype format:

            @rtype: list

        Return an empty string if return type information is not found
        """
        res = RETURN_TYPE_REXP.search(self.raw_docstring)
        return res.group(1) if res else ""
