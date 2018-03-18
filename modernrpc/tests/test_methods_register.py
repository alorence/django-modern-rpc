# coding: utf-8
import pytest
from django.core.exceptions import ImproperlyConfigured

from modernrpc.core import rpc_method, registry
from . import python_xmlrpc
from .testsite.rpc_methods_stub.not_decorated import another_not_decorated


def test_not_registered(live_server):
    client = python_xmlrpc.ServerProxy(live_server.url + '/all-rpc/')
    result = client.system.listMethods()

    assert 'existing_but_not_decorated' not in result

    with pytest.raises(python_xmlrpc.Fault) as exc_info:
        client.existing_but_not_decorated()
    assert 'Method not found: "existing_but_not_decorated"' in str(exc_info.value)


@rpc_method
def another_dummy_method():
    return 33


def test_manual_registration():

    registry.register_method(another_dummy_method)
    assert 'another_dummy_method' in registry.get_all_method_names()


def test_double_registration():

    assert registry.register_method(another_dummy_method) == 'another_dummy_method'
    assert registry.register_method(another_dummy_method) == 'another_dummy_method'


@rpc_method(name='another_name')
def another_dummy_method_2():
    return 33


def test_manual_registration_with_different_name():

    registry.register_method(another_dummy_method_2)
    assert 'another_name' in registry.get_all_method_names()
    assert 'another_dummy_method_2' not in registry.get_all_method_names()


@rpc_method(name='rpc.invalid.name')
def another_dummy_method_3():
    return 42


def test_invalid_name():

    with pytest.raises(ImproperlyConfigured) as exc_info:
        registry.register_method(another_dummy_method_3)

    assert 'method names starting with "rpc." are reserved' in str(exc_info.value)
    assert 'rpc.invalid.name' not in registry.get_all_method_names()
    assert 'another_dummy_method_3' not in registry.get_all_method_names()


@rpc_method(name='divide')
def another_dummy_method_4():
    return 42


def test_duplicated_name():

    with pytest.raises(ImproperlyConfigured) as exc_info:
        registry.register_method(another_dummy_method_4)

    assert 'has already been registered' in str(exc_info.value)


def test_wrong_manual_registration():

    # Trying to register a not decorated method with the latest version raises an ImproperlyConfigured exception
    with pytest.raises(ImproperlyConfigured):
        registry.register_method(another_not_decorated)


def test_method_names_list():

    raw_list = registry.get_all_method_names()
    sorted_list = registry.get_all_method_names(sort_methods=True)

    assert len(raw_list) == len(sorted_list)
    assert raw_list != sorted_list

    for n in raw_list:
        assert n in sorted_list


def test_methods_list():

    raw_list = registry.get_all_methods()
    sorted_list = registry.get_all_methods(sort_methods=True)

    assert len(raw_list) == len(sorted_list)
    assert raw_list != sorted_list

    for m in raw_list:
        assert m in sorted_list

    for m in sorted_list:
        assert m in raw_list
