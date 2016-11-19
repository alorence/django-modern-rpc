# coding: utf-8
import pytest
from django.core.exceptions import ImproperlyConfigured

from modernrpc.core import register_method
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
