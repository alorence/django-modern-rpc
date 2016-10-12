# coding: utf-8
import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR

try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def test_xrpc_bool(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_true()

    assert type(result) == bool
    assert result is True

    result = client.get_false()

    assert type(result) == bool
    assert result is False


def test_xrpc_null(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_module.Fault) as excinfo:
        client.get_null()

    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert 'cannot marshal None unless allow_none is enabled' in excinfo.value.faultString


def test_xrpc_numeric(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    result = client.get_int()
    assert type(result) == int
    assert result == 42

    result = client.get_negative_int()
    assert type(result) == int
    assert result == -42

    result = client.get_float()
    assert type(result) == float
    assert result == 3.14


def test_xrpc_string(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_string()

    # Unlike JSON-RPC, XML-RPC always return a str. That means the result is unicode
    # in Python 3 and ASCII in Python 2. This may be addressed in the future
    assert type(result) == str
    assert result == 'abcde'


def test_jsrpc_bytes(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_byte()

    assert result == b'abcde'


def test_xrpc_list(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_list()

    assert type(result) == list
    assert result == [1, 2, 3, ]


def test_jsrpc_struct(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_struct()

    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }
