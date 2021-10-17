# coding: utf-8
import datetime

import pytest
from jsonrpcclient.exceptions import ReceivedErrorResponse

from modernrpc.exceptions import RPC_INTERNAL_ERROR
from tests import xmlrpclib


def test_xmlrpc_bool(xmlrpc_client):
    result = xmlrpc_client.get_true()
    assert type(result) == bool
    assert result is True


def test_jsonrpc_bool(jsonrpc_client):
    result = jsonrpc_client.get_true()
    assert type(result) == bool
    assert result is True


def test_xmlrpc_bool_2(xmlrpc_client):
    result = xmlrpc_client.get_false()
    assert type(result) == bool
    assert result is False


def test_jsonrpc_bool_2(jsonrpc_client):
    result = jsonrpc_client.get_false()
    assert type(result) == bool
    assert result is False


def test_xmlrpc_null(xmlrpc_client):
    assert xmlrpc_client.get_null() is None


def test_jsonrpc_null(jsonrpc_client):
    result = jsonrpc_client.get_null()
    assert result is None


def test_xmlrpc_int(xmlrpc_client):
    result = xmlrpc_client.get_int()
    assert type(result) == int
    assert result == 42


def test_jsonrpc_int(jsonrpc_client):
    result = jsonrpc_client.get_int()
    assert type(result) == int
    assert result == 42


def test_xmlrpc_int_negative(xmlrpc_client):
    result = xmlrpc_client.get_negative_int()
    assert type(result) == int
    assert result == -42


def test_jsonrpc_int_negative(jsonrpc_client):
    result = jsonrpc_client.get_negative_int()
    assert type(result) == int
    assert result == -42


def test_xmlrpc_float(xmlrpc_client):
    result = xmlrpc_client.get_float()
    assert type(result) == float
    assert result == 3.14


def test_jsonrpc_float(jsonrpc_client):
    result = jsonrpc_client.get_float()
    assert type(result) == float
    assert result == 3.14


def test_xmlrpc_string(xmlrpc_client):
    result = xmlrpc_client.get_string()
    assert type(result) == str
    assert result == 'abcde'


def test_jsonrpc_string(jsonrpc_client):
    result = jsonrpc_client.get_string()
    assert type(result) == str
    assert result == 'abcde'


def test_xmlrpc_input_string(xmlrpc_client):
    assert xmlrpc_client.get_data_type('abcd') == "<class 'str'>"


def test_jsonrpc_input_string(jsonrpc_client):
    assert jsonrpc_client.get_data_type('abcd') == "<class 'str'>"


def test_xmlrpc_bytes(xmlrpc_client):
    result = xmlrpc_client.get_bytes()
    assert result == b'abcde'


def test_jsonrpc_bytes(jsonrpc_client):
    with pytest.raises(ReceivedErrorResponse) as excinfo:
        jsonrpc_client.get_bytes()

    assert excinfo.value.code == RPC_INTERNAL_ERROR


def test_xmlrpc_date(xmlrpc_client):
    result = xmlrpc_client.get_date()

    assert isinstance(result, xmlrpclib.DateTime)
    assert '19870602' in str(result)
    assert '08:45:00' in str(result)


def test_xmlrpc_date_2(all_rpc_url):
    try:
        # Python 3
        client = xmlrpclib.ServerProxy(all_rpc_url, use_builtin_types=True)
    except TypeError:
        # Python 3
        client = xmlrpclib.ServerProxy(all_rpc_url, use_datetime=True)

    result = client.get_date()

    assert isinstance(result, datetime.datetime)

    assert result.year == 1987
    assert result.month == 6
    assert result.day == 2
    assert result.hour == 8
    assert result.minute == 45
    assert result.second == 0


def test_xmlrpc_date_3(xmlrpc_client):
    date = datetime.datetime(1990, 1, 1, 0, 0, 0)
    result = xmlrpc_client.get_data_type(date)
    assert result == "<class 'datetime.datetime'>"


def test_xmlrpc_date_4(all_rpc_url):
    client = xmlrpclib.ServerProxy(all_rpc_url, use_builtin_types=True)

    base_date = datetime.datetime(2000, 6, 3, 0, 0, 0)
    result = client.add_one_month(base_date)

    # JSON-RPC will transmit the input argument and the result as standard string
    assert result.year == 2000
    assert result.month == 7
    assert result.day == 4
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0


def test_jsonrpc_date(jsonrpc_client):
    result = jsonrpc_client.get_date()
    # Unlike XML-RPC, JSON transport does not store value types.
    # Dates are transmitted as string in ISO 8601 format:
    assert '1987-06-02' in result
    assert '08:45:00' in result


def test_jsonrpc_date_2(jsonrpc_client):
    date = datetime.datetime(1990, 1, 1, 0, 0, 0)

    # Since date type is not supported by JSON-RPC spec, it is transported as string
    # to the server. We have to convert date to ISO 8601, since JSON-RPC cannot serialize it
    assert jsonrpc_client.get_data_type(date.isoformat()) == "<class 'str'>"


def test_jsonrpc_date_3(jsonrpc_client):
    date = datetime.datetime(2000, 6, 3, 0, 0, 0)

    # We have to convert date to ISO 8601, since JSON-RPC cannot serialize it
    result = jsonrpc_client.add_one_month(date.isoformat())

    # JSON-RPC will transmit the input argument and the result as standard string
    assert '2000-07-04' in result


def test_xmlrpc_list(xmlrpc_client):
    result = xmlrpc_client.get_list()
    assert type(result) == list
    assert result == [1, 2, 3]


def test_jsonrpc_list(jsonrpc_client):
    result = jsonrpc_client.get_list()
    assert type(result) == list
    assert result == [1, 2, 3]


def test_xmlrpc_struct(xmlrpc_client):
    result = xmlrpc_client.get_struct()
    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }


def test_jsonrpc_struct(jsonrpc_client):
    result = jsonrpc_client.get_struct()
    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }


@pytest.mark.skip(msg="django-modern-rpc is not ready yet to support model instances results")
def test_xmlrpc_model_instance(xmlrpc_client, john_doe):
    result = xmlrpc_client.user_instance(john_doe.pk)

    # XML serialisation returns an object as dict
    assert result["username"] == john_doe.username
    assert result["email"] == john_doe.email


@pytest.mark.skip(msg="django-modern-rpc is not ready yet to support model instances results")
def test_jsonrpc_model_instance(jsonrpc_client, john_doe):
    result = jsonrpc_client.user_instance(john_doe.pk)

    # XML serialisation returns an object as dict
    assert result["username"] == john_doe.username
    assert result["email"] == john_doe.email
