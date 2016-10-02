# coding: utf-8
import pytest

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

    with pytest.raises(xmlrpc_module.Fault) as e:
        client.get_null()

        assert e.faultCode == -32603
        assert 'cannot marshal None unless allow_none is enabled' in e.faultString


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
