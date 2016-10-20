# coding: utf-8
import xml

import pytest

from modernrpc.exceptions import RPC_METHOD_NOT_FOUND, RPC_INTERNAL_ERROR

try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def test_xmlrpc_normal_multicall(live_server):
    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    multicall = xmlrpc_module.MultiCall(client)
    multicall.add(5, 10)
    multicall.divide(30, 5)
    multicall.add(8, 8)
    multicall.divide(6, 2)
    result = multicall()

    assert isinstance(result, xmlrpc_module.MultiCallIterator)
    assert result[0] == 15  # 5 + 10
    assert result[1] == 6   # 30 / 5
    assert result[2] == 16  # 8 + 8
    assert result[3] == 3   # 6 / 2


def test_xmlrpc_multicall_with_errors(live_server):
    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    multicall = xmlrpc_module.MultiCall(client)
    multicall.add(7, 3)
    multicall.unknown_method()
    multicall.add(8, 8)
    result = multicall()

    assert isinstance(result, xmlrpc_module.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpc_module.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND
    assert result[2] == 16


def test_xmlrpc_multicall_with_errors_2(live_server):
    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    multicall = xmlrpc_module.MultiCall(client)
    multicall.add(7, 3)
    multicall.divide(75, 0)
    multicall.add(8, 8)
    result = multicall()

    assert isinstance(result, xmlrpc_module.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpc_module.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert result[2] == 16
