# coding: utf-8
import pytest

from modernrpc.core import RPCMethod, get_all_methods, get_method, ALL
from modernrpc.handlers import XMLRPC, JSONRPC
from modernrpc.config import MODERNRPC_DEFAULT_ENTRYPOINT_NAME
from testsite.rpc_methods_stub.not_decorated import full_documented_method


def dummy_function():
    return 42


def test_method_always_available():

    m = RPCMethod(dummy_function, 'dummy_name')

    assert m.available_for_entry_point(MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
    assert m.available_for_entry_point('random_entry_point')

    assert m.available_for_protocol(XMLRPC)
    assert m.available_for_protocol(JSONRPC)


def test_method_xmlrpc_only():
    m = RPCMethod(dummy_function, 'dummy_name', protocol=XMLRPC)

    assert m.available_for_protocol(XMLRPC)
    assert not m.available_for_protocol(JSONRPC)

    # This is for coverage :)
    assert m.is_available_in_xml_rpc()
    assert not m.is_available_in_json_rpc()


def test_method_jsonrpc_only():
    m = RPCMethod(dummy_function, 'dummy_name', protocol=JSONRPC)

    assert not m.available_for_protocol(XMLRPC)
    assert m.available_for_protocol(JSONRPC)

    # This is for coverage :)
    assert not m.is_available_in_xml_rpc()
    assert m.is_available_in_json_rpc()


def test_method_available_for_entry_point():
    m = RPCMethod(dummy_function, 'dummy_name', entry_point='my_entry_point')

    assert not m.available_for_entry_point(MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
    assert m.available_for_entry_point('my_entry_point')


def test_docs_helpers():
    m = RPCMethod(dummy_function, 'dummy_name')

    # Dummy function has no documentation
    assert not m.is_doc_available()
    assert not m.is_args_doc_available()
    assert not m.is_return_doc_available()
    assert not m.is_any_doc_available()


def test_docs_helpers_2():
    m = RPCMethod(full_documented_method, 'dummy name')

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
    for m in methods:
        if m not in sorted_methods:
            pytest.fail('Found a method ({}) not referenced in sorted_methods'.format(m))


def test_arguments_order():

    method = get_method("divide", ALL, ALL)

    args_names = list(method.args_doc.keys())
    # We want to make sure arguments doc is stored with the same order method parameters are defined
    assert args_names[0] == 'numerator'
    assert args_names[1] == 'denominator'
