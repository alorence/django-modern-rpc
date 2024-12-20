from textwrap import dedent

from modernrpc.introspection import DocstringParser, Introspector


def no_doc_no_args(): ...


class TestNoDocNoArgs:
    """Make sure docstring and introspection works as expected"""

    def test_docstring(self):
        parser = DocstringParser(no_doc_no_args)
        assert parser.raw_docstring == ""
        assert parser.text_documentation == ""
        assert parser.html_documentation == ""

    def test_docstring_args_and_return(self):
        parser = DocstringParser(no_doc_no_args)
        assert parser.args_doc == {}
        assert parser.args_types == {}
        assert parser.return_doc == ""
        assert parser.return_type == ""

    def test_introspector(self):
        intros = Introspector(no_doc_no_args)
        assert intros.args == []
        assert intros.args_types == {}
        assert not intros.accept_kwargs


def single_line_doc():
    """*italic*, **strong**, normal text"""


class TestSingleLineDoc:
    """Standard single-line docstring with various parsers"""

    def test_text_doc(self):
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


def multiline_docstring_simple():
    """
    This method has multi-lines documentation.

    The content is indented when raw ``__doc__`` attribute function is read.
    The indentation should not interfere with semantic interpretation of the docstring.
    """


class TestMultiLinesDocstringSimple:
    """Standard multi-line docstring"""

    def test_text_doc(self):
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


def multiline_docstring_with_block():
    """
    This method has *multi-lines* **documentation**.

    Here is a quote block:

        abcdef 123456

    """


class TestMultiLinesDocstringWithBlock:
    """Standard multi-line docstring with an indented block"""

    def test_text_doc(self):
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


def with_docstring():
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


class TestDocstringParser:
    def test_extracted_docstring(self):
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
        parser = DocstringParser(with_docstring)
        assert parser.raw_docstring == dedent(expected).strip()

    def test_extracted_documentation(self):
        parser = DocstringParser(with_docstring)

        assert parser.text_documentation == (
            "Lorem ipsum dolor sit amet. ferox, talis valebats nunquam reperire de alter, varius advena.\n"
            "musa camerarius sectam est. grandis, primus axonas hic transferre de neuter, barbatus pes?"
        )

    def test_extracted_args_doc(self):
        parser = DocstringParser(with_docstring)

        assert parser.args_doc["one"] == "single line description"
        assert parser.args_doc["two"] == ""
        assert parser.args_doc["three"] == "description with long value on multiple lines"
        assert parser.args_doc["four"] == ""
        assert parser.args_doc["five"] == "last param"
        assert parser.args_types == {}

    def test_introspector(self):
        intros = Introspector(with_docstring)
        assert intros.args == []
        assert intros.args_types == {}
        assert not intros.accept_kwargs


def no_doc_with_args(a, b, c):
    pass


class TestNoDocstringWithArgs:
    def test_extracted_docstring(self):
        parser = DocstringParser(no_doc_with_args)
        assert parser.raw_docstring == ""
        assert parser.text_documentation == ""
        assert parser.html_documentation == ""

    def test_extracted_args_doc(self):
        parser = DocstringParser(no_doc_with_args)
        assert parser.args_doc == {}
        assert parser.args_types == {}

    def test_introspector(self):
        intros = Introspector(no_doc_with_args)
        assert intros.args == ["a", "b", "c"]
        assert intros.args_types == {}
        assert not intros.accept_kwargs
