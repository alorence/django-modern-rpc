# coding: utf-8
import json

import requests

from modernrpc.exceptions import RPC_INVALID_REQUEST, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR, RPC_INVALID_PARAMS, \
    RPC_CUSTOM_ERROR_BASE, RPC_CUSTOM_ERROR_MAX, RPC_INTERNAL_ERROR
from modernrpc.tests import send_jsonrpc_request


def test_jsrpc_call_unknown_method(live_server):

    method = "non_existing_medthod"
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', method, req_id=51)

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] == 51
    error = response['error']

    assert 'Method not found: ' + method in error['message']
    assert error['code'] == RPC_METHOD_NOT_FOUND


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

    method = "add"
    params = [42]
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', method, params, req_id=-12)

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] == -12
    error = response['error']

    assert 'Invalid parameters' in error['message']
    # Python2: takes exactly 2 arguments (1 given)
    # Python3: 1 required positional argument
    assert "argument" in error['message']
    assert error['code'] == RPC_INVALID_PARAMS


def test_jsrpc_invalid_params2(live_server):

    method = "add"
    params = [42, -51, 98]
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', method, params, req_id=51)

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] == 51
    error = response['error']

    assert 'Invalid parameters' in error['message']
    # Python2: takes exactly 2 arguments (3 given)
    # Python3: takes 2 positional arguments but 3 were given
    assert "arguments" in error['message']
    assert error['code'] == RPC_INVALID_PARAMS


def test_jsrpc_internal_error(live_server):
    method = "raise_custom_exception"
    params = []
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', method, params, req_id=22)

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] == 22
    error = response['error']

    assert "This is a test error" in error['message']
    assert RPC_CUSTOM_ERROR_BASE <= error['code'] <= RPC_CUSTOM_ERROR_MAX


def test_jsrpc_divide_by_zero(live_server):
    method = "divide"
    params = [42, 0]
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', method, params, req_id=44)

    assert 'error' in response
    assert 'result' not in response
    assert response['id'] == 44
    error = response['error']

    assert 'Internal error' in error['message']
    # Python2: integer division or modulo by zero
    # Python3: division by zero
    assert "by zero" in error['message']
    assert error['code'] == RPC_INTERNAL_ERROR
