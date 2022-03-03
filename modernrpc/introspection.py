"""Handle all introspection related features on rpc_methods:
- Help text
- Signature
"""
import inspect
import re
from typing import Callable, Dict, List

from django.utils.functional import cached_property

from modernrpc.conf import settings

# Define regular expressions used to parse docstring
PARAM_REXP = re.compile(r"^[:@]param (\w+):\s?(.*)$", flags=re.MULTILINE)
PARAM_TYPE_REXP = re.compile(r"^[:@]type (\w+):\s?(.*)$", flags=re.MULTILINE)
RETURN_REXP = re.compile(r"^[:@]return:\s?(.*)$", flags=re.MULTILINE)
RETURN_TYPE_REXP = re.compile(r"^[:@]rtype:\s?(.*)$", flags=re.MULTILINE)


class Introspector:
    """Helper to extract signature and type hint for given function"""

    def __init__(self, function: Callable):
        self.func = function

    @cached_property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

    @cached_property
    def accept_kwargs(self) -> bool:
        """Determine if function signature contains **kwargs special argument"""
        if self.signature.parameters:
            # Note: cast to list() is required by python 3.5 only, to allow use of reversed() helper
            last_param = next(reversed(list(self.signature.parameters)))
            return (
                self.signature.parameters[last_param].kind
                == inspect.Parameter.VAR_KEYWORD
            )
        return False

    @cached_property
    def args(self) -> List[str]:
        """List all function arguments"""
        return list(self.signature.parameters.keys())

    @cached_property
    def return_type(self) -> str:
        """Return the return type as defined from signature typehint"""
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
    def args_types(self) -> Dict[str, str]:
        if not self.signature.parameters:
            return {}
        return {
            name: getattr(param.annotation, "__name__", str(param.annotation))
            for name, param in self.signature.parameters.items()
            if param.annotation != param.empty
        }


class DocstringParser:
    """Parse docstring to extract params docs & types and return doc & type. It also converts
    long docstring part to an HTML representation using parser from settings (markdown/rst)"""

    def __init__(self, function: Callable):
        self.func = function

    @cached_property
    def full_docstring(self) -> str:
        """Return full content of function docstring, as extracted by inspect.getdoc()"""
        return inspect.getdoc(self.func) or ""

    @cached_property
    def raw_docstring(self) -> str:
        """Return the text part of the docstring block, excluding legacy typehints and parameters and return docs"""
        content = self.full_docstring
        for pattern in [PARAM_REXP, PARAM_TYPE_REXP, RETURN_REXP, RETURN_TYPE_REXP]:
            content = pattern.sub("", content)
        return content.strip()

    @cached_property
    def html_doc(self) -> str:
        """Convert the text part of the docstring to an HTML representation, using the parser set in settings"""
        if not self.raw_docstring:
            return ""

        if settings.MODERNRPC_DOC_FORMAT.lower() in (
            "rst",
            "restructred",
            "restructuredtext",
        ):
            from docutils.core import publish_parts

            return publish_parts(self.raw_docstring, writer_name="html")["body"]

        if settings.MODERNRPC_DOC_FORMAT.lower() in ("md", "markdown"):
            import markdown

            return markdown.markdown(self.raw_docstring)

        return "<p>{}</p>".format(
            self.raw_docstring.replace("\n\n", "</p><p>").replace("\n", " ")
        )

    @cached_property
    def args_doc(self) -> Dict[str, str]:
        """Return a dict with argument name as key and documentation as value. The dict will contain only
        documented arguments.
        Basically this method parse and extract reST documented arguments:

            :param <argname>: Documentation for <argname>

        Alternatively, it also supports @param format:

            @param <argname>: Documentation for <argname>
        """
        return dict(PARAM_REXP.findall(self.full_docstring))

    @cached_property
    def args_types(self) -> Dict[str, str]:
        """Return a dict with argument name as key and documented type as value. The dict will contain only
        documented arguments.
        Basically this method parse and extract reST doctype documentation:

            :type <argname>: int or str

        Alternatively, it also supports @type format:

            @type <argname>: int or str
        """
        return dict(PARAM_TYPE_REXP.findall(self.full_docstring))

    @cached_property
    def return_doc(self) -> str:
        """Return the documentation for method return value, as found in docstring:

            :return: Documentation on return value

        Alternatively, it also supports @return format:

            @return: Documentation on return value

        Return an empty string if return documentation is not found
        """
        res = RETURN_REXP.search(self.full_docstring)
        return res.group(1) if res else ""

    @cached_property
    def return_type(self) -> str:
        """Return the documentation for method return type, as found in docstring:

            :rtype: list

        Alternatively, it also supports @rtype format:

            @rtype: list

        Return an empty string if return type information is not found
        """
        res = RETURN_TYPE_REXP.search(self.full_docstring)
        return res.group(1) if res else ""
