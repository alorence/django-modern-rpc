from textwrap import dedent
from unittest.mock import Mock

import pytest

from modernrpc import RpcRequestContext
from modernrpc.constants import NOT_SET
from modernrpc.core import ProcedureWrapper
from modernrpc.introspection import DocstringParser, Introspector


def dummy(): ...


class TestProcedureAuth:
    @pytest.fixture
    def dummy_request(self, rf):
        return rf.post("/")

    def test_auth_not_set(self, dummy_request):
        wrapper = ProcedureWrapper(dummy)

        assert wrapper.auth is NOT_SET
        assert wrapper.check_permissions(dummy_request) is True

    def test_auth_none(self, dummy_request):
        wrapper = ProcedureWrapper(dummy, auth=None)

        assert wrapper.auth is None
        assert wrapper.check_permissions(dummy_request) is True

    @pytest.mark.parametrize(
        "auth_result",
        [
            object(),
            True,
            12345,
            "john.doe",
        ],
    )
    def test_single_auth_returns_ok(self, dummy_request, auth_result):
        auth_callback = Mock(return_value=auth_result)

        wrapper = ProcedureWrapper(dummy, auth=auth_callback)

        assert wrapper.auth is auth_callback
        assert bool(wrapper.check_permissions(dummy_request)) is True
        assert wrapper.check_permissions(dummy_request) is auth_result

    @pytest.mark.parametrize(
        "auth_result",
        [
            False,
            None,
            0,
            "",
        ],
    )
    def test_single_auth_returns_ko(self, dummy_request, auth_result):
        auth_callback = Mock(return_value=auth_result)

        wrapper = ProcedureWrapper(dummy, auth=auth_callback)

        assert wrapper.auth is auth_callback
        assert bool(wrapper.check_permissions(dummy_request)) is False
        assert wrapper.check_permissions(dummy_request) is False

    def test_multiple_auth(self, rf):
        auth_callbacks = [Mock(), Mock()]

        wrapper = ProcedureWrapper(dummy, auth=auth_callbacks)
        assert wrapper.auth is auth_callbacks

    def test_multiple_auth_false_true(self, dummy_request):
        ok_result = object()
        auth_callbacks = [Mock(return_value=False), Mock(return_value=ok_result)]

        wrapper = ProcedureWrapper(dummy, auth=auth_callbacks)
        check_perms_result = wrapper.check_permissions(dummy_request)

        assert bool(check_perms_result) is True
        assert check_perms_result is ok_result

        auth_callbacks[0].assert_called_once()
        auth_callbacks[1].assert_called_once()

    def test_multiple_auth_true_false(self, dummy_request):
        ok_result = object()
        auth_callbacks = [Mock(return_value=ok_result), Mock(return_value=False)]

        wrapper = ProcedureWrapper(dummy, auth=auth_callbacks)
        check_perms_result = wrapper.check_permissions(dummy_request)

        assert bool(check_perms_result) is True
        assert check_perms_result is ok_result

        auth_callbacks[0].assert_called_once()
        auth_callbacks[1].assert_not_called()


def no_doc(): ...


class TestNoDoc:
    """Make sure docstring and introspection works as expected"""

    def test_docstring_parser_docs(self):
        parser = DocstringParser(no_doc)
        assert parser.raw_docstring == ""
        assert parser.text_documentation == ""
        assert parser.html_documentation == ""

    def test_docstring_parser_signature(self):
        parser = DocstringParser(no_doc)
        assert parser.args_doc == {}
        assert parser.args_types == {}
        assert parser.return_doc == ""
        assert parser.return_type == ""

    def test_introspector(self):
        intros = Introspector(no_doc)
        assert intros.args == []
        assert intros.args_types == {}
        assert intros.return_type == ""
        assert intros.accept_kwargs is False

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(no_doc)
        assert wrapper.raw_docstring == ""
        assert wrapper.html_doc == ""

    def test_wrapper_signature(self):
        wrapper = ProcedureWrapper(no_doc)
        assert wrapper.args == []
        assert wrapper.args_doc == {}
        assert wrapper.return_doc == {"type": "", "text": ""}


def single_line_doc():
    """*italic*, **strong**, normal text"""


class TestSingleLineDoc:
    """Standard single-line docstring with various parsers"""

    def test_docstring_parser_default_doc(self):
        parser = DocstringParser(single_line_doc)
        assert parser.text_documentation == "*italic*, **strong**, normal text"
        assert parser.html_documentation == "<p>*italic*, **strong**, normal text</p>"

    def test_markdown_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        parser = DocstringParser(single_line_doc)
        assert parser.html_documentation == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>"

    def test_rst_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        parser = DocstringParser(single_line_doc)
        assert parser.html_documentation == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>\n"

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(single_line_doc)
        assert wrapper.raw_docstring == "*italic*, **strong**, normal text"
        assert wrapper.html_doc == "<p>*italic*, **strong**, normal text</p>"


def multiline_docstring_simple():
    """
    This method has multi-lines documentation.

    The content is indented when raw ``__doc__`` attribute function is read.
    The indentation should not interfere with semantic interpretation of the docstring.
    """


class TestMultiLinesDocstringSimple:
    def test_docstring_parser_default_doc(self):
        parser = DocstringParser(multiline_docstring_simple)
        assert parser.text_documentation == (
            "This method has multi-lines documentation.\n\n"
            "The content is indented when raw ``__doc__`` attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring."
        )
        assert parser.html_documentation == (
            "<p>This method has multi-lines documentation.</p>"
            "<p>The content is indented when raw ``__doc__`` attribute function is read. "
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_markdown_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        parser = DocstringParser(multiline_docstring_simple)
        assert parser.html_documentation == (
            "<p>This method has multi-lines documentation.</p>\n"
            "<p>The content is indented when raw <code>__doc__</code> attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_rst_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        parser = DocstringParser(multiline_docstring_simple)
        assert parser.html_documentation == (
            "<p>This method has multi-lines documentation.</p>\n"
            '<p>The content is indented when raw <tt class="docutils literal">__doc__</tt> attribute function is '
            "read.\nThe indentation should not interfere with semantic interpretation of the docstring.</p>\n"
        )

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(multiline_docstring_simple)
        assert wrapper.raw_docstring == (
            "This method has multi-lines documentation.\n\n"
            "The content is indented when raw ``__doc__`` attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring."
        )
        assert wrapper.html_doc == (
            "<p>This method has multi-lines documentation.</p>"
            "<p>The content is indented when raw ``__doc__`` attribute function is read. "
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )


def multiline_docstring_with_block():
    """
    This method has *multi-lines* **documentation**.

    Here is a quote block:

        abcdef 123456

    """


class TestMultiLinesDocstringWithBlock:
    """Standard multi-line docstring with an indented block"""

    def test_docstring_parser_default_doc(self):
        parser = DocstringParser(multiline_docstring_with_block)

        assert parser.text_documentation == (
            "This method has *multi-lines* **documentation**.\n\nHere is a quote block:\n\n    abcdef 123456"
        )
        assert parser.html_documentation == (
            "<p>This method has *multi-lines* **documentation**.</p>"
            "<p>Here is a quote block:</p>"
            "<p>    abcdef 123456</p>"
        )

    def test_markdown_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        parser = DocstringParser(multiline_docstring_with_block)
        assert parser.html_documentation == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<pre><code>abcdef 123456\n</code></pre>"
        )

    def test_rst_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        parser = DocstringParser(multiline_docstring_with_block)
        assert parser.html_documentation == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<blockquote>\nabcdef 123456</blockquote>\n"
        )

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(multiline_docstring_with_block)
        assert wrapper.raw_docstring == (
            "This method has *multi-lines* **documentation**.\n\nHere is a quote block:\n\n    abcdef 123456"
        )
        assert wrapper.html_doc == (
            "<p>This method has *multi-lines* **documentation**.</p>"
            "<p>Here is a quote block:</p>"
            "<p>    abcdef 123456</p>"
        )


def multiline_docstring_with_args_doc():
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


class TestMultilineDocstringWithArgs:
    def test_docstring_parser_raw(self):
        expected = """
            Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena.
            musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?
            :param one: single line description
            :param two:
            :param three: description with long value
              on multiple lines
            :param four:
            :param five: last param
            :return: bar
        """
        parser = DocstringParser(multiline_docstring_with_args_doc)
        assert parser.raw_docstring == dedent(expected).strip()

    def test_docstring_parser_default_doc(self):
        parser = DocstringParser(multiline_docstring_with_args_doc)

        assert parser.text_documentation == (
            "Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena.\n"
            "musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?"
        )

    def test_docstring_parser_signature(self):
        parser = DocstringParser(multiline_docstring_with_args_doc)

        assert parser.args_doc["one"] == "single line description"
        assert parser.args_doc["two"] == ""
        assert parser.args_doc["three"] == "description with long value on multiple lines"
        assert parser.args_doc["four"] == ""
        assert parser.args_doc["five"] == "last param"
        assert parser.args_types == {}

    def test_introspector(self):
        intros = Introspector(multiline_docstring_with_args_doc)
        assert intros.args == []
        assert intros.args_types == {}
        assert intros.return_type == ""
        assert intros.accept_kwargs is False

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(multiline_docstring_with_args_doc)
        assert wrapper.raw_docstring == (
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
    def test_extracted_docstring(self):
        parser = DocstringParser(untyped_and_undocumented_args)
        assert parser.raw_docstring == ""
        assert parser.text_documentation == ""
        assert parser.html_documentation == ""

    def test_extracted_args_doc(self):
        parser = DocstringParser(untyped_and_undocumented_args)
        assert parser.args_doc == {}
        assert parser.args_types == {}

    def test_introspector(self):
        intros = Introspector(untyped_and_undocumented_args)
        assert intros.args == ["a", "b", "c"]
        assert intros.args_types == {}
        assert intros.return_type == ""
        assert not intros.accept_kwargs

    def test_args_and_return(self):
        wrapper = ProcedureWrapper(untyped_and_undocumented_args)
        assert wrapper.args == ["a", "b", "c"]
        assert wrapper.args_doc == {
            "a": {"type": "", "text": ""},
            "b": {"type": "", "text": ""},
            "c": {"type": "", "text": ""},
        }
        assert wrapper.return_doc == {"type": "", "text": ""}

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(untyped_and_undocumented_args)
        assert wrapper.raw_docstring == ""
        assert wrapper.html_doc == ""


def typed_args(a: int, b: str, c: list) -> dict:
    pass


class TestArgsTypeHint:
    """Type hinting is correctly returned using introspection module"""

    def test_extracted_docstring(self):
        parser = DocstringParser(typed_args)
        assert parser.raw_docstring == ""
        assert parser.text_documentation == ""
        assert parser.html_documentation == ""

    def test_extracted_args_doc(self):
        parser = DocstringParser(typed_args)
        assert parser.args_doc == {}
        assert parser.args_types == {}

    def test_introspector(self):
        intros = Introspector(typed_args)
        assert intros.args == ["a", "b", "c"]
        assert intros.args_types == {
            "a": "int",
            "b": "str",
            "c": "list",
        }
        assert intros.return_type == "dict"
        assert intros.accept_kwargs is False

    def test_wrapper_args_and_return(self):
        wrapper = ProcedureWrapper(typed_args)
        assert wrapper.args == ["a", "b", "c"]
        assert wrapper.args_doc == {
            "a": {"type": "int", "text": ""},
            "b": {"type": "str", "text": ""},
            "c": {"type": "list", "text": ""},
        }
        assert wrapper.return_doc == {"type": "dict", "text": ""}

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(typed_args)
        assert wrapper.raw_docstring == ""
        assert wrapper.html_doc == ""


def typehints_and_standard_docstring(a: str, b: dict, c: float) -> float:
    """

    :param a: param A
    :param b: param B
    :param c: param C
    :return: A decimal value
    """


class TestWithTypeHintAndDocstring:
    """Typehint + standard reStructuredText docstring"""

    def test_extracted_docstring(self):
        parser = DocstringParser(typed_args)
        assert parser.raw_docstring == ""
        assert parser.text_documentation == ""
        assert parser.html_documentation == ""

    def test_extracted_args_doc(self):
        parser = DocstringParser(typed_args)
        assert parser.args_doc == {}
        assert parser.args_types == {}

    def test_introspector(self):
        intros = Introspector(typed_args)
        assert intros.args == ["a", "b", "c"]
        assert intros.args_types == {
            "a": "int",
            "b": "str",
            "c": "list",
        }
        assert intros.accept_kwargs is False

    def test_wrapper_args_and_return(self):
        wrapper = ProcedureWrapper(typehints_and_standard_docstring)
        assert wrapper.args == ["a", "b", "c"]
        assert wrapper.args_doc == {
            "a": {"type": "str", "text": "param A"},
            "b": {"type": "dict", "text": "param B"},
            "c": {"type": "float", "text": "param C"},
        }
        assert wrapper.return_doc == {"type": "float", "text": "A decimal value"}

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(typehints_and_standard_docstring)
        assert wrapper.raw_docstring == ""
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

    def test_extracted_args_doc(self):
        parser = DocstringParser(args_and_types_docstring)
        assert parser.args_doc == {"name": "A name", "birthdate": "A birthdate", "sex": "Male or Female"}
        assert parser.args_types == {"birthdate": "datetime.datetime", "name": "str", "sex": "str"}

    def test_introspector(self):
        intros = Introspector(args_and_types_docstring)
        assert intros.args == ["name", "birthdate", "sex"]
        assert intros.args_types == {}
        assert intros.return_type == ""
        assert intros.accept_kwargs is False

    def test_args_and_return(self):
        wrapper = ProcedureWrapper(args_and_types_docstring)

        assert wrapper.args == ["name", "birthdate", "sex"]
        assert wrapper.args_doc == {
            "name": {"type": "str", "text": "A name"},
            "birthdate": {"type": "datetime.datetime", "text": "A birthdate"},
            "sex": {"type": "str", "text": "Male or Female"},
        }
        assert wrapper.return_doc == {
            "type": "",
            "text": "A string representation of given arguments",
        }

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(args_and_types_docstring)
        assert wrapper.raw_docstring == "This is the textual doc of the method"
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

    def test_extracted_args_doc(self):
        parser = DocstringParser(typehints_and_types_docstring)
        assert parser.args_doc == {"x": "abcd", "y": "xyz"}
        assert parser.args_types == {"x": "float", "y": "int"}

    def test_introspector(self):
        intros = Introspector(typehints_and_types_docstring)
        assert intros.args == ["x", "y"]
        assert intros.args_types == {"x": "list", "y": "str"}
        assert intros.return_type == "dict"
        assert intros.accept_kwargs is False

    def test_args_and_return(self):
        wrapper = ProcedureWrapper(typehints_and_types_docstring)

        assert wrapper.args == ["x", "y"]
        assert wrapper.args_doc == {
            "x": {"type": "list", "text": "abcd"},
            "y": {"type": "str", "text": "xyz"},
        }
        assert wrapper.return_doc == {"type": "dict", "text": "efgh"}

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(typehints_and_types_docstring)

        assert wrapper.raw_docstring == (
            "This is the docstring part of the function\n\nIt also contains a multi-line description"
        )
        assert wrapper.html_doc == (
            "<p>This is the docstring part of the function</p><p>It also contains a multi-line description</p>"
        )


def with_kwargs(x: list, y: str, **kwargs) -> dict:
    """This is the docstring part of the function"""


class TestWithTypeHintAndKwargs:
    """Legacy standard docstring must override typehint"""

    def test_extracted_args_doc(self):
        parser = DocstringParser(with_kwargs)
        assert parser.args_doc == {}
        assert parser.args_types == {}

    def test_introspector(self):
        intros = Introspector(with_kwargs)
        assert intros.args == ["x", "y"]
        assert intros.args_types == {"x": "list", "y": "str"}
        assert intros.return_type == "dict"
        assert intros.accept_kwargs is True

    def test_args_and_return(self):
        wrapper = ProcedureWrapper(with_kwargs)

        assert wrapper.args == ["x", "y"]
        assert wrapper.args_doc == {
            "x": {"type": "list", "text": ""},
            "y": {"type": "str", "text": ""},
        }
        assert wrapper.return_doc == {"type": "dict", "text": ""}

    def test_wrapper_doc(self):
        wrapper = ProcedureWrapper(with_kwargs)

        assert wrapper.raw_docstring == "This is the docstring part of the function"
        assert wrapper.html_doc == "<p>This is the docstring part of the function</p>"


def dummy_with_ctx_target(a: int, b: str, context: RpcRequestContext): ...


class TestContextTarget:
    def test_context_target(self):
        wrapper = ProcedureWrapper(dummy_with_ctx_target, context_target="context")
        assert wrapper.args == ["a", "b"]
        assert wrapper.args_doc == {
            "a": {"type": "int", "text": ""},
            "b": {"type": "str", "text": ""},
        }
