from modernrpc.conf import settings as modernrpc_settings
from modernrpc.core import Protocol, RPCMethod, rpc_method


def dummy_empty():
    pass


class TestRpcMethodEntryPointProtocol:
    """Check whether entry_points and protocol specifications works as expected when registering method"""

    def test_method_always_available(self):
        rpc_method(dummy_empty, "dummy_name")
        m = RPCMethod(dummy_empty)

        assert m.available_for_entry_point(
            modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
        )
        assert m.available_for_entry_point("random_entry_point")

        assert m.is_available_in_xml_rpc()
        assert m.is_available_in_json_rpc()

    def test_method_xmlrpc_only(self):
        rpc_method(dummy_empty, "dummy_name", protocol=Protocol.XML_RPC)
        m = RPCMethod(dummy_empty)

        assert m.is_available_in_xml_rpc()
        assert not m.is_available_in_json_rpc()

    def test_method_jsonrpc_only(self):
        rpc_method(dummy_empty, "dummy_name", protocol=Protocol.JSON_RPC)
        m = RPCMethod(dummy_empty)

        assert not m.is_available_in_xml_rpc()
        assert m.is_available_in_json_rpc()

    def test_method_repr(self):
        rpc_method(dummy_empty, "dummy_name", protocol=Protocol.JSON_RPC)
        m = RPCMethod(dummy_empty)
        assert "dummy_name" in repr(m)

    def test_method_available_for_entry_point(self):
        rpc_method(dummy_empty, "dummy_name", entry_point="my_entry_point")
        m = RPCMethod(dummy_empty)

        assert not m.available_for_entry_point(
            modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
        )
        assert m.available_for_entry_point("my_entry_point")


@rpc_method
def dummy_no_doc_no_args():
    pass


class TestNoDocNoArgs:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_no_doc_no_args)
        assert m.args == []
        assert m.args_doc == {}
        assert m.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_no_doc_no_args)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_no_doc_with_args(a, b, c):
    pass


class TestNoDocWithArgs:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_no_doc_with_args)
        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            "a": {"type": "", "text": ""},
            "b": {"type": "", "text": ""},
            "c": {"type": "", "text": ""},
        }
        assert m.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_no_doc_with_args)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_args_with_typehints(a: int, b: str, c: list) -> dict:
    pass


class TestArgsTypeHint:
    """Type hinting is correctly returned using introspection module"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_args_with_typehints)
        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            "a": {"type": "int", "text": ""},
            "b": {"type": "str", "text": ""},
            "c": {"type": "list", "text": ""},
        }
        assert m.return_doc == {"type": "dict", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_args_with_typehints)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_typehints_and_standard_docstring(a: str, b: dict, c: float) -> float:
    """

    :param a: param A
    :param b: param B
    :param c: param C
    :return: A decimal value
    """


class TestWithTypeHintAndDocstring:
    """Typehint + standard reStructuredText docstring"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_typehints_and_standard_docstring)

        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            "a": {"type": "str", "text": "param A"},
            "b": {"type": "dict", "text": "param B"},
            "c": {"type": "float", "text": "param C"},
        }
        assert m.return_doc == {"type": "float", "text": "A decimal value"}

    def test_doc(self):
        m = RPCMethod(dummy_typehints_and_standard_docstring)

        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_typehints_and_rst_docstring_types(x: list, y: str) -> dict:
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

    def test_args_and_return(self):
        m = RPCMethod(dummy_typehints_and_rst_docstring_types)

        assert m.args == ["x", "y"]
        assert m.args_doc == {
            "x": {"type": "float", "text": "abcd"},
            "y": {"type": "int", "text": "xyz"},
        }
        assert m.return_doc == {"type": "str", "text": "efgh"}

    def test_doc(self):
        m = RPCMethod(dummy_typehints_and_rst_docstring_types)

        assert m.raw_docstring == (
            "This is the docstring part of the function\n\nIt also contains a multi-line description"
        )
        assert m.html_doc == (
            "<p>This is the docstring part of the function</p><p>It also contains a multi-line description</p>"
        )


@rpc_method
def dummy_rst_docstring(name, birthdate, sex):
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
    return f"{name} ({str(sex)}) born on {str(birthdate)}"


class TestWithDoctstringOnlyFunction:
    """No typehint but everything in reStructuredText docstring"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_rst_docstring)

        assert m.args == ["name", "birthdate", "sex"]
        assert dict(m.args_doc) == {
            "name": {"type": "str", "text": "A name"},
            "birthdate": {"type": "datetime.datetime", "text": "A birthdate"},
            "sex": {"type": "str", "text": "Male or Female"},
        }
        assert m.return_doc == {
            "type": "",
            "text": "A string representation of given arguments",
        }

    def test_doc(self):
        m = RPCMethod(dummy_rst_docstring)
        assert m.raw_docstring == "This is the textual doc of the method"
        assert m.html_doc == "<p>This is the textual doc of the method</p>"


@rpc_method
def single_line_documented():
    """*italic*, **strong**, normal text"""
    return 111


class TestSingleLineDoc:
    """Standard single-line docstring with various parsers"""

    @staticmethod
    def method():
        return RPCMethod(single_line_documented)

    def test_raw_doc(self):
        method = self.method()
        assert method.raw_docstring == "*italic*, **strong**, normal text"
        assert method.html_doc == "<p>*italic*, **strong**, normal text</p>"

    def test_markdown_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        assert (
            self.method().html_doc
            == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>"
        )

    def test_rst_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        assert (
            self.method().html_doc
            == "<p><em>italic</em>, <strong>strong</strong>, normal text</p>\n"
        )


@rpc_method
def multiline_doc_simple():
    """
    This method has multi-lines documentation.

    The content is indented when raw ``__doc__`` attribute function is read.
    The indentation should not interfere with semantic interpretation of the docstring.
    """
    return 111


class TestMultiLinesDocSimple:
    """Standard multi-line docstring"""

    @staticmethod
    def method():
        return RPCMethod(multiline_doc_simple)

    def test_raw_doc(self):
        method = self.method()
        assert method.raw_docstring == (
            "This method has multi-lines documentation.\n\n"
            "The content is indented when raw ``__doc__`` attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring."
        )
        assert self.method().html_doc == (
            "<p>This method has multi-lines documentation.</p>"
            "<p>The content is indented when raw ``__doc__`` attribute function is read. "
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_markdown_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        assert self.method().html_doc == (
            "<p>This method has multi-lines documentation.</p>\n"
            "<p>The content is indented when raw <code>__doc__</code> attribute function is read.\n"
            "The indentation should not interfere with semantic interpretation of the docstring.</p>"
        )

    def test_rst_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        assert self.method().html_doc == (
            "<p>This method has multi-lines documentation.</p>\n"
            '<p>The content is indented when raw <tt class="docutils literal">__doc__</tt> attribute function is '
            "read.\nThe indentation should not interfere with semantic interpretation of the docstring.</p>\n"
        )


@rpc_method
def multiline_doc_with_block():
    """
    This method has *multi-lines* **documentation**.

    Here is a quote block:

        abcdef 123456

    """
    return "abc"


class TestMultiLinesWithBlock:
    """Standard multi-line docstring with an indented block"""

    @staticmethod
    def method():
        return RPCMethod(multiline_doc_with_block)

    def test_raw_doc(self):
        method = self.method()
        assert method.raw_docstring == (
            "This method has *multi-lines* **documentation**.\n\nHere is a quote block:\n\n    abcdef 123456"
        )
        assert self.method().html_doc == (
            "<p>This method has *multi-lines* **documentation**.</p>"
            "<p>Here is a quote block:</p>"
            "<p>    abcdef 123456</p>"
        )

    def test_markdown_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "md"
        assert self.method().html_doc == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<pre><code>abcdef 123456\n</code></pre>"
        )

    def test_rst_to_html(self, settings):
        settings.MODERNRPC_DOC_FORMAT = "rst"
        assert self.method().html_doc == (
            "<p>This method has <em>multi-lines</em> <strong>documentation</strong>.</p>\n"
            "<p>Here is a quote block:</p>\n"
            "<blockquote>\nabcdef 123456</blockquote>\n"
        )
