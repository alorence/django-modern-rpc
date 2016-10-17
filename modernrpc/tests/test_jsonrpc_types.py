# coding: utf-8
import sys

import datetime
import pytest

from dummy_jsonrpc_client import ServerProxy, JsonRpcFault
from modernrpc.exceptions import RPC_INTERNAL_ERROR


def test_jsrpc_bool(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_true()

    assert type(result) == bool
    assert result is True

    result = client.get_false()

    assert type(result) == bool
    assert result is False


def test_jsrpc_null(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    result = client.get_null()
    assert result is None


def test_jsrpc_numeric(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')

    result = client.get_int()
    assert type(result) == int
    assert result == 42

    result = client.get_negative_int()
    assert type(result) == int
    assert result == -42

    result = client.get_float()
    assert type(result) == float
    assert result == 3.14


def test_jsrpc_string(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_string()

    # Unlike XML-RPC, JSON-RPC always return a unicode string. That means the type of the result value is
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

    client = ServerProxy(live_server.url + '/all-rpc/')

    if sys.version_info < (3, 0):

        # Python 2: no problem, returned result is a standard string...
        result = client.get_byte()

        # ... but json.loads will convert that string into an unicode object
        assert type(result) == unicode  # noqa: F821
        assert result == 'abcde'

    else:

        # Python 3: JSON cannot transport a bytearray
        with pytest.raises(JsonRpcFault) as excinfo:
            client.get_byte()

        assert excinfo.value.faultCode == RPC_INTERNAL_ERROR


def test_jsrpc_date(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_date()

    # Unlike XML-RPC, JSON transport does not store value types.
    # Dates are transmitted as string in ISO 8601 format:
    assert '1987-06-02' in result
    assert '08:45:00' in result


def test_jsrpc_date_2(live_server):
    client = ServerProxy(live_server.url + '/all-rpc/')
    date = datetime.datetime(1990, 1, 1, 0, 0, 0)
    result = client.get_date_type(date)

    # Since data type are not included in JSON-RPC request, dates are transmitter as string
    # to the server. The decoded type depends on the Python version used
    if sys.version_info < (3, 0):
        assert 'unicode' in result
    else:
        assert 'str' in result


def test_jsrpc_date_3(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')
    date = datetime.datetime(2000, 6, 3, 0, 0, 0)
    result = client.add_one_month(date)

    # JSON-RPC will transmit the input argument and the result as standard string
    assert '2000-07-04' in result


def test_jsrpc_list(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_list()

    assert type(result) == list
    assert result == [1, 2, 3, ]


def test_jsrpc_struct(live_server):

    client = ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_struct()

    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }
