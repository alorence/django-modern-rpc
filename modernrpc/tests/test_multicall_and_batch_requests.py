# coding: utf-8
import json

import pytest
import requests
from jsonrpcclient.exceptions import ReceivedErrorResponse

from modernrpc.exceptions import RPC_METHOD_NOT_FOUND, RPC_INTERNAL_ERROR, RPC_INVALID_REQUEST
from . import xmlrpclib


def test_xmlrpc_multicall_standard(xmlrpc_client):

    multicall = xmlrpclib.MultiCall(xmlrpc_client)
    multicall.add(5, 10)
    multicall.divide(30, 5)
    multicall.add(8, 8)
    multicall.divide(6, 2)
    result = multicall()

    assert isinstance(result, xmlrpclib.MultiCallIterator)
    assert result[0] == 15  # 5 + 10
    assert result[1] == 6   # 30 / 5
    assert result[2] == 16  # 8 + 8
    assert result[3] == 3   # 6 / 2


def test_xmlrpc_multicall_with_errors(xmlrpc_client):

    multicall = xmlrpclib.MultiCall(xmlrpc_client)
    multicall.add(7, 3)
    multicall.unknown_method()
    multicall.add(8, 8)
    result = multicall()

    assert isinstance(result, xmlrpclib.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND
    assert result[2] == 16


def test_xmlrpc_multicall_with_errors_2(xmlrpc_client):

    multicall = xmlrpclib.MultiCall(xmlrpc_client)
    multicall.add(7, 3)
    multicall.divide(75, 0)
    multicall.add(8, 8)
    result = multicall()

    assert isinstance(result, xmlrpclib.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert result[2] == 16


def test_xmlrpc_multicall_with_auth(xmlrpc_client):

    multicall = xmlrpclib.MultiCall(xmlrpc_client)
    multicall.add(7, 3)
    multicall.logged_superuser_required(5)
    result = multicall()

    assert isinstance(result, xmlrpclib.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excinfo.value.faultString


def test_xmlrpc_multicall_with_auth_2(xmlrpc_client_as_superuser):

    multicall = xmlrpclib.MultiCall(xmlrpc_client_as_superuser)
    multicall.add(7, 3)
    multicall.logged_superuser_required(5)
    result = multicall()

    assert isinstance(result, xmlrpclib.MultiCallIterator)
    assert result[0] == 10
    assert result[1] == 5


def test_jsonrpc_multicall_error(jsonrpc_client):

    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.request('system.multicall')

    assert 'Method not found' in excinfo.value.message
    assert excinfo.value.code == RPC_METHOD_NOT_FOUND


def test_jsonrpc_batch_standard(jsonrpc_client):

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': [5, 10]},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'divide', 'params': [30, 5]},
    ])

    result = jsonrpc_client.send(batch_request)

    assert isinstance(result, list)

    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 15}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'result': 6}


def test_jsonrpc_batch_with_errors(jsonrpc_client):

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': [7, 3]},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'unknown_method'},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'add', 'params': {'a': 2, 'b': 13}},
    ])

    result = jsonrpc_client.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 10}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'error': {
        'code': RPC_METHOD_NOT_FOUND, 'message': 'Method not found: "unknown_method"'
    }}
    assert result[2] == {'jsonrpc': '2.0', 'id': 3, 'result': 15}


def test_jsonrpc_batch_with_errors_2(jsonrpc_client):

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': [7, 3]},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'divide', 'params': (75, 0)},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'add', 'params': (8, 8)},
    ])

    result = jsonrpc_client.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 10}
    assert result[1]['id'] == 2
    assert result[1]['error']['code'] == RPC_INTERNAL_ERROR
    # py2: integer division or modulo by zero
    # py2: division by zero
    assert 'by zero' in result[1]['error']['message']
    assert result[2] == {'jsonrpc': '2.0', 'id': 3, 'result': 16}


def test_jsonrpc_batch_with_named_params(jsonrpc_client):

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': {'a': 5, 'b': 10}},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'divide', 'params': {'numerator': 30, 'denominator': 5}},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'method_with_kwargs'},
        {'jsonrpc': '2.0', 'id': 4, 'method': 'method_with_kwargs_2', 'params': [6]},
        {'jsonrpc': '2.0', 'id': 5, 'method': 'method_with_kwargs_2', 'params': {'x': 25}},
    ])

    result = jsonrpc_client.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 15}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'result': 6}

    assert result[2] == {'jsonrpc': '2.0', 'id': 3, 'result': '__json_rpc'}
    assert result[3] == {'jsonrpc': '2.0', 'id': 4, 'result': [6, '__json_rpc']}
    assert result[4] == {'jsonrpc': '2.0', 'id': 5, 'result': [25, '__json_rpc']}


def test_jsonrpc_batch_with_notifications(jsonrpc_client):

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': {'a': 5, 'b': 10}},
        {'jsonrpc': '2.0', 'method': 'method_with_kwargs'},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'divide', 'params': {'numerator': 30, 'denominator': 5}}
    ])

    result = jsonrpc_client.send(batch_request)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 15}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'result': 6}


def test_jsonrpc_batch_notifications_only(jsonrpc_client):

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'method': 'add', 'params': {'a': 5, 'b': 10}},
        {'jsonrpc': '2.0', 'method': 'method_with_kwargs'},
        {'jsonrpc': '2.0', 'method': 'divide', 'params': {'numerator': 30, 'denominator': 5}}
    ])

    result = jsonrpc_client.send(batch_request)

    assert result is None


def test_jsonrpc_batch_with_auth(jsonrpc_client):

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': {'a': 7, 'b': 3}},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'logged_superuser_required', 'params': [5, ]}
    ])

    result = jsonrpc_client.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 10}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'error': {
        'code': RPC_INTERNAL_ERROR,
        'message': 'Internal error: Authentication failed when calling "logged_superuser_required"'
    }}


def test_jsonrpc_batch_with_auth_2(jsonrpc_client, superuser, common_pwd):

    jsonrpc_client.session.auth = (superuser.username, common_pwd)

    batch_request = json.dumps([
        {'jsonrpc': '2.0', 'id': 1, 'method': 'add', 'params': {'a': 7, 'b': 3}},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'logged_superuser_required', 'params': [5, ]}
    ])

    result = jsonrpc_client.send(batch_request)

    assert isinstance(result, list)
    assert result[0] == {'jsonrpc': '2.0', 'id': 1, 'result': 10}
    assert result[1] == {'jsonrpc': '2.0', 'id': 2, 'result': 5}


def test_jsonrpc_batch_invalid_request(all_rpc_url):

    headers = {'content-type': 'application/json'}
    result = requests.post(all_rpc_url, data='[1, 2, 3]', headers=headers).json()

    assert isinstance(result, list)
    assert len(result) == 3

    assert result[0]['jsonrpc'] == '2.0'
    assert result[0]['id'] is None
    assert result[0]['error']['code'] == RPC_INVALID_REQUEST
    assert 'Invalid request' in result[0]['error']['message']

    assert result[1]['jsonrpc'] == '2.0'
    assert result[1]['id'] is None
    assert result[1]['error']['code'] == RPC_INVALID_REQUEST
    assert 'Invalid request' in result[1]['error']['message']

    assert result[2]['jsonrpc'] == '2.0'
    assert result[2]['id'] is None
    assert result[2]['error']['code'] == RPC_INVALID_REQUEST
    assert 'Invalid request' in result[2]['error']['message']
