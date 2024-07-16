import datetime
import xmlrpc.client

import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR

# TODO: add more tests for corner case and unsupported types: base64, bytes, nil with ALLOW_NONE = True, etc.


class TestBase:
    @pytest.mark.parametrize(
        ("method_name", "return_type", "value"),
        [
            ("get_null", type(None), None),
            ("get_true", bool, True),
            ("get_false", bool, False),
            ("get_int", int, 42),
            ("get_negative_int", int, -42),
            ("get_float", float, 3.14),
            ("get_string", str, "abcde"),
            ("get_list", list, [1, 2, 3]),
            (
                "get_struct",
                dict,
                {
                    "x": 1,
                    "y": 2,
                    "z": 3,
                },
            ),
        ],
    )
    def test_return_types(self, any_rpc_client, method_name, return_type, value):
        result = any_rpc_client.call(method_name)
        assert isinstance(result, return_type)
        assert result == value

    @pytest.mark.parametrize(
        ("arg", "expected_type"),
        [
            ("abcdef", "str"),
            (100, "int"),
            (3.12, "float"),
            ((1, 6, 9, 12, 87), "list"),
            (("x", "y", "z"), "list"),
            ([1, 6, 9, 12, 87], "list"),
            (["x", "y", "z"], "list"),
            ({"x": 55, "y": "abcd", "z": 8.5}, "dict"),
        ],
    )
    def test_input_types(self, any_rpc_client, arg, expected_type):
        assert any_rpc_client.call("get_data_type", arg) == expected_type

    @pytest.mark.skip(reason="django-modern-rpc does not support model instances results yet")
    def test_input_arg_types(self, any_rpc_client, john_doe):
        result = any_rpc_client.call("user_instance", john_doe.pk) == "str"
        assert result["username"] == john_doe.username
        assert result["email"] == john_doe.email


class TestXmlSpecific:
    def test_return_type_date(self, xmlrpc_client):
        result = xmlrpc_client.call("get_date")
        assert isinstance(result, xmlrpc.client.DateTime)
        assert not isinstance(result, datetime.datetime)
        assert result == datetime.datetime(1987, 6, 2, 8, 45, 0)

    def test_return_type_builtin_date(self, xmlrpc_client_with_builtin_types):
        result = xmlrpc_client_with_builtin_types.call("get_date")
        assert not isinstance(result, xmlrpc.client.DateTime)
        assert isinstance(result, datetime.datetime)
        assert result == datetime.datetime(1987, 6, 2, 8, 45, 0)

    def test_input_type_date(self, xmlrpc_client):
        dt = datetime.datetime(1990, 1, 1, 0, 0, 0)
        assert xmlrpc_client.call("get_data_type", dt) == "datetime"
        assert xmlrpc_client.call("get_data_type", xmlrpc.client.DateTime(dt)) == "datetime"

    def test_input_type_date_builtin(self, xmlrpc_client_with_builtin_types):
        dt = datetime.datetime(1990, 1, 1, 0, 0, 0)
        assert xmlrpc_client_with_builtin_types.call("get_data_type", dt) == "datetime"
        assert xmlrpc_client_with_builtin_types.call("get_data_type", xmlrpc.client.DateTime(dt)) == "datetime"

    def test_input_type_date_add(self, xmlrpc_client):
        base_date = datetime.datetime(2000, 6, 3, 0, 0, 0)
        result = xmlrpc_client.call("add_one_month", base_date)
        assert isinstance(result, xmlrpc.client.DateTime)
        assert result == datetime.datetime(2000, 7, 3, 0, 0, 0)

    def test_input_type_date_add_builtin(self, xmlrpc_client_with_builtin_types):
        base_date = datetime.datetime(2000, 6, 3, 0, 0, 0)
        result = xmlrpc_client_with_builtin_types.call("add_one_month", base_date)
        assert isinstance(result, datetime.datetime)
        assert result == datetime.datetime(2000, 7, 3, 0, 0, 0)

    def test_return_type_bytes(self, xmlrpc_client):
        assert xmlrpc_client.call("get_bytes") == b"abcde"

    def test_input_bytes(self, xmlrpc_client):
        assert xmlrpc_client.call("get_data_type", b"abcd") == "bytes"

    def test_input_bytes_builtin(self, xmlrpc_client_with_builtin_types):
        assert xmlrpc_client_with_builtin_types.call("get_data_type", b"abcd") == "bytes"


class TestJsonSpecific:
    def test_return_type_date(self, jsonrpc_client):
        # Unlike XML-RPC, JSON transport does not store value types, and JSON doesn't support native date type
        # Dates are transmitted as string in ISO 8601 format:
        assert jsonrpc_client.call("get_date") == "1987-06-02T08:45:00"

    def test_input_type_date(self, jsonrpc_client):
        dt = datetime.datetime(1990, 1, 1, 0, 0, 0)
        # Since date type is not supported by JSON-RPC spec, it is transported as string
        # to the server. We have to convert date to ISO 8601, since JSON-RPC cannot serialize it
        assert jsonrpc_client.call("get_data_type", dt.isoformat()) == "str"

    def test_input_type_date_add(self, jsonrpc_client):
        base_date = datetime.datetime(2000, 6, 3, 0, 0, 0)
        result = jsonrpc_client.call("add_one_month", base_date.isoformat())
        assert result == "2000-07-03T00:00:00"

    def test_return_type_bytes(self, jsonrpc_client):
        exc_match = (
            r"Unable to serialize result: "
            r"(Object of type '?bytes'? is not JSON serializable"
            r"|b'abcde' is not JSON serializable)"
        )
        with pytest.raises(jsonrpc_client.error_response_exception, match=exc_match) as exc_info:
            jsonrpc_client.call("get_bytes")
        jsonrpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)
