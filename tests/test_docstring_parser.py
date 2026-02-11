import pytest

from modernrpc.introspection import DocstringParser


class TestEmptyAndPlainText:
    @pytest.fixture
    def parser(self):
        def func():
            pass

        return DocstringParser(func)

    def test_docstring(self, parser):
        assert parser.docstring == ""

    def test_args_docs(self, parser):
        assert parser.args_docstrings == {}
        assert parser.args_types == {}

    def test_returns_docs(self, parser):
        assert parser.return_doc == ""
        assert parser.return_type == ""


class TestSimpleDocstring:
    @pytest.fixture
    def parser(self):
        def func():
            """
            A brief description line.

            Additional details should remain in the parsed docstring while any
            parameter/return legacy annotations are stripped.
            """

        return DocstringParser(func)

    def test_docstring(self, parser):
        assert parser.docstring == (
            "A brief description line.\n\nAdditional details should remain in the parsed docstring "
            "while any\nparameter/return legacy annotations are stripped."
        )

    def test_args_docs(self, parser):
        assert parser.args_docstrings == {}
        assert parser.args_types == {}

    def test_returns_docs(self, parser):
        assert parser.return_doc == ""
        assert parser.return_type == ""


class TestParamAndReturnParsing:
    @pytest.fixture
    def parser(self):
        def func():
            """
            Function with params in reST style.

            :param x: the first value
            :param y: the second value with
                a continuation line that should be glued
                with single spaces
            :type x: int
            :type y: str
            :return: sum of values
            :rtype: int
            """

        return DocstringParser(func)

    def test_docstring(self, parser):
        assert parser.docstring == "Function with params in reST style."

    def test_args_docs(self, parser):
        assert parser.args_docstrings == {
            "x": "the first value",
            "y": "the second value with a continuation line that should be glued with single spaces",
        }
        assert parser.args_types == {"x": "int", "y": "str"}

    def test_returns_docs(self, parser):
        assert parser.return_doc == "sum of values"
        assert parser.return_type == "int"


class TestDocstringStripsMeta:
    @pytest.fixture
    def parser(self):
        def func():
            """
            Function with params in @ style.

            @param a: alpha
            @param b: beta with
              line wrap
            @type a: float
            @type b: list[str]
            @return: something
            @rtype: dict
            """

        return DocstringParser(func)

    def test_docstring(self, parser):
        assert parser.docstring == "Function with params in @ style."

    def test_args_docs(self, parser):
        assert parser.args_docstrings == {
            "a": "alpha",
            "b": "beta with line wrap",
        }
        assert parser.args_types == {"a": "float", "b": "list[str]"}

    def test_returns_docs(self, parser):
        assert parser.return_doc == "something"
        assert parser.return_type == "dict"
