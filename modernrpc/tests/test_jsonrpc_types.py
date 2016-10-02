# coding: utf-8
import sys

from modernrpc.exceptions import RPC_INTERNAL_ERROR
from modernrpc.tests import send_jsonrpc_request


def test_jsrpc_bool(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_true')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert type(result) == bool
    assert result is True

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_false')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert type(result) == bool
    assert result is False


def test_jsrpc_null(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_null')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert result is None


def test_jsrpc_numeric(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_int')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert type(result) == int
    assert result == 42

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_negative_int')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert type(result) == int
    assert result == -42

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_float')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert type(result) == float
    assert result == 3.14


def test_jsrpc_string(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_string')

    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    # Unlike XML-RPC, JSON-RPC always return a unicode string.That means the type of the result value is
    # 'unicode' in Python 2 and 'str' in python 3. This may be addressed in the future
    try:
        # Python 2
        expected = unicode('abcde')
    except NameError:
        # Python 3
        expected = 'abcde'
    assert result == expected
    assert type(result) == type(expected)


def test_jsrpc_bytes(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_byte')

    if sys.version_info < (3, 0):

        # Python 2: no problem, returned result is a standard string...
        assert 'error' not in response
        assert 'result' in response

        # ... but json.loads will convert that string into an unicode object
        assert type(response['result']) == unicode
        assert response['result'] == 'abcde'

    else:

        # Python 3: JSON cannot transport a bytearray
        assert 'error' in response
        assert 'result' not in response

        assert response['error']['code'] == RPC_INTERNAL_ERROR


def test_jsrpc_list(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_list')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert type(result) == list
    assert result == [1, 2, 3, ]


def test_jsrpc_struct(live_server):

    response = send_jsonrpc_request(live_server.url + '/all-rpc/', 'get_struct')
    assert 'error' not in response
    assert 'result' in response
    result = response['result']

    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }
