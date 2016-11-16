# coding: utf-8
import datetime
import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR

try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module


def test_xrpc_bool(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_true()

    assert type(result) == bool
    assert result is True

    result = client.get_false()

    assert type(result) == bool
    assert result is False


def test_xrpc_null(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    with pytest.raises(xmlrpc_module.Fault) as excinfo:
        client.get_null()

    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert 'cannot marshal None unless allow_none is enabled' in excinfo.value.faultString


def test_xrpc_numeric(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')

    result = client.get_int()
    assert type(result) == int
    assert result == 42

    result = client.get_negative_int()
    assert type(result) == int
    assert result == -42

    result = client.get_float()
    assert type(result) == float
    assert result == 3.14


def test_xrpc_string(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_string()

    # Unlike JSON-RPC, XML-RPC always return a str. That means the result is unicode
    # in Python 3 and ASCII in Python 2. This may be addressed in the future
    assert type(result) == str
    assert result == 'abcde'


def test_xrpc_bytes(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_bytes()

    assert result == b'abcde'


def test_xrpc_date(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_date()

    assert isinstance(result, xmlrpc_module.DateTime)
    assert '19870602' in str(result)
    assert '08:45:00' in str(result)

    try:
        # Python 3
        client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/', use_builtin_types=True)
    except TypeError:
        # Python 3
        client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/', use_datetime=True)

    result = client.get_date()

    assert isinstance(result, datetime.datetime)

    assert result.year == 1987
    assert result.month == 6
    assert result.day == 2
    assert result.hour == 8
    assert result.minute == 45
    assert result.second == 0


def test_xrpc_date_2(live_server):

    date = datetime.datetime(1990, 1, 1, 0, 0, 0)

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_date_type(date)
    assert 'datetime.datetime' in result


def test_xrpc_date_3(live_server):

    try:
        # Python 3
        client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/', use_builtin_types=True)
    except TypeError:
        # Python 3
        client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/', use_datetime=True)
    date = datetime.datetime(2000, 6, 3, 0, 0, 0)
    result = client.add_one_month(date)

    # JSON-RPC will transmit the input argument and the result as standard string
    assert result.year == 2000
    assert result.month == 7
    assert result.day == 4
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0


def test_xrpc_list(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_list()

    assert type(result) == list
    assert result == [1, 2, 3, ]


def test_xrpc_struct(live_server):

    client = xmlrpc_module.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_struct()

    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }
