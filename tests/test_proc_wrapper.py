import pytest

from modernrpc import Protocol, RpcRequestContext
from modernrpc.core import ProcedureArgDocs, ProcedureWrapper


class TestProcedureArgDocs:
    def test_type_hint_as_str(self):
        argz = ProcedureArgDocs(docstring="", doc_type="", type_hint=str)
        assert argz.type_hint_as_str == "str"

    def test_union_type_hint_as_str(self):
        argz = ProcedureArgDocs(docstring="", doc_type="", type_hint=int | str)
        assert argz.type_hint_as_str == "int | str"


class TestProtocolsAvailability:
    @pytest.fixture
    def dummy_procedure(self):
        def func(): ...

        return func

    def test_all_protocols(self, dummy_procedure):
        wrapper = ProcedureWrapper(dummy_procedure)

        assert wrapper.is_available_in_xml_rpc is True
        assert wrapper.is_available_in_json_rpc is True

    def test_xml_rpc_only(self, dummy_procedure):
        wrapper = ProcedureWrapper(dummy_procedure, protocol=Protocol.XML_RPC)

        assert wrapper.is_available_in_xml_rpc is True
        assert wrapper.is_available_in_json_rpc is False

    def test_json_rpc_only(self, dummy_procedure):
        wrapper = ProcedureWrapper(dummy_procedure, protocol=Protocol.JSON_RPC)

        assert wrapper.is_available_in_xml_rpc is False
        assert wrapper.is_available_in_json_rpc is True


class TestNoDocNoArgs:
    """Make sure docstring and introspection work as expected"""

    @pytest.fixture
    def wrapper(self):
        def dummy_procedure(): ...

        return ProcedureWrapper(dummy_procedure)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "dummy_procedure()"

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_type="", type_hint=None)


class TestSingleLineDocNoArgs:
    """Standard single-line docstring with various parsers"""

    @pytest.fixture
    def wrapper(self):
        def single_line_doc():
            """*italic*, **strong**, normal text"""

        return ProcedureWrapper(single_line_doc)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "single_line_doc()"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_type="", type_hint=None)

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == "*italic*, **strong**, normal text"

    def test_default_html_doc(self, wrapper):
        assert wrapper.html_doc == "<p>*italic*, **strong**, normal text</p>"

    def test_markdown_html_doc(self, settings, wrapper):
        settings.MODERNRPC_DOC_FORMAT = "md"
        assert wrapper.html_doc == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>"

    def test_rst_html_doc(self, settings, wrapper):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        assert wrapper.html_doc == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>\n"


class TestMultiLinesDocstringSimple:
    @pytest.fixture
    def wrapper(self):
        def multilines_docstring():
            """
            This method has multi-lines documentation.

            The content is indented when raw ``__doc__`` attribute function is read.
            The indentation should not interfere with semantic interpretation of the docstring.
            """

        return ProcedureWrapper(multilines_docstring)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "multilines_docstring()"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_type="", type_hint=None)

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == (
            "This method has multi-lines documentation.\n\n"
            "The content is indented when raw ``__doc__`` attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring."
        )

    def test_default_html_doc(self, wrapper):
        assert wrapper.html_doc == (
            "<p>This method has multi-lines documentation.</p>"
            "<p>The content is indented when raw ``__doc__`` attribute function is read. "
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_markdown_html_doc(self, settings, wrapper):
        settings.MODERNRPC_DOC_FORMAT = "md"
        assert wrapper.html_doc == (
            "<p>This method has multi-lines documentation.</p>\n"
            "<p>The content is indented when raw <code>__doc__</code> attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_rst_html_doc(self, settings, wrapper):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        assert wrapper.html_doc == (
            "<p>This method has multi-lines documentation.</p>\n"
            '<p>The content is indented when raw <tt class="docutils literal">__doc__</tt> attribute function is '
            "read.\nThe indentation should not interfere with semantic interpretation of the docstring.</p>\n"
        )


class TestMultiLinesDocstringWithBlock:
    """Standard multi-line docstring with an indented block"""

    @pytest.fixture
    def wrapper(self):
        def multilines_docstring_with_block():
            """
            This method has *multi-lines* **documentation**.

            Here is a quote block:

                abcdef 123456

            """

        return ProcedureWrapper(multilines_docstring_with_block)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "multilines_docstring_with_block()"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == []
        assert wrapper.arguments == {}

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_type="", type_hint=None)

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == (
            "This method has *multi-lines* **documentation**.\n\nHere is a quote block:\n\n    abcdef 123456"
        )

    def test_default_html_doc(self, wrapper):
        assert wrapper.html_doc == (
            "<p>This method has *multi-lines* **documentation**.</p>"
            "<p>Here is a quote block:</p>"
            "<p>    abcdef 123456</p>"
        )

    def test_markdown_html_doc(self, settings, wrapper):
        settings.MODERNRPC_DOC_FORMAT = "md"
        assert wrapper.html_doc == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<pre><code>abcdef 123456\n</code></pre>"
        )

    def test_rst_html_doc(self, settings, wrapper):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        assert wrapper.html_doc == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<blockquote>\nabcdef 123456</blockquote>\n"
        )


class TestMultilinesDocstringWithArgs:
    @pytest.fixture
    def wrapper(self):
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

        return ProcedureWrapper(multilines_docstring_with_args_and_doc)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "multilines_docstring_with_args_and_doc(one, two, three, four, five)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["one", "two", "three", "four", "five"]

        assert wrapper.arguments == {
            "one": ProcedureArgDocs(docstring="single line description", doc_type="", type_hint=None),
            "two": ProcedureArgDocs(docstring="", doc_type="", type_hint=None),
            "three": ProcedureArgDocs(
                docstring="description with long value on multiple lines", doc_type="", type_hint=None
            ),
            "four": ProcedureArgDocs(docstring="", doc_type="", type_hint=None),
            "five": ProcedureArgDocs(docstring="last param", doc_type="", type_hint=None),
        }

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="bar", doc_type="", type_hint=None)

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == (
            "Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena.\n"
            "musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?"
        )
        assert wrapper.html_doc == (
            "<p>Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena. "
            "musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?</p>"
        )


class TestNoDocstringWithArgs:
    @pytest.fixture
    def wrapper(self):
        def untyped_and_undocumented_args(a, b, c):
            pass

        return ProcedureWrapper(untyped_and_undocumented_args)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "untyped_and_undocumented_args(a, b, c)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["a", "b", "c"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="", doc_type="", type_hint=None),
            "b": ProcedureArgDocs(docstring="", doc_type="", type_hint=None),
            "c": ProcedureArgDocs(docstring="", doc_type="", type_hint=None),
        }

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_type="", type_hint=None)

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""


class TestArgsTypeHint:
    """Type hinting is correctly returned using the introspection module"""

    @pytest.fixture
    def wrapper(self):
        def typed_args(a: int, b: str, c: list | float) -> dict | list:
            return []

        return ProcedureWrapper(typed_args)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "typed_args(a, b, c)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["a", "b", "c"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="", doc_type="", type_hint=int),
            "b": ProcedureArgDocs(docstring="", doc_type="", type_hint=str),
            "c": ProcedureArgDocs(docstring="", doc_type="", type_hint=list | float),
        }

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_type="", type_hint=dict | list)

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""


class TestWithTypeHintAndDocstring:
    """Typehint + standard reStructuredText docstring"""

    @pytest.fixture
    def wrapper(self):
        def typehints_and_standard_docstring(a: str, b, c: float) -> float:
            """

            :param a: param A
            :param b: param B
            :param c: param C
            :return: A decimal value
            """
            return 1.33

        return ProcedureWrapper(typehints_and_standard_docstring)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "typehints_and_standard_docstring(a, b, c)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["a", "b", "c"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="param A", doc_type="", type_hint=str),
            "b": ProcedureArgDocs(docstring="param B", doc_type="", type_hint=None),
            "c": ProcedureArgDocs(docstring="param C", doc_type="", type_hint=float),
        }

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="A decimal value", doc_type="", type_hint=float)

    def test_docstring(self, wrapper):
        assert wrapper.text_doc == ""
        assert wrapper.html_doc == ""


class TestWithDocstringOnlyFunction:
    """No typehint but everything in reStructuredText docstring"""

    @pytest.fixture
    def wrapper(self):
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

        return ProcedureWrapper(args_and_types_docstring)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "args_and_types_docstring(name, birthdate, sex)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["name", "birthdate", "sex"]
        assert wrapper.arguments == {
            "name": ProcedureArgDocs(docstring="A name", doc_type="str", type_hint=None),
            "birthdate": ProcedureArgDocs(docstring="A birthdate", doc_type="datetime.datetime", type_hint=None),
            "sex": ProcedureArgDocs(docstring="Male or Female", doc_type="str", type_hint=None),
        }

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(
            docstring="A string representation of given arguments", doc_type="", type_hint=None
        )

    def test_default_html_doc_doc(self, wrapper):
        assert wrapper.text_doc == "This is the textual doc of the method"
        assert wrapper.html_doc == "<p>This is the textual doc of the method</p>"


class TestWithTypeHintAndDocstringTypes:
    """Legacy standard docstring must override typehint"""

    @pytest.fixture
    def wrapper(self):
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
            return {}

        return ProcedureWrapper(typehints_and_types_docstring)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "typehints_and_types_docstring(x, y)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["x", "y"]
        assert wrapper.arguments == {
            "x": ProcedureArgDocs(docstring="abcd", doc_type="float", type_hint=list),
            "y": ProcedureArgDocs(docstring="xyz", doc_type="int", type_hint=str),
        }

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="efgh", doc_type="str", type_hint=dict)

    def test_default_html_doc(self, wrapper):
        assert wrapper.text_doc == (
            "This is the docstring part of the function\n\nIt also contains a multi-line description"
        )
        assert wrapper.html_doc == (
            "<p>This is the docstring part of the function</p><p>It also contains a multi-line description</p>"
        )


class TestWithTypeHintAndKwargs:
    """Legacy standard docstring must override typehint"""

    @pytest.fixture
    def wrapper(self):
        def with_kwargs(x: list, y: str, **kwargs) -> str:
            """This is the docstring part of the function"""
            return "abcdefgh"

        return ProcedureWrapper(with_kwargs)

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "with_kwargs(x, y, kwargs)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["x", "y", "kwargs"]
        assert wrapper.arguments == {
            "x": ProcedureArgDocs(docstring="", doc_type="", type_hint=list),
            "y": ProcedureArgDocs(docstring="", doc_type="", type_hint=str),
            "kwargs": ProcedureArgDocs(docstring="", doc_type="", type_hint=None),
        }

    def test_returns(self, wrapper):
        assert wrapper.returns == ProcedureArgDocs(docstring="", doc_type="", type_hint=str)

    def test_default_html_doc(self, wrapper):
        assert wrapper.text_doc == "This is the docstring part of the function"
        assert wrapper.html_doc == "<p>This is the docstring part of the function</p>"


class TestContextTarget:
    @pytest.fixture
    def wrapper(self):
        def dummy_with_ctx_target(a: int, b: str, context: RpcRequestContext): ...

        return ProcedureWrapper(dummy_with_ctx_target, context_target="context")

    def test_str_repr(self, wrapper):
        assert str(wrapper) == "dummy_with_ctx_target(a, b)"

    def test_arguments(self, wrapper):
        assert wrapper.arguments_names == ["a", "b"]
        assert wrapper.arguments == {
            "a": ProcedureArgDocs(docstring="", doc_type="", type_hint=int),
            "b": ProcedureArgDocs(docstring="", doc_type="", type_hint=str),
        }
