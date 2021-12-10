# coding: utf-8

from modernrpc.conf import settings as modernrpc_settings
from modernrpc.core import RPCMethod, rpc_method, JSONRPC_PROTOCOL, XMLRPC_PROTOCOL


def dummy_empty():
    pass


class TestRpcMethod:
    """Check wether entry_points and protocol specifications works as expected when registering method"""

    def test_method_always_available(self):
        rpc_method(dummy_empty, 'dummy_name')
        m = RPCMethod(dummy_empty)

        assert m.available_for_entry_point(modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
        assert m.available_for_entry_point('random_entry_point')

        assert m.is_available_in_xml_rpc()
        assert m.is_available_in_json_rpc()

    def test_method_xmlrpc_only(self):
        rpc_method(dummy_empty, 'dummy_name', protocol=XMLRPC_PROTOCOL)
        m = RPCMethod(dummy_empty)

        assert m.is_available_in_xml_rpc()
        assert not m.is_available_in_json_rpc()

    def test_method_jsonrpc_only(self):
        rpc_method(dummy_empty, 'dummy_name', protocol=JSONRPC_PROTOCOL)
        m = RPCMethod(dummy_empty)

        assert not m.is_available_in_xml_rpc()
        assert m.is_available_in_json_rpc()

    def test_method_repr(self):
        rpc_method(dummy_empty, 'dummy_name', protocol=JSONRPC_PROTOCOL)
        m = RPCMethod(dummy_empty)
        assert 'dummy_name' in repr(m)

    def test_method_available_for_entry_point(self):
        rpc_method(dummy_empty, 'dummy_name', entry_point='my_entry_point')
        m = RPCMethod(dummy_empty)

        assert not m.available_for_entry_point(modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
        assert m.available_for_entry_point('my_entry_point')


class TestNoDocNoTypeFunction:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        rpc_method(dummy_empty)
        m = RPCMethod(dummy_empty)
        assert m.args == []
        assert m.args_doc == {}
        assert m.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        rpc_method(dummy_empty)
        m = RPCMethod(dummy_empty)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_with_args_no_doc(a, b, c):
    pass


class TestNoDocNoTypeFunctionWithArgs:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_with_args_no_doc)
        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            'a': {'type': '', 'text': ''},
            'b': {'type': '', 'text': ''},
            'c': {'type': '', 'text': ''}
        }
        assert m.return_doc == {"type": "", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_with_args_no_doc)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_args_with_typehints(a: int, b: str, c: list) -> dict:
    pass


class TestNoDocNoTypeFunctionWithArgsTypehints:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_args_with_typehints)
        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            'a': {'type': 'int', 'text': ''},
            'b': {'type': 'str', 'text': ''},
            'c': {'type': 'list', 'text': ''}
        }
        assert m.return_doc == {"type": "dict", "text": ""}

    def test_doc(self):
        m = RPCMethod(dummy_args_with_typehints)
        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_args_with_typehints_and_text(a: str, b: dict, c: float) -> float:
    """

    :param a: param A
    :param b: param B
    :param c: param C
    :return: A decimal value
    """


class TestEmptyDocTypeHintsFunction:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_args_with_typehints_and_text)

        assert m.args == ["a", "b", "c"]
        assert m.args_doc == {
            'a': {'type': 'str', 'text': 'param A'},
            'b': {'type': 'dict', 'text': 'param B'},
            'c': {'type': 'float', 'text': 'param C'}
        }
        assert m.return_doc == {"type": "float", "text": "A decimal value"}

    def test_doc(self):
        m = RPCMethod(dummy_args_with_typehints_and_text)

        assert m.raw_docstring == ""
        assert m.html_doc == ""


@rpc_method
def dummy_with_typehints_doctypes_and_text(x: list, y: str) -> dict:
    """This is the docstring part of the function

    It also contains a multi-line description
    :param x: abcd
    :param y: xyz
    :return: efgh
    :type x: float
    :type y: int
    :rtype: str
    """


class TestWithDoctypesAndTypeHintsFunction:
    """Make sure docstring and introspection works as expected"""

    def test_args_and_return(self):
        m = RPCMethod(dummy_with_typehints_doctypes_and_text)

        assert m.args == ["x", "y"]
        assert m.args_doc == {
            'x': {'type': 'float', 'text': 'abcd'},
            'y': {'type': 'int', 'text': 'xyz'},
        }
        assert m.return_doc == {"type": "str", "text": "efgh"}

    def test_doc(self):
        m = RPCMethod(dummy_with_typehints_doctypes_and_text)

        assert m.raw_docstring == (
            "This is the docstring part of the function\n\nIt also contains a multi-line description"
        )
        assert m.html_doc == (
            "<p>This is the docstring part of the function</p><p>It also contains a multi-line description</p>"
        )


def dummy_function_with_doc(name, birthdate, sex):
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
    return '{} ({}) born on {}'.format(name, str(sex), str(birthdate))


def single_line_documented():
    """*italic*, **strong**, normal text"""
    return 111


def multi_line_documented_1():
    """
    This method has multi-lines documentation.

    The content is indented when raw ``__doc__`` attribute function is read.
    The indentation should not interfere with semantic interpretation of the docstring.
    """
    return 111


def multi_line_documented_2():
    """
    This method has *multi-lines* **documentation**.

    Here is a quote block:

        abcdef 123456

    """
    return "abc"


class TestMethodDocumentation:
    def test_raw_documentation(self, settings):
        settings.MODERNRPC_DOC_FORMAT = ''

        rpc_method(single_line_documented, 'dummy_name')
        method = RPCMethod(single_line_documented)
        assert '*italic*, **strong**, normal text' == method.raw_docstring

        rpc_method(multi_line_documented_1, 'dummy_name_2')
        method = RPCMethod(multi_line_documented_1)
        assert ('This method has multi-lines documentation.\n\nThe content is indented when '
                'raw ``__doc__`` attribute function is read.\nThe indentation should not interfere '
                'with semantic interpretation of the docstring.') == method.raw_docstring

        rpc_method(multi_line_documented_2, 'dummy_name_3')
        method = RPCMethod(multi_line_documented_2)
        assert ('This method has *multi-lines* **documentation**.\n\nHere is '
                'a quote block:\n\n    abcdef 123456') == method.raw_docstring

    def test_html_documentation_simple(self, settings):
        settings.MODERNRPC_DOC_FORMAT = ''

        rpc_method(single_line_documented, 'dummy_name')
        method = RPCMethod(single_line_documented)
        assert '*italic*, **strong**, normal text' in method.html_doc

        rpc_method(multi_line_documented_1, 'dummy_name_2')
        method = RPCMethod(multi_line_documented_1)
        # We ensure no <br/> is added to the text when the original docstring contained single \n characters
        assert 'attribute function is read. The indentation should not' in method.html_doc

    def test_html_documentation_markdown(self, settings):
        settings.MODERNRPC_DOC_FORMAT = 'md'

        rpc_method(single_line_documented, 'dummy_name')
        method = RPCMethod(single_line_documented)
        assert '<em>italic</em>, <strong>strong</strong>, normal text' in method.html_doc

        rpc_method(multi_line_documented_1, 'dummy_name_2')
        method = RPCMethod(multi_line_documented_1)
        assert '<blockquote>' not in method.html_doc

        rpc_method(multi_line_documented_2, 'dummy_name_3')
        method = RPCMethod(multi_line_documented_2)
        assert '<em>multi-lines</em>' in method.html_doc.replace('\n', '')
        assert '<strong>documentation</strong>' in method.html_doc.replace('\n', '')
        assert '<pre><code>abcdef 123456</code></pre>' in method.html_doc.replace('\n', '')

    def test_html_documentation_reST(self, settings):
        settings.MODERNRPC_DOC_FORMAT = 'rst'

        rpc_method(single_line_documented, 'dummy_name')
        method = RPCMethod(single_line_documented)
        assert '<em>italic</em>, <strong>strong</strong>, normal text' in method.html_doc

        rpc_method(multi_line_documented_1, 'dummy_name_2')
        method = RPCMethod(multi_line_documented_1)
        assert '<blockquote>' not in method.html_doc

        rpc_method(multi_line_documented_2, 'dummy_name_3')
        method = RPCMethod(multi_line_documented_2)
        assert '<em>multi-lines</em>' in method.html_doc.replace('\n', '')
        assert '<strong>documentation</strong>' in method.html_doc.replace('\n', '')
        assert '<blockquote>abcdef 123456</blockquote>' in method.html_doc.replace('\n', '')
