# coding: utf-8
import json

import requests


def send_jsonrpc_request(url, method, params=(), req_id=42, return_json=True):
    """Helper used to simulate a JSON-RPC request"""
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": req_id,
    }
    req_data = json.dumps(payload)
    response = requests.post(url, data=req_data, headers=headers)
    if return_json:
        return response.json()
    return response


def test_basic_add(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'add', [2, 3], req_id=45)

    assert response['id'] == 45
    assert response['jsonrpc'] == '2.0'
    assert response['result'] == 5


def test_basic_types(live_server):
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'basic_types')
    result = response['result']

    assert isinstance(result['bool'], bool)
    assert result['bool'] is True

    assert isinstance(result['int'], int)
    assert result['int'] == 42

    assert isinstance(result['float'], float)
    assert result['float'] == 51.2

    assert isinstance(result['string'], str)
    assert result['string'] == 'abcde'

    assert isinstance(result['list'], list)
    assert result['list'] == [1, 2, 3]

    assert isinstance(result['struct'], dict)
    assert result['struct'] == {'a': 6, 'b': 21}
