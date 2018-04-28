# coding: utf-8
import jsonrpcclient.exceptions
import pytest
from django.core.exceptions import ImproperlyConfigured

from modernrpc.core import rpc_method
from . import xmlrpclib
from .testsite.rpc_methods_stub.not_decorated import another_not_decorated


def test_xmlrpc_not_registered(xmlrpc_client):

    result = xmlrpc_client.system.listMethods()
    assert 'existing_but_not_decorated' not in result


def test_xmlrpc_not_decorated(xmlrpc_client):

    with pytest.raises(xmlrpclib.Fault) as exc_info:
        xmlrpc_client.existing_but_not_decorated()
    assert 'Method not found: "existing_but_not_decorated"' in str(exc_info.value)


def test_jsonrpc_not_registered(jsonrpc_client):

    result = jsonrpc_client.request('system.listMethods')
    assert 'existing_but_not_decorated' not in result


def test_jsonrpc_not_decorated(jsonrpc_client):

    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse) as exc_info:
        jsonrpc_client.existing_but_not_decorated()
    assert 'Method not found: "existing_but_not_decorated"' in str(exc_info.value)


@rpc_method
def another_dummy_method():
    return 33


def test_manual_registration(rpc_registry):
    assert 'another_dummy_method' not in rpc_registry.get_all_method_names()
    rpc_registry.register_method(another_dummy_method)
    assert 'another_dummy_method' in rpc_registry.get_all_method_names()


def test_double_registration(rpc_registry):

    assert rpc_registry.register_method(another_dummy_method) == 'another_dummy_method'
    assert rpc_registry.register_method(another_dummy_method) == 'another_dummy_method'


@rpc_method(name='another_name')
def another_dummy_method_2():
    return 33


def test_manual_registration_with_different_name(rpc_registry):

    assert 'another_name' not in rpc_registry.get_all_method_names()
    rpc_registry.register_method(another_dummy_method_2)
    assert 'another_name' in rpc_registry.get_all_method_names()
    assert 'another_dummy_method_2' not in rpc_registry.get_all_method_names()


@rpc_method(name='rpc.invalid.name')
def another_dummy_method_3():
    return 42


def test_invalid_name(rpc_registry):

    with pytest.raises(ImproperlyConfigured) as exc_info:
        rpc_registry.register_method(another_dummy_method_3)

    assert 'method names starting with "rpc." are reserved' in str(exc_info.value)
    assert 'rpc.invalid.name' not in rpc_registry.get_all_method_names()
    assert 'another_dummy_method_3' not in rpc_registry.get_all_method_names()


@rpc_method(name='divide')
def another_dummy_method_4():
    return 42


def test_duplicated_name(rpc_registry):

    with pytest.raises(ImproperlyConfigured) as exc_info:
        rpc_registry.register_method(another_dummy_method_4)

    assert 'has already been registered' in str(exc_info.value)


def test_wrong_manual_registration(rpc_registry):

    # Trying to register a not decorated method with the latest version raises an ImproperlyConfigured exception
    with pytest.raises(ImproperlyConfigured):
        rpc_registry.register_method(another_not_decorated)


def test_method_names_list(rpc_registry):

    raw_list = rpc_registry.get_all_method_names()
    sorted_list = rpc_registry.get_all_method_names(sort_methods=True)

    assert len(raw_list) == len(sorted_list)
    assert raw_list != sorted_list

    for n in raw_list:
        assert n in sorted_list


def test_methods_list(rpc_registry):

    raw_list = rpc_registry.get_all_methods()
    sorted_list = rpc_registry.get_all_methods(sort_methods=True)

    assert len(raw_list) == len(sorted_list)
    assert raw_list != sorted_list

    for m in raw_list:
        assert m in sorted_list

    for m in sorted_list:
        assert m in raw_list
