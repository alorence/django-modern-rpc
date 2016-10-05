# coding: utf-8
from modernrpc.tests import send_jsonrpc_request


def test_basic_add(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'add', [2, 3], req_id=45)
    assert 'error' not in response
    assert 'result' in response

    assert response['id'] == 45
    assert response['jsonrpc'] == '2.0'
    assert response['result'] == 5


def test_jsrpc_list_methods(live_server):

    method = 'system.listMethods'
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', method, req_id=64)

    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 64
    result = response['result']

    assert type(result) == list
    assert method in result
    assert len(result) > 1


def test_get_signature(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'system.getSignature', ["add"], req_id=51)
    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 51

    signature = response['result']
    # This one doesn not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'system.getSignature', ["divide"], req_id=43)
    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 43

    signature = response['result']
    # Return type + 2 parameters = 3 elements in the signature
    assert type(signature) == list
    assert len(signature) == 3
    assert signature[0] == 'int or double'
    assert signature[1] == 'int or double'
    assert signature[2] == 'int or double'
