# coding: utf-8
import sys
from modernrpc.exceptions import RPC_METHOD_NOT_FOUND
from modernrpc.tests import send_jsonrpc_request


def test_jsrpc_basic_add(live_server):

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


def test_jsrpc_system_get_signature(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'system.methodSignature', ["add"], req_id=51)
    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 51

    signature = response['result']
    # This one doesn not have any docstring defined
    assert type(signature) == list
    assert len(signature) == 0

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'system.methodSignature', ["divide"], req_id=43)
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


def test_jsrpc_method_help(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'system.methodHelp', ["add"], req_id=54)
    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 54

    help = response['result']
    if sys.version_info < (3, 0):
        assert type(help) == unicode  # noqa: F821
    else:
        assert type(help) == str
    assert help == ''

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'system.methodHelp', ["divide"], req_id=54)
    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 54

    help = response['result']
    assert 'Divide a numerator by a denominator' in help


def test_jsrpc_only_method(live_server):

    response = send_jsonrpc_request(live_server.url + '/json-only/', 'system.listMethods', req_id=94)
    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 94

    methods_list = response['result']
    assert 'method_x' in methods_list
    assert 'method_y' not in methods_list

    # method_x is available only via JSON-RPC
    response = send_jsonrpc_request(live_server.url + '/json-only/', 'method_x', req_id=78)
    assert 'error' not in response
    assert 'result' in response
    assert response['id'] == 78

    result = response['result']
    assert result == 'JSON only'

    # method_y is available only via XML-RPC
    response = send_jsonrpc_request(live_server.url + '/json-only/', 'method_y', req_id=321)
    assert 'error' in response
    assert 'result' not in response
    assert response['id'] == 321

    error = response['error']

    assert 'Method not found: method_y' in error['message']
    assert error['code'] == RPC_METHOD_NOT_FOUND


def test_xrpc_only_internal_error(live_server):

    response = send_jsonrpc_request(live_server.url + '/xml-only/', 'system.listMethods', return_json=False)
    assert 'Unable to handle your request. Please ensure you called the right entry point' in str(response.content)
