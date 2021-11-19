# coding: utf-8
from modernrpc.conf import settings as modernrpc_settings
from modernrpc.core import RPCMethod, rpc_method, JSONRPC_PROTOCOL, XMLRPC_PROTOCOL
from tests.unit.stubs import single_line_documented, multi_line_documented_1, multi_line_documented_2, \
    dummy_function, dummy_function_with_doc


def test_method_always_available(settings):
    rpc_method(dummy_function, 'dummy_name')
    m = RPCMethod(dummy_function)

    assert m.available_for_entry_point(modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
    assert m.available_for_entry_point('random_entry_point')

    assert m.is_available_in_xml_rpc()
    assert m.is_available_in_json_rpc()


def test_method_xmlrpc_only():
    rpc_method(dummy_function, 'dummy_name', protocol=XMLRPC_PROTOCOL)
    m = RPCMethod(dummy_function)

    assert m.is_available_in_xml_rpc()
    assert not m.is_available_in_json_rpc()


def test_method_jsonrpc_only():
    rpc_method(dummy_function, 'dummy_name', protocol=JSONRPC_PROTOCOL)
    m = RPCMethod(dummy_function)

    assert not m.is_available_in_xml_rpc()
    assert m.is_available_in_json_rpc()


def test_method_repr():
    rpc_method(dummy_function, 'dummy_name', protocol=JSONRPC_PROTOCOL)
    m = RPCMethod(dummy_function)
    assert 'dummy_name' in repr(m)


def test_method_available_for_entry_point(settings):
    rpc_method(dummy_function, 'dummy_name', entry_point='my_entry_point')
    m = RPCMethod(dummy_function)

    assert not m.available_for_entry_point(modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
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
    rpc_method(dummy_function_with_doc, 'dummy_name')
    m = RPCMethod(dummy_function_with_doc)

    # Dummy function has no documentation
    assert m.is_doc_available()
    assert m.is_args_doc_available()
    assert m.is_return_doc_available()
    assert m.is_any_doc_available()


def test_raw_documentation(settings):
    settings.MODERNRPC_DOC_FORMAT = ''

    rpc_method(single_line_documented, 'dummy_name')
    method = RPCMethod(single_line_documented)
    assert '*italic*, **strong**, normal text' == method.raw_docstring

    rpc_method(multi_line_documented_1, 'dummy_name_2')
    method = RPCMethod(multi_line_documented_1)
    assert 'This method has multi-lines documentation.\n\nThe content is indented when ' \
           'raw ``__doc__`` attribute function is read.\nThe indentation should not interfere ' \
           'with semantic interpretation of the docstring.' == method.raw_docstring

    rpc_method(multi_line_documented_2, 'dummy_name_3')
    method = RPCMethod(multi_line_documented_2)
    assert 'This method has *multi-lines* **documentation**.\n\nHere is ' \
           'a quote block:\n\n    abcdef 123456' == method.raw_docstring


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
