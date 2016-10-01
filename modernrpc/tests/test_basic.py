# coding: utf-8
import json
try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module
import requests


def send_jsonrpc_request(url, method, params=(), req_id=42, return_json=True):
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


def test_xml_basic_add(live_server):
    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    assert client.add(2, 3) == 5


def test_json_basic_add(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'add', [2, 3], req_id=45)

    assert response['id'] == 45
    assert response['jsonrpc'] == '2.0'
    assert response['result'] == 5

