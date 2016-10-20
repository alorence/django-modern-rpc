# coding: utf-8
from modernrpc.core import RPCMethod, ALL
from modernrpc.handlers import XMLRPC, JSONRPC
from modernrpc.modernrpc_settings import MODERNRPC_DEFAULT_ENTRYPOINT_NAME


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


def test_method_jsonrpc_only():
    m = RPCMethod(dummy_function, 'dummy_name', protocol=JSONRPC)

    assert not m.available_for_protocol(XMLRPC)
    assert m.available_for_protocol(JSONRPC)


def test_method_available_for_entry_point():
    m = RPCMethod(dummy_function, 'dummy_name', entry_point='my_entry_point')

    assert not m.available_for_entry_point(MODERNRPC_DEFAULT_ENTRYPOINT_NAME)
    assert m.available_for_entry_point('my_entry_point')
