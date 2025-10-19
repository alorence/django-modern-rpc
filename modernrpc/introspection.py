"""Handle all introspection-related features on rpc_methods:
- Help text
- Signature
"""

from __future__ import annotations

import inspect
import re
import typing
from typing import Callable

from django.utils.functional import cached_property


class Introspector:
    """Helper class to extract the signature of a callable and the type hint of its arguments & returns"""

    def __init__(self, function: Callable):
        self.func = function

    @cached_property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

    @cached_property
    def _func_type_hints(self) -> dict[str, type]:
        return typing.get_type_hints(self.func)

    def get_arg_type_hint(self, arg: str) -> type | None:
        return self._func_type_hints.get(arg)

    def get_return_type_hint(self) -> type | None:
        return self._func_type_hints.get("return")


class DocstringParser:
    """Helper class to parse the docstring of a callable and extract arguments and return docs & types."""

    MULTIPLE_SPACES = re.compile(r"\s+")

    PARAM_REXP = re.compile(r"^[:@]param (\w+): ?(.*(?:\n[^:@].+)*)$", flags=re.MULTILINE)
    RETURN_REXP = re.compile(r"^[:@]return: ?(.*(?:\n[^:@].+)*)$", flags=re.MULTILINE)

    PARAM_TYPE_REXP = re.compile(r"^[:@]type (\w+): ?(.*)$", flags=re.MULTILINE)
    RETURN_TYPE_REXP = re.compile(r"^[:@]rtype ?: ?(.*)$", flags=re.MULTILINE)

    def __init__(self, function: Callable):
        self.func = function

    @staticmethod
    def _cleanup_spaces(subject: str) -> str:
        """Basically, replaces any number of consecutive space chars (space, newline, tab, etc.) to a single space"""
        return DocstringParser.MULTIPLE_SPACES.sub(" ", subject)

    @cached_property
    def _full_docstring(self) -> str:
        """Return full content of function docstring, as extracted by inspect.getdoc()"""
        return inspect.getdoc(self.func) or ""

    @cached_property
    def docstring(self) -> str:
        """Return the text part of the docstring block, excluding legacy typehints, parameters and return docs"""
        content = self._full_docstring
        for pattern in [self.PARAM_REXP, self.PARAM_TYPE_REXP, self.RETURN_REXP, self.RETURN_TYPE_REXP]:
            content = pattern.sub("", content)
        return content.strip()

    @cached_property
    def args_docstrings(self) -> dict[str, str]:
        """Return a dict with, for each argument, its name as key and documentation text as value. The dict
        will contain only documented arguments.
        Basically this method parses and extracts reST documented arguments:

            :param <argname>: Documentation for <argname>

        Alternatively, it also supports the @param format:

            @param <argname>: Documentation for <argname>
        """
        return {param: self._cleanup_spaces(text) for param, text in self.PARAM_REXP.findall(self._full_docstring)}

    @cached_property
    def args_types(self) -> dict[str, str]:
        """Return a dict with, for each argument, its name as key and documented type as value. The dict
        will contain only documented arguments.
        Basically this method parses and extracts reST doctype documentation:

            :type <argname>: int or str

        Alternatively, it also supports the @type format:

            @type <argname>: int or str
        """
        return dict(self.PARAM_TYPE_REXP.findall(self._full_docstring))

    @cached_property
    def return_doc(self) -> str:
        """Return the documentation for method return value, as found in docstring:

            :return: Documentation on return value

        Alternatively, it also supports @return format:

            @return: Documentation on return value

        Return an empty string if return documentation is not found
        """
        res = self.RETURN_REXP.search(self._full_docstring)
        return self._cleanup_spaces(res.group(1)) if res else ""

    @cached_property
    def return_type(self) -> str:
        """Return the documentation for the method return type, as found in docstring:

            :rtype: list

        Alternatively, it also supports the @rtype format:

            @rtype: list

        Return an empty string if return type information is not found
        """
        res = self.RETURN_TYPE_REXP.search(self._full_docstring)
        return res.group(1) if res else ""
