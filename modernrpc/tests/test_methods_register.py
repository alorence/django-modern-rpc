# coding: utf-8
import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils.six.moves import xmlrpc_client
from pytest import raises

from modernrpc.core import rpc_method, register_rpc_method, get_all_method_names, get_all_methods
from testsite.rpc_methods_stub.not_decorated import another_not_decorated


def test_not_registered(live_server):
    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.system.listMethods()

    assert 'existing_but_not_decorated' not in result

    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        client.existing_but_not_decorated()
    assert "Method not found: existing_but_not_decorated" in str(excinfo.value)


@rpc_method
def another_dummy_method():
    return 33


def test_manual_registration():

    register_rpc_method(another_dummy_method)
    assert 'another_dummy_method' in get_all_method_names()


@rpc_method(name='another_name')
def another_dummy_method_2():
    return 33


def test_manual_registration_with_different_name():

    register_rpc_method(another_dummy_method_2)
    assert 'another_name' in get_all_method_names()


@rpc_method(name='rpc.invalid.name')
def another_dummy_method_3():
    return 42


def test_invalid_name():

    with raises(ImproperlyConfigured) as excinfo:
        register_rpc_method(another_dummy_method_3)

    assert 'method names starting with "rpc." are reserved' in str(excinfo.value)
    assert 'rpc.invalid.name' not in get_all_method_names()


@rpc_method(name='divide')
def another_dummy_method_4():
    return 42


def test_duplicated_name():

    with raises(ImproperlyConfigured) as excinfo:
        register_rpc_method(another_dummy_method_4)

    assert 'has already been registered' in str(excinfo.value)


def test_wrong_manual_registration():
    # Trying to register a not decorated method with the latest version raises an ImproperlyConfigured exception
    with pytest.raises(ImproperlyConfigured):
        register_rpc_method(another_not_decorated)


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
