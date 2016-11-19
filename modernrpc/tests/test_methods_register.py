# coding: utf-8
import pytest
from django.core.exceptions import ImproperlyConfigured

from modernrpc.core import register_method, rpc_method, register_rpc_method, get_all_method_names, \
    unregister_rpc_method, get_all_methods
from testsite.rpc_methods_stub.not_decorated import func_a, func_b, func_c, full_documented_method

try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def test_redundant_names():

    # func_a is registered once, it's OK
    register_method(func_a)

    # We try to register another function, with an existing name => error
    with pytest.raises(ImproperlyConfigured) as excinfo:
        register_method(func_b, 'func_a')
    assert 'func_a has already been registered' in str(excinfo.value)


def test_reserved_names():

    with pytest.raises(ImproperlyConfigured) as excinfo:
        register_method(func_c, 'rpc.func_c')
    assert 'method names starting with "rpc." are reserved' in str(excinfo.value)


def test_register_twice():
    # Registering twice or more the same method is OK, no exception should be raised
    register_method(full_documented_method)
    register_method(full_documented_method)


def test_not_registered(live_server):
    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.system.listMethods()

    assert 'existing_but_not_decorated' not in result

    with pytest.raises(xmlrpc_module.Fault) as excinfo:
        client.existing_but_not_decorated()
    assert "Method not found: existing_but_not_decorated" in str(excinfo.value)


@rpc_method
def another_dummy_method():
    return 33


def test_manual_registration():

    register_rpc_method(another_dummy_method)
    assert 'another_dummy_method' in get_all_method_names()

    unregister_rpc_method('another_dummy_method')
    assert 'another_dummy_method' not in get_all_method_names()


def test_wrong_manual_registration():
    # Trying to register a not decorated method with the latest version raises an ImproperlyConfigured exception
    with pytest.raises(ImproperlyConfigured) as excp:
        register_rpc_method(func_a)


def test_method_names_list():

    raw_list = get_all_method_names()
    sorted_list = get_all_method_names(sort_methods=True)

    assert len(raw_list) == len(sorted_list)
    assert raw_list != sorted_list

    for n in raw_list:
        assert n in sorted_list


def test_methods_list():

    raw_list = get_all_methods()
    sorted_list = get_all_methods(sort_methods=True)

    assert len(raw_list) == len(sorted_list)
    assert raw_list != sorted_list

    for m in raw_list:
        assert m in sorted_list
