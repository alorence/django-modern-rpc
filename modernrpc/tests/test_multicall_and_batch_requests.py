# coding: utf-8
import json

import pytest
from django.utils.six.moves import xmlrpc_client
from jsonrpcclient.http_client import HTTPClient

from modernrpc.exceptions import RPC_METHOD_NOT_FOUND, RPC_INTERNAL_ERROR


def test_xmlrpc_multicall_standard(live_server):

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


def test_jsonrpc_batch_standard(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': [5, 10]},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'divide', 'params': [30, 5]},
    ])

    result = c.send(batch_request)

    assert isinstance(result, list)

    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 15}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'result': 6}


def test_jsonrpc_batch_with_errors(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': [7, 3]},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'unknown_method'},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'add', 'params': {'a': 2, 'b': 13}},
    ])

    result = c.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 10}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'error': {
        'code': RPC_METHOD_NOT_FOUND, 'message': 'Method not found: unknown_method'
    }}
    assert result[2] == {'jsonrpc': '2.0', 'id': 3, 'result': 15}


def test_jsonrpc_batch_with_errors_2(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': [7, 3]},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'divide', 'params': (75, 0)},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'add', 'params': (8, 8)},
    ])

    result = c.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 10}
    assert result[1]['id'] == 2
    assert result[1]['error']['code'] == RPC_INTERNAL_ERROR
    # py2: integer division or modulo by zero
    # py2: division by zero
    assert 'by zero' in result[1]['error']['message']
    assert result[2] == {'jsonrpc': '2.0', 'id': 3, 'result': 16}


def test_jsonrpc_batch_with_named_params(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': {'a': 5, 'b': 10}},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'divide', 'params': {'numerator': 30, 'denominator': 5}},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'method_with_kwargs'},
        {'jsonrpc': '2.0', 'id': 4, 'method': 'method_with_kwargs_2', 'params': [6]},
        {'jsonrpc': '2.0', 'id': 5, 'method': 'method_with_kwargs_2', 'params': {'x': 25}},
    ])

    result = c.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 15}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'result': 6}

    assert result[2] == {'jsonrpc': '2.0', 'id': 3, 'result': '__json_rpc'}
    assert result[3] == {'jsonrpc': '2.0', 'id': 4, 'result': [6, '__json_rpc']}
    assert result[4] == {'jsonrpc': '2.0', 'id': 5, 'result': [25, '__json_rpc']}
