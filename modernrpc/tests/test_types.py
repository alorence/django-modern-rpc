# coding: utf-8
import datetime
import re
import sys

import django.utils.six as six
import pytest
from django.utils.six import text_type
from django.utils.six.moves import xmlrpc_client
from jsonrpcclient.exceptions import ReceivedErrorResponse
from jsonrpcclient.http_client import HTTPClient

from modernrpc.exceptions import RPC_INTERNAL_ERROR


def test_xmlrpc_bool(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_true()

    assert type(result) == bool
    assert result is True

def test_xmlrpc_bool_2(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_false()

    assert type(result) == bool
    assert result is False

def test_jsonrpc_bool(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    result = c.get_true()

    assert type(result) == bool
    assert result is True

def test_jsonrpc_bool_2(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    result = c.get_false()

    assert type(result) == bool
    assert result is False


def test_xmlrpc_null(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    assert c.get_null() is None

def test_jsonrpc_null(live_server):
    c = HTTPClient(live_server.url + '/all-rpc/')

    result = c.get_null()
    assert result is None


def test_xmlrpc_numeric(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    result = c.get_int()
    assert type(result) == int
    assert result == 42

def test_xmlrpc_numeric_2(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    result = c.get_negative_int()
    assert type(result) == int
    assert result == -42

def test_xmlrpc_numeric_3(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    result = c.get_float()
    assert type(result) == float
    assert result == 3.14

def test_jsonrpc_numeric(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    result = c.get_int()
    assert type(result) == int
    assert result == 42

def test_jsonrpc_numeric_2(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    result = c.get_negative_int()
    assert type(result) == int
    assert result == -42

def test_jsonrpc_numeric_3(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    result = c.get_float()
    assert type(result) == float
    assert result == 3.14


def test_xmlrpc_string(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_string()

    # Unlike JSON-RPC, XML-RPC always return a str. That means the result is unicode
    # in Python 3 and ASCII in Python 2. This may be addressed in the future
    assert type(result) == str
    assert result == 'abcde'

def test_jsonrpc_string(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    result = c.get_string()

    # Unlike XML-RPC, JSON-RPC always return a unicode string. That means the type of the result value is
    # 'unicode' in Python 2 and 'str' in python 3. This may be addressed in the future
    expected = text_type('abcde')

    assert result == expected
    assert type(result) == type(expected)


def test_xmlrpc_input_string(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_data_type('abcd')

    # Python 2 : "<type 'str'>"
    # Python 3 : "<class 'str'>"
    assert re.match(r"<(class|type) 'str'>", result)

def test_jsonrpc_input_string(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    result = c.get_data_type('abcd')

    # Python 2 : "<type 'unicode'>"
    # Python 3 : "<class 'str'>"
    if six.PY2:
        assert "<type 'unicode'>" == result
    else:
        assert "<class 'str'>" == result


def test_xmlrpc_bytes(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_bytes()

    assert result == b'abcde'

def test_jsonrpc_bytes(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    if sys.version_info < (3, 0):

        # Python 2: no problem, returned result is a standard string...
        result = c.get_bytes()

        # ... but json.loads will convert that string into an unicode object
        assert type(result) == text_type
        assert result == 'abcde'

    else:

        # Python 3: JSON cannot transport a bytearray
        with pytest.raises(ReceivedErrorResponse) as excinfo:
            c.get_bytes()

        assert excinfo.value.code == RPC_INTERNAL_ERROR


def test_xmlrpc_date(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_date()

    assert isinstance(result, xmlrpc_client.DateTime)
    assert '19870602' in str(result)
    assert '08:45:00' in str(result)


def test_xmlrpc_date_2(live_server):
    try:
        # Python 3
        c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_builtin_types=True)
    except TypeError:
        # Python 3
        c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_datetime=True)

    result = c.get_date()

    assert isinstance(result, datetime.datetime)

    assert result.year == 1987
    assert result.month == 6
    assert result.day == 2
    assert result.hour == 8
    assert result.minute == 45
    assert result.second == 0


def test_xmlrpc_date_3(live_server):

    date = datetime.datetime(1990, 1, 1, 0, 0, 0)

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_data_type(date)

    # Python 2 : "<type 'datetime.datetime'>"
    # Python 3 : "<class 'datetime.datetime'>"
    assert re.match(r"<(class|type) 'datetime.datetime'>", result)


def test_xmlrpc_date_4(live_server):

    try:
        # Python 3
        c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_builtin_types=True)
    except TypeError:
        # Python 3
        c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_datetime=True)
    date = datetime.datetime(2000, 6, 3, 0, 0, 0)
    result = c.add_one_month(date)

    # JSON-RPC will transmit the input argument and the result as standard string
    assert result.year == 2000
    assert result.month == 7
    assert result.day == 4
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0



def test_jsonrpc_date(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    result = c.get_date()

    # Unlike XML-RPC, JSON transport does not store value types.
    # Dates are transmitted as string in ISO 8601 format:
    assert '1987-06-02' in result
    assert '08:45:00' in result

def test_jsonrpc_date_2(live_server):
    c = HTTPClient(live_server.url + '/all-rpc/')
    date = datetime.datetime(1990, 1, 1, 0, 0, 0)
    # We have to convert date to ISO 8601, since JSON-RPC cannot serialize it
    result = c.get_data_type(date.isoformat())

    # Since data type are not included in JSON-RPC request, dates are transmitter as string
    # to the server. The decoded type depends on the Python version used
    if sys.version_info < (3, 0):
        # Python 2 : "<type 'unicode'>"
        assert "<type 'unicode'>" == result
    else:
        # Python 3 : "<class 'str'>"
        assert "<class 'str'>" == result


def test_jsonrpc_date_3(live_server):
    c = HTTPClient(live_server.url + '/all-rpc/')
    date = datetime.datetime(2000, 6, 3, 0, 0, 0)
    # We have to convert date to ISO 8601, since JSON-RPC cannot serialize it
    result = c.add_one_month(date.isoformat())

    # JSON-RPC will transmit the input argument and the result as standard string
    assert '2000-07-04' in result


def test_xmlrpc_list(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_list()

    assert type(result) == list
    assert result == [1, 2, 3, ]

def test_jsonrpc_list(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    result = c.get_list()

    assert type(result) == list
    assert result == [1, 2, 3, ]


def test_xmlrpc_struct(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = c.get_struct()

    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }

def test_jsonrpc_struct(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    result = c.get_struct()

    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }
