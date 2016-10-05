# coding: utf-8
from modernrpc.tests import send_jsonrpc_request


def test_jsrpc_list_methods(live_server):

    method = 'system.listMethods'
    response = send_jsonrpc_request(live_server.url + '/all-rpc/', method)

    assert 'result' in response
    result = response['result']

    assert type(result) == list
    assert method in result
    assert len(result) > 1


def test_basic_add(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'add', [2, 3], req_id=45)

    assert response['id'] == 45
    assert response['jsonrpc'] == '2.0'
    assert response['result'] == 5
