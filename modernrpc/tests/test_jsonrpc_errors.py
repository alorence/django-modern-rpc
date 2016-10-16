# coding: utf-8
import json

import pytest
import requests

from dummy_jsonrpc_client import ServerProxy, JsonRpcFault
from modernrpc.exceptions import RPC_INVALID_REQUEST, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR, RPC_INVALID_PARAMS, \
    RPC_CUSTOM_ERROR_BASE, RPC_CUSTOM_ERROR_MAX, RPC_INTERNAL_ERROR


def test_jsrpc_call_unknown_method(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(JsonRpcFault) as excinfo:
        client.non_existing_method()

    assert 'Method not found: non_existing_method' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND


def test_jsrpc_call_bad_request(live_server):

    headers = {'content-type': 'application/json'}
    payload = {
        "method": "add",
        "params": [],
        "jsonrpc": "2.0",
        # Missing field 'id' in this request
    }
    req_data = json.dumps(payload)
    response = requests.post(live_server.url + '/all-rpc/', data=req_data, headers=headers).json()

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] is None
    error = response['error']

    assert 'Invalid request' in error['message']
    assert 'id' in error['message']
    assert error['code'] == RPC_INVALID_REQUEST


def test_jsrpc_invalid_request(live_server):
    # Closing } is missing from this payload
    invalid_json_payload = '''
        {
            "method": "add",
            "params": [},
            "jsonrpc": "2.0",
            "id": 74,
    '''
    headers = {'content-type': 'application/json'}
    response = requests.post(live_server.url + '/all-rpc/', data=invalid_json_payload, headers=headers).json()

    assert 'error' in response
    assert 'result' not in response
    # On ParseError, JSOn has not been properly deserialized, so the request ID can't be given to error response"
    assert response['id'] is None
    error = response['error']

    assert 'Parse error' in error['message']
    assert 'unable to read the request' in error['message']
    assert error['code'] == RPC_PARSE_ERROR


def test_jsrpc_invalid_params(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(JsonRpcFault) as excinfo:
        client.add(42)

    assert 'Invalid parameters' in excinfo.value.faultString
    # Python2: takes exactly 2 arguments (1 given)
    # Python3: 1 required positional argument
    assert 'argument' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INVALID_PARAMS


def test_jsrpc_invalid_params2(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(JsonRpcFault) as excinfo:
        client.add(42, -51, 98)

    assert 'Invalid parameters' in excinfo.value.faultString
    # Python2: takes exactly 2 arguments (3 given)
    # Python3: takes 2 positional arguments but 3 were given
    assert 'arguments' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INVALID_PARAMS


def test_jsrpc_internal_error(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(JsonRpcFault) as excinfo:
        client.raise_custom_exception()

    assert 'This is a test error' in excinfo.value.faultString
    assert RPC_CUSTOM_ERROR_BASE <= excinfo.value.faultCode <= RPC_CUSTOM_ERROR_MAX


def test_jsrpc_divide_by_zero(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(JsonRpcFault) as excinfo:
        client.divide(42, 0)

    assert 'Internal error' in excinfo.value.faultString
    # Python2: integer division or modulo by zero
    # Python3: division by zero
    assert 'by zero' in excinfo.value.faultString
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
