# coding: utf-8
import pytest
from django.utils.six.moves import xmlrpc_client
from jsonrpcclient.http_client import HTTPClient

from modernrpc.exceptions import RPC_METHOD_NOT_FOUND, RPC_INTERNAL_ERROR


def test_xmlrpc_normal_multicall(live_server):
    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    multicall = xmlrpc_client.MultiCall(client)
    multicall.add(5, 10)
    multicall.divide(30, 5)
    multicall.add(8, 8)
    multicall.divide(6, 2)
    result = multicall()

    assert isinstance(result, xmlrpc_client.MultiCallIterator)
    assert result[0] == 15  # 5 + 10
    assert result[1] == 6   # 30 / 5
    assert result[2] == 16  # 8 + 8
    assert result[3] == 3   # 6 / 2


def test_xmlrpc_multicall_with_errors(live_server):
    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    multicall = xmlrpc_client.MultiCall(client)
    multicall.add(7, 3)
    multicall.unknown_method()
    multicall.add(8, 8)
    result = multicall()

    assert isinstance(result, xmlrpc_client.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND
    assert result[2] == 16


def test_xmlrpc_multicall_with_errors_2(live_server):
    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    multicall = xmlrpc_client.MultiCall(client)
    multicall.add(7, 3)
    multicall.divide(75, 0)
    multicall.add(8, 8)
    result = multicall()

    assert isinstance(result, xmlrpc_client.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpc_client.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert result[2] == 16


def test_jsonrpc_normal_multicall(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    calls_args = [
        {'methodName': 'add', 'params': (5, 10)},
        {'methodName': 'divide', 'params': (30, 5)},
    ]
    result = c.request('system.multicall', [calls_args])

    assert isinstance(result, list)
    # Since json-rpc doesn't provide standard for system.multicall,
    # we used the same rules than the one used for xml-rpc
    # See https://mirrors.talideon.com/articles/multicall.html:
    assert result[0] == [15]  # 5 + 10
    assert result[1] == [6]   # 30 / 5


def test_jsonrpc_multicall_with_errors(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    calls_args = [
        {'methodName': 'add', 'params': (7, 3)},
        {'methodName': 'unknown_method'},
        {'methodName': 'add', 'params': (8, 8)},
    ]
    result = c.request('system.multicall', [calls_args])

    assert isinstance(result, list)
    assert result[0] == [10]
    assert result[1] == {"faultCode": RPC_METHOD_NOT_FOUND, "faultString": "Method not found: unknown_method"}
    assert result[2] == [16]


def test_jsonrpc_multicall_with_errors_2(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    calls_args = [
        {'methodName': 'add', 'params': (7, 3)},
        {'methodName': 'divide', 'params': (75, 0)},
        {'methodName': 'add', 'params': (8, 8)},
    ]
    result = c.request('system.multicall', [calls_args])

    assert isinstance(result, list)
    assert result[0] == [10]
    assert result[1]['faultCode'] == RPC_INTERNAL_ERROR
    # py2: integer division or modulo by zero
    # py2: division by zero
    assert 'by zero' in result[1]['faultString']
    assert result[2] == [16]
