from __future__ import annotations

import sys

import pytest

from modernrpc import Protocol, RpcRequestContext
from modernrpc.core import ProcedureArgDocs, ProcedureWrapper


def dummy_procedure(): ...


class TestProtocolsAvailability:
    def test_all_protocols(self):
        wrapper = ProcedureWrapper(dummy_procedure)

        assert wrapper.is_available_in_xml_rpc is True
        assert wrapper.is_available_in_json_rpc is True

    def test_xml_rpc_only(self):
        wrapper = ProcedureWrapper(dummy_procedure, protocol=Protocol.XML_RPC)

        assert wrapper.is_available_in_xml_rpc is True
        assert wrapper.is_available_in_json_rpc is False

    def test_json_rpc_only(self):
        wrapper = ProcedureWrapper(dummy_procedure, protocol=Protocol.JSON_RPC)

        assert wrapper.is_available_in_xml_rpc is False
        assert wrapper.is_available_in_json_rpc is True


class TestNoDocNoArgs:
    """Make sure docstring and introspection work as expected"""

    def test_str_repr(self):
        wrapper = ProcedureWrapper(dummy_procedure)
        assert str(wrapper) == "dummy_procedure()"

    def test_docstring(self):
        wrapper = ProcedureWrapper(dummy_procedure)
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""

    def test_arguments(self):
        wrapper = ProcedureWrapper(dummy_procedure)
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self):
        wrapper = ProcedureWrapper(dummy_procedure)
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_types=[], annotations=())


def single_line_doc():
    """*italic*, **strong**, normal text"""


class TestSingleLineDocNoArgs:
    """Standard single-line docstring with various parsers"""

    def test_str_repr(self):
        wrapper = ProcedureWrapper(single_line_doc)
        assert str(wrapper) == "single_line_doc()"

    def test_arguments(self):
        wrapper = ProcedureWrapper(single_line_doc)
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self):
        wrapper = ProcedureWrapper(single_line_doc)
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_types=[], annotations=())

    def test_docstring(self):
        wrapper = ProcedureWrapper(single_line_doc)
        assert wrapper.text_doc == "*italic*, **strong**, normal text"

    def test_default_html_doc(self):
        wrapper = ProcedureWrapper(single_line_doc)
        assert wrapper.html_doc == "<p>*italic*, **strong**, normal text</p>"

    def test_markdown_html_doc(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        wrapper = ProcedureWrapper(single_line_doc)
        assert wrapper.html_doc == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>"

    def test_rst_html_doc(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        wrapper = ProcedureWrapper(single_line_doc)
        assert wrapper.html_doc == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>\n"


def multilines_docstring():
    """
    This method has multi-lines documentation.

    The content is indented when raw ``__doc__`` attribute function is read.
    The indentation should not interfere with semantic interpretation of the docstring.
    """


class TestMultiLinesDocstringSimple:
    def test_str_repr(self):
        wrapper = ProcedureWrapper(multilines_docstring)
        assert str(wrapper) == "multilines_docstring()"

    def test_arguments(self):
        wrapper = ProcedureWrapper(multilines_docstring)
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self):
        wrapper = ProcedureWrapper(multilines_docstring)
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_types=[], annotations=())

    def test_docstring(self):
        wrapper = ProcedureWrapper(multilines_docstring)
        assert wrapper.text_doc == (
            "This method has multi-lines documentation.\n\n"
            "The content is indented when raw ``__doc__`` attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring."
        )

    def test_default_html_doc(self):
        wrapper = ProcedureWrapper(multilines_docstring)
        assert wrapper.html_doc == (
            "<p>This method has multi-lines documentation.</p>"
            "<p>The content is indented when raw ``__doc__`` attribute function is read. "
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_markdown_html_doc(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        wrapper = ProcedureWrapper(multilines_docstring)
        assert wrapper.html_doc == (
            "<p>This method has multi-lines documentation.</p>\n"
            "<p>The content is indented when raw <code>__doc__</code> attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_rst_html_doc(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        wrapper = ProcedureWrapper(multilines_docstring)
        assert wrapper.html_doc == (
            "<p>This method has multi-lines documentation.</p>\n"
            '<p>The content is indented when raw <tt class="docutils literal">__doc__</tt> attribute function is '
            "read.\nThe indentation should not interfere with semantic interpretation of the docstring.</p>\n"
        )


def multilines_docstring_with_block():
    """
    This method has *multi-lines* **documentation**.

    Here is a quote block:

        abcdef 123456

    """


class TestMultiLinesDocstringWithBlock:
    """Standard multi-line docstring with an indented block"""

    def test_str_repr(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_block)
        assert str(wrapper) == "multilines_docstring_with_block()"

    def test_arguments(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_block)
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_block)
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_types=[], annotations=())

    def test_docstring(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_block)
        assert wrapper.text_doc == (
            "This method has *multi-lines* **documentation**.\n\nHere is a quote block:\n\n    abcdef 123456"
        )

    def test_default_html_doc(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_block)
        assert wrapper.html_doc == (
            "<p>This method has *multi-lines* **documentation**.</p>"
            "<p>Here is a quote block:</p>"
            "<p>    abcdef 123456</p>"
        )

    def test_markdown_html_doc(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        wrapper = ProcedureWrapper(multilines_docstring_with_block)
        assert wrapper.html_doc == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<pre><code>abcdef 123456\n</code></pre>"
        )

    def test_rst_html_doc(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        wrapper = ProcedureWrapper(multilines_docstring_with_block)
        assert wrapper.html_doc == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<blockquote>\nabcdef 123456</blockquote>\n"
        )


def multilines_docstring_with_args_and_doc(one, two, three, four, five):
    """Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena.
    musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?
    :param one: single line description
    :param two:
    :param three: description with long value
      on multiple lines
    :param four:
    :param five: last param
    :return: bar
    """


class TestMultilinesDocstringWithArgs:
    def test_str_repr(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_args_and_doc)
        assert str(wrapper) == "multilines_docstring_with_args_and_doc(one, two, three, four, five)"

    def test_arguments(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_args_and_doc)
        assert wrapper.arguments_names == ["one", "two", "three", "four", "five"]

        assert wrapper.arguments == {
            "one": ProcedureArgDocs(docstring="single line description", doc_types=[], annotations=()),
            "two": ProcedureArgDocs(docstring="", doc_types=[], annotations=()),
            "three": ProcedureArgDocs(
                docstring="description with long value on multiple lines", doc_types=[], annotations=()
            ),
            "four": ProcedureArgDocs(docstring="", doc_types=[], annotations=()),
            "five": ProcedureArgDocs(docstring="last param", doc_types=[], annotations=()),
        }

    def test_returns(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_args_and_doc)
        assert wrapper.returns == ProcedureArgDocs(docstring="bar", doc_types=[], annotations=())

    def test_docstring(self):
        wrapper = ProcedureWrapper(multilines_docstring_with_args_and_doc)
        assert wrapper.text_doc == (
            "Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena.\n"
            "musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?"
        )
        assert wrapper.html_doc == (
            "<p>Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena. "
            "musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?</p>"
        )


def untyped_and_undocumented_args(a, b, c):
    pass


class TestNoDocstringWithArgs:
    def test_str_repr(self):
        wrapper = ProcedureWrapper(untyped_and_undocumented_args)
        assert str(wrapper) == "untyped_and_undocumented_args(a, b, c)"

    def test_arguments(self):
        wrapper = ProcedureWrapper(untyped_and_undocumented_args)
        assert wrapper.arguments_names == ["a", "b", "c"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="", doc_types=[], annotations=()),
            "b": ProcedureArgDocs(docstring="", doc_types=[], annotations=()),
            "c": ProcedureArgDocs(docstring="", doc_types=[], annotations=()),
        }

    def test_returns(self):
        wrapper = ProcedureWrapper(untyped_and_undocumented_args)
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_types=[], annotations=())

    def test_docstring(self):
        wrapper = ProcedureWrapper(untyped_and_undocumented_args)
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""


def typed_args(a: int, b: str, c: list | float) -> dict | list:
    pass


class TestArgsTypeHint:
    """Type hinting is correctly returned using the introspection module"""

    @pytest.mark.xfail(
        sys.version_info < (3, 10),
        reason="New union type syntax is fully supported with Python 3.10+",
    )
    def test_str_repr(self):
        wrapper = ProcedureWrapper(typed_args)
        assert str(wrapper) == "typed_args(a, b, c)"

    @pytest.mark.xfail(
        sys.version_info < (3, 10),
        reason="New union type syntax is fully supported with Python 3.10+",
    )
    def test_arguments(self):
        wrapper = ProcedureWrapper(typed_args)
        assert wrapper.arguments_names == ["a", "b", "c"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="", doc_types=[], annotations=(int,)),
            "b": ProcedureArgDocs(docstring="", doc_types=[], annotations=(str,)),
            "c": ProcedureArgDocs(docstring="", doc_types=[], annotations=(list, float)),
        }

    @pytest.mark.xfail(
        sys.version_info < (3, 10),
        reason="New union type syntax is fully supported with Python 3.10+",
    )
    def test_returns(self):
        wrapper = ProcedureWrapper(typed_args)
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_types=[], annotations=(dict, list))

    def test_docstring(self):
        wrapper = ProcedureWrapper(typed_args)
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""


def typehints_and_standard_docstring(a: str, b, c: float) -> float:
    """

    :param a: param A
    :param b: param B
    :param c: param C
    :return: A decimal value
    """


class TestWithTypeHintAndDocstring:
    """Typehint + standard reStructuredText docstring"""

    def test_str_repr(self):
        wrapper = ProcedureWrapper(typehints_and_standard_docstring)
        assert str(wrapper) == "typehints_and_standard_docstring(a, b, c)"

    def test_arguments(self):
        wrapper = ProcedureWrapper(typehints_and_standard_docstring)
        assert wrapper.arguments_names == ["a", "b", "c"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="param A", doc_types=[], annotations=(str,)),
            "b": ProcedureArgDocs(docstring="param B", doc_types=[], annotations=()),
            "c": ProcedureArgDocs(docstring="param C", doc_types=[], annotations=(float,)),
        }

    def test_returns(self):
        wrapper = ProcedureWrapper(typehints_and_standard_docstring)
        assert wrapper.returns == ProcedureArgDocs(docstring="A decimal value", doc_types=[], annotations=(float,))

    def test_docstring(self):
        wrapper = ProcedureWrapper(typehints_and_standard_docstring)
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""


def args_and_types_docstring(name, birthdate, sex):
    """
    This is the textual doc of the method
    :param name: A name
    :param birthdate: A birthdate
    :param sex: Male or Female
    :type name: str
    :type birthdate: datetime.datetime
    :type sex: str
    :return: A string representation of given arguments
    """


class TestWithDocstringOnlyFunction:
    """No typehint but everything in reStructuredText docstring"""

    def test_str_repr(self):
        wrapper = ProcedureWrapper(args_and_types_docstring)
        assert str(wrapper) == "args_and_types_docstring(name, birthdate, sex)"

    def test_arguments(self):
        wrapper = ProcedureWrapper(args_and_types_docstring)
        assert wrapper.arguments_names == ["name", "birthdate", "sex"]
        assert wrapper.arguments == {
            "name": ProcedureArgDocs(docstring="A name", doc_types=["str"], annotations=()),
            "birthdate": ProcedureArgDocs(docstring="A birthdate", doc_types=["datetime.datetime"], annotations=()),
            "sex": ProcedureArgDocs(docstring="Male or Female", doc_types=["str"], annotations=()),
        }

    def test_returns(self):
        wrapper = ProcedureWrapper(args_and_types_docstring)
        assert wrapper.returns == ProcedureArgDocs(
            docstring="A string representation of given arguments", doc_types=[], annotations=()
        )

    def test_default_html_doc_doc(self):
        wrapper = ProcedureWrapper(args_and_types_docstring)
        assert wrapper.text_doc == "This is the textual doc of the method"
        assert wrapper.html_doc == "<p>This is the textual doc of the method</p>"


def typehints_and_types_docstring(x: list, y: str) -> dict:
    """This is the docstring part of the function

    It also contains a multi-line description
    :param x: abcd
    :param y: xyz
    :return: efgh
    :type x: float
    :type y: int
    :rtype: str
    """


class TestWithTypeHintAndDocstringTypes:
    """Legacy standard docstring must override typehint"""

    def test_str_repr(self):
        wrapper = ProcedureWrapper(typehints_and_types_docstring)
        assert str(wrapper) == "typehints_and_types_docstring(x, y)"

    def test_arguments(self):
        wrapper = ProcedureWrapper(typehints_and_types_docstring)
        assert wrapper.arguments_names == ["x", "y"]
        assert wrapper.arguments == {
            "x": ProcedureArgDocs(docstring="abcd", doc_types=["float"], annotations=(list,)),
            "y": ProcedureArgDocs(docstring="xyz", doc_types=["int"], annotations=(str,)),
        }

    def test_returns(self):
        wrapper = ProcedureWrapper(typehints_and_types_docstring)
        assert wrapper.returns == ProcedureArgDocs(docstring="efgh", doc_types=["str"], annotations=(dict,))

    def test_default_html_doc(self):
        wrapper = ProcedureWrapper(typehints_and_types_docstring)

        assert wrapper.text_doc == (
            "This is the docstring part of the function\n\nIt also contains a multi-line description"
        )
        assert wrapper.html_doc == (
            "<p>This is the docstring part of the function</p><p>It also contains a multi-line description</p>"
        )


def with_kwargs(x: list, y: str, **kwargs) -> dict:
    """This is the docstring part of the function"""


class TestWithTypeHintAndKwargs:
    """Legacy standard docstring must override typehint"""

    def test_str_repr(self):
        wrapper = ProcedureWrapper(with_kwargs)
        assert str(wrapper) == "with_kwargs(x, y, kwargs)"

    def test_arguments(self):
        wrapper = ProcedureWrapper(with_kwargs)
        assert wrapper.arguments_names == ["x", "y", "kwargs"]
        assert wrapper.arguments == {
            "x": ProcedureArgDocs(docstring="", doc_types=[], annotations=(list,)),
            "y": ProcedureArgDocs(docstring="", doc_types=[], annotations=(str,)),
            "kwargs": ProcedureArgDocs(docstring="", doc_types=[], annotations=()),
        }

    def test_returns(self):
        wrapper = ProcedureWrapper(with_kwargs)
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_types=[], annotations=(dict,))

    def test_default_html_doc(self):
        wrapper = ProcedureWrapper(with_kwargs)

        assert wrapper.text_doc == "This is the docstring part of the function"
        assert wrapper.html_doc == "<p>This is the docstring part of the function</p>"


def dummy_with_ctx_target(a: int, b: str, context: RpcRequestContext): ...


class TestContextTarget:
    def test_str_repr(self):
        wrapper = ProcedureWrapper(dummy_with_ctx_target, context_target="context")
        assert str(wrapper) == "dummy_with_ctx_target(a, b)"

    def test_arguments(self):
        wrapper = ProcedureWrapper(dummy_with_ctx_target, context_target="context")
        assert wrapper.arguments_names == ["a", "b"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="", doc_types=[], annotations=(int,)),
            "b": ProcedureArgDocs(docstring="", doc_types=[], annotations=(str,)),
        }
