# coding: utf-8
import json
import random

import pytest
import requests
from django.core.serializers.json import DjangoJSONEncoder
from jsonrpcclient.exceptions import ReceivedErrorResponse

from modernrpc.exceptions import RPC_INVALID_REQUEST, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR, RPC_INVALID_PARAMS, \
    RPC_CUSTOM_ERROR_BASE, RPC_CUSTOM_ERROR_MAX, RPC_INTERNAL_ERROR


def test_jsonrpc_call_unknown_method(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.non_existing_method()

    assert 'Method not found: "non_existing_method"' in excinfo.value.message
    assert excinfo.value.code == RPC_METHOD_NOT_FOUND


def test_jsonrpc_invalid_request_1(all_rpc_url):
    # Missing 'method' in payload

    headers = {'content-type': 'application/json'}
    payload = {
        # "method": 'add',
        "params": [5, 6],
        "jsonrpc": "2.0",
        "id": random.randint(1, 1000),
    }
    req_data = json.dumps(payload, cls=DjangoJSONEncoder)
    response = requests.post(all_rpc_url, data=req_data, headers=headers).json()

    assert 'Missing parameter "method"' in response['error']['message']
    assert RPC_INVALID_REQUEST == response['error']['code']


def test_jsonrpc_invalid_request_2(all_rpc_url):
    # Missing 'jsonrpc' in payload

    headers = {'content-type': 'application/json'}
    payload = {
        "method": 'add',
        "params": [5, 6],
        # "jsonrpc": "2.0",
        "id": random.randint(1, 1000),
    }
    req_data = json.dumps(payload, cls=DjangoJSONEncoder)
    response = requests.post(all_rpc_url, data=req_data, headers=headers).json()

    assert 'Missing parameter "jsonrpc"' in response['error']['message']
    assert RPC_INVALID_REQUEST == response['error']['code']


def test_jsonrpc_invalid_request_3(all_rpc_url):
    # Bad value for payload member 'jsonrpc'

    headers = {'content-type': 'application/json'}
    payload = {
        "method": 'add',
        "params": [5, 6],
        "jsonrpc": "1.0",
        "id": random.randint(1, 1000),
    }
    req_data = json.dumps(payload, cls=DjangoJSONEncoder)
    response = requests.post(all_rpc_url, data=req_data, headers=headers).json()

    assert 'jsonrpc version must be set to 2.0' in response['error']['message']
    assert RPC_INVALID_REQUEST == response['error']['code']


def test_jsonrpc_invalid_request_4(all_rpc_url):
    # Closing '}' is missing from this payload => invalid json data

    invalid_json_payload = '''
        {
            "method": "add",
            "params": [},
            "jsonrpc": "2.0",
            "id": 74
        }
    '''
    headers = {'content-type': 'application/json'}
    response = requests.post(all_rpc_url, data=invalid_json_payload, headers=headers).json()

    assert 'error' in response
    assert 'result' not in response
    # On ParseError, JSON has not been properly deserialized, so the request ID can't be returned in error response
    assert response['id'] is None
    error = response['error']

    assert 'Parse error' in error['message']
    assert 'unable to read the request' in error['message']
    assert error['code'] == RPC_PARSE_ERROR


def test_jsonrpc_invalid_request_5(all_rpc_url):
    # Json payload is not a struct or a list

    headers = {'content-type': 'application/json'}
    response = requests.post(all_rpc_url, data='10', headers=headers).json()

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] is None
    error = response['error']

    assert 'Invalid JSON-RPC payload' in error['message']
    assert error['code'] == RPC_INVALID_REQUEST


def test_jsonrpc_no_content_type(all_rpc_url):
    payload = {
        "method": "add",
        "params": [5, 6],
        "jsonrpc": "2.0",
        "id": 51,
    }
    req_data = json.dumps(payload)
    headers = {'content-type': ''}
    response = requests.post(all_rpc_url, data=req_data, headers=headers).json()

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] is None
    error = response['error']
    assert 'Missing header' in error['message']
    assert error['code'] == RPC_INVALID_REQUEST


def test_jsonrpc_invalid_params(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.add(42)

    assert 'Invalid parameters' in excinfo.value.message
    # Python2: takes exactly 2 arguments (1 given)
    # Python3: 1 required positional argument
    assert 'argument' in excinfo.value.message
    assert excinfo.value.code == RPC_INVALID_PARAMS


def test_jsonrpc_invalid_params2(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.add(42, -51, 98)

    assert 'Invalid parameters' in excinfo.value.message
    # Python2: takes exactly 2 arguments (3 given)
    # Python3: takes 2 positional arguments but 3 were given
    assert 'arguments' in excinfo.value.message
    assert excinfo.value.code == RPC_INVALID_PARAMS


def test_jsonrpc_internal_error(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.raise_custom_exception()

    assert 'This is a test error' in excinfo.value.message
    assert RPC_CUSTOM_ERROR_BASE <= excinfo.value.code <= RPC_CUSTOM_ERROR_MAX


def test_jsonrpc_exception_with_data(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.raise_custom_exception_with_data()

    assert ['a', 'b', 'c'] == excinfo.value.data


def test_jsonrpc_divide_by_zero(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.divide(42, 0)

    assert 'Internal error' in excinfo.value.message
    # Python2: integer division or modulo by zero
    # Python3: division by zero
    assert 'by zero' in excinfo.value.message
    assert excinfo.value.code == RPC_INTERNAL_ERROR


def test_jsonrpc_invalid_result(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.get_invalid_result()

    assert 'Unable to serialize result' in excinfo.value.message
    assert excinfo.value.code == RPC_INTERNAL_ERROR
