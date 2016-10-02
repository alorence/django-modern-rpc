# coding: utf-8
from modernrpc.tests import send_jsonrpc_request


def test_jsrpc_bool(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_true')
    result = response['result']

    assert type(result) == bool
    assert result is True

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_false')
    result = response['result']

    assert type(result) == bool
    assert result is False


def test_jsrpc_null(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_null')
    result = response['result']

    assert result is None


def test_jsrpc_numeric(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_int')
    result = response['result']

    assert type(result) == int
    assert result == 42

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_negative_int')
    result = response['result']

    assert type(result) == int
    assert result == -42

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_float')
    result = response['result']

    assert type(result) == float
    assert result == 3.14


