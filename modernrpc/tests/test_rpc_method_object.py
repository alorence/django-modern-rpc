# coding: utf-8
from modernrpc.conf import settings
from modernrpc.core import RPCMethod, get_all_methods, get_method, ALL, rpc_method
from modernrpc.handlers import XMLRPC, JSONRPC
from testsite.rpc_methods_stub.not_decorated import full_documented_method


def dummy_function():
    return 42


def test_method_always_available():

    rpc_method(dummy_function, 'dummy_name')
    m = RPCMethod(dummy_function)

    assert m.available_for_entry_point(settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
    assert m.available_for_entry_point('random_entry_point')

    assert m.is_available_in_xml_rpc()
    assert m.is_available_in_json_rpc()


def test_method_xmlrpc_only():

    rpc_method(dummy_function, 'dummy_name', protocol=XMLRPC)
    m = RPCMethod(dummy_function)

    assert m.is_available_in_xml_rpc()
    assert not m.is_available_in_json_rpc()


def test_method_jsonrpc_only():

    rpc_method(dummy_function, 'dummy_name', protocol=JSONRPC)
    m = RPCMethod(dummy_function)

    assert not m.is_available_in_xml_rpc()
    assert m.is_available_in_json_rpc()


def test_method_repr():

    rpc_method(dummy_function, 'dummy_name', protocol=JSONRPC)
    m = RPCMethod(dummy_function)
    assert 'dummy_name' in repr(m)


def test_method_available_for_entry_point():

    rpc_method(dummy_function, 'dummy_name', entry_point='my_entry_point')
    m = RPCMethod(dummy_function)

    assert not m.available_for_entry_point(settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
    assert m.available_for_entry_point('my_entry_point')


def test_docs_helpers():

    rpc_method(dummy_function, 'dummy_name')
    m = RPCMethod(dummy_function)

    # Dummy function has no documentation
    assert not m.is_doc_available()
    assert not m.is_args_doc_available()
    assert not m.is_return_doc_available()
    assert not m.is_any_doc_available()


def test_docs_helpers_2():

    rpc_method(full_documented_method, 'dummy_name')
    m = RPCMethod(full_documented_method)

    # Dummy function has no documentation
    assert m.is_doc_available()
    assert m.is_args_doc_available()
    assert m.is_return_doc_available()
    assert m.is_any_doc_available()


def test_get_methods():

    methods = get_all_methods(sort_methods=False)
    sorted_methods = get_all_methods(sort_methods=True)

    assert methods != sorted_methods
    assert len(methods) == len(sorted_methods)
    # Ensure all methods from on is referenced in other
    assert all([method in sorted_methods for method in methods])
    assert all([method in methods for method in sorted_methods])


def test_arguments_order():

    method = get_method("divide", ALL, ALL)

    args_names = list(method.args_doc.keys())
    # We want to make sure arguments doc is stored with the same order method parameters are defined
    assert args_names[0] == 'numerator'
    assert args_names[1] == 'denominator'
    assert args_names[2] == 'x'
    assert args_names[3] == 'y'
    assert args_names[4] == 'z'
    assert args_names[5] == 'a'
    assert args_names[6] == 'b'
    assert args_names[7] == 'c'

    args = method.args
    assert args[0] == 'numerator'
    assert args[1] == 'denominator'
    assert args[2] == 'x'
    assert args[3] == 'y'
    assert args[4] == 'z'
    assert args[5] == 'a'
    assert args[6] == 'b'
    assert args[7] == 'c'


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


def test_html_documentation_simple(settings):

    settings.MODERNRPC_DOC_FORMAT = ''

    rpc_method(single_line_documented, 'dummy_name')
    method = RPCMethod(single_line_documented)
    assert '*italic*, **strong**, normal text' in method.html_doc

    rpc_method(multi_line_documented_1, 'dummy_name_2')
    method = RPCMethod(multi_line_documented_1)
    # We ensure no <br/> is added to the text when the original docstring contained single \n characters
    assert 'attribute function is read. The indentation should not' in method.html_doc


def test_html_documentation_markdown(settings):

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


def test_html_documentation_reST(settings):

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
