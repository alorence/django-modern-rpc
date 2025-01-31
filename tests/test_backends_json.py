import json
import random
from datetime import datetime

import pytest
from helpers import assert_json_data_are_equal

from modernrpc.exceptions import RPCInternalError, RPCInvalidRequest, RPCParseError
from modernrpc.handlers.base import JsonRpcErrorResult, JsonRpcRequest, JsonRpcSuccessResult


class TestJsonRpcDeserializer:
    """
    This class will test the JsonRpcDeserializer classes.
    It will ensure that a given request payload is parsed correctly and the extracted data
    have correct type and value
    """

    def test_method_name_no_params(self, json_deserializer):
        payload = """{
          "id": 255,
          "jsonrpc": "2.0",
          "method": "foo"
        }
        """
        request = json_deserializer.loads(payload)
        assert request.jsonrpc == "2.0"
        assert request.request_id == 255
        assert request.is_notification is False
        assert request.method_name == "foo"
        assert request.args == []
        assert request.kwargs == {}

    def test_method_name_null_params(self, json_deserializer):
        payload = """{
          "id": 255,
          "jsonrpc": "2.0",
          "method": "foo",
          "params": null
        }
        """
        request = json_deserializer.loads(payload)
        assert request.jsonrpc == "2.0"
        assert request.request_id == 255
        assert request.is_notification is False
        assert request.method_name == "foo"
        assert request.args == []
        assert request.kwargs == {}

    def test_args(self, json_deserializer):
        payload = """{
          "id": null,
          "jsonrpc": "2.0",
          "method": "foo",
          "params": [55, 74.2, false, true]
        }
        """
        request = json_deserializer.loads(payload)
        assert request.jsonrpc == "2.0"
        assert request.request_id is None
        assert request.is_notification is False
        assert request.method_name == "foo"
        assert request.args == [55, 74.2, False, True]
        assert request.kwargs == {}

    def test_kwargs(self, json_deserializer):
        payload = """{
          "id": "33",
          "jsonrpc": "2.0",
          "method": "foo.bar.baz",
          "params": {
            "foo": null,
            "a": 123.5,
            "b": "foo-bar!"
          }
        }
        """
        request = json_deserializer.loads(payload)
        assert request.jsonrpc == "2.0"
        assert request.request_id == "33"
        assert request.is_notification is False
        assert request.method_name == "foo.bar.baz"
        assert request.args == []
        assert request.kwargs == {"foo": None, "a": 123.5, "b": "foo-bar!"}

    @pytest.mark.parametrize(
        ("value", "expected_value"),
        [
            ("true", True),
            ("false", False),
            ("-1", -1),
            ("0", 0),
            ("999", 999),
            ("33.9", 33.9),
            ("-3.14", -3.14),
            ('"foo"', "foo"),
            ('"💗💗💗-💗💗💗"', "💗💗💗-💗💗💗"),
            ('"foo.bar\\n  baz"', "foo.bar\n  baz"),
            ("[0]", [0]),
            ('["foo", "bar", 88, 99, 3.14]', ["foo", "bar", 88, 99, 3.14]),
            ('{"pi": 3.14}', {"pi": 3.14}),
            ('{"π": 3.14159}', {"π": 3.14159}),
        ],
    )
    @pytest.mark.parametrize("is_kwargs", [True, False])
    def test_arg_scalar(self, json_deserializer, value, expected_value, is_kwargs):
        if is_kwargs:
            params = f'{{"arg1": {value}}}'
            expected_args = []
            expected_kwargs = {"arg1": expected_value}
        else:
            params = f"[{value}]"
            expected_args = [expected_value]
            expected_kwargs = {}

        payload = f"""{{
          "jsonrpc": "2.0",
          "id": 128,
          "method": "hello",
          "params": {params}
        }}"""
        request = json_deserializer.loads(payload)
        assert request.args == expected_args
        assert request.kwargs == expected_kwargs

    @pytest.mark.parametrize(
        ("value", "expected_value"),
        [
            ("true", True),
            ("false", False),
            ("-1", -1),
            ("0", 0),
            ("999", 999),
            ("33.9", 33.9),
            ("-3.14", -3.14),
            ('"foo"', "foo"),
            ('"💗💗💗-💗💗💗"', "💗💗💗-💗💗💗"),
            ('"foo.bar\\n  baz"', "foo.bar\n  baz"),
            ("[0]", [0]),
            ('["foo", "bar", 88, 99, 3.14]', ["foo", "bar", 88, 99, 3.14]),
            ('{"pi": 3.14}', {"pi": 3.14}),
            ('{"π": 3.14159}', {"π": 3.14159}),
        ],
    )
    @pytest.mark.parametrize("is_kwargs", [True, False])
    def test_notification(self, json_deserializer, value, expected_value, is_kwargs):
        if is_kwargs:
            params = f'{{"arg1": {value}}}'
            expected_args = []
            expected_kwargs = {"arg1": expected_value}
        else:
            params = f"[{value}]"
            expected_args = [expected_value]
            expected_kwargs = {}

        payload = f"""{{
          "jsonrpc": "2.0",
          "method": "hello",
          "params": {params}
        }}"""
        request = json_deserializer.loads(payload)
        assert request.args == expected_args
        assert request.kwargs == expected_kwargs

    def test_multicall(self, json_deserializer):
        payload = """
        [
          {"jsonrpc": "2.0", "id": 33, "method": "foo", "params": {"a": 5, "b": null}},
          {"jsonrpc": "2.0", "method": "bar", "params": ["abcd", 123.5]}
        ]
        """
        requests = json_deserializer.loads(payload)
        assert isinstance(requests, list)
        assert len(requests) == 2

        assert requests[0].jsonrpc == "2.0"
        assert requests[0].method_name == "foo"
        assert requests[0].request_id == 33
        assert requests[0].args == []
        assert requests[0].kwargs == {"a": 5, "b": None}

        assert requests[1].jsonrpc == "2.0"
        assert requests[1].method_name == "bar"
        assert requests[1].is_notification is True
        assert requests[1].args == ["abcd", 123.5]
        assert requests[1].kwargs == {}

    def test_invalid_json_payload(self, json_deserializer):
        payload = """{
          "id]: 255,
          "jsonrpc": "2.0",
          "method": "foo",
          "params": null
        }
        """
        with pytest.raises(RPCParseError):
            json_deserializer.loads(payload)

    def test_missing_method_name(self, json_deserializer):
        payload = """{
          "id": 255,
          "jsonrpc": "2.0",
          "params": [5]
        }
        """
        with pytest.raises(RPCInvalidRequest):
            json_deserializer.loads(payload)

    def test_missing_jsonrpc(self, json_deserializer):
        payload = """{
          "id": 255,
          "method": "foo",
          "params": [5]
        }
        """
        with pytest.raises(RPCInvalidRequest):
            json_deserializer.loads(payload)

    @pytest.mark.parametrize(
        "request_id",
        [
            "{}",
            '{"x": "y"}',
            "[]",
            "[1, 2, 3]",
        ],
    )
    def test_invalid_request_id_type(self, json_deserializer, request_id):
        payload = f"""{{
          "id": {request_id},
          "jsonrpc": "2.0",
          "method": "foo",
          "params": [5]
        }}
        """
        with pytest.raises(RPCInvalidRequest):
            json_deserializer.loads(payload)


class TestJsonRpcSerializer:
    notif = JsonRpcRequest(method_name="webhook")
    req0 = JsonRpcRequest(request_id=None, method_name="foo")
    req1 = JsonRpcRequest(request_id="1", method_name="bar")
    req2 = JsonRpcRequest(request_id=2, method_name="foo.bar")

    @pytest.mark.parametrize(
        ("data", "expected_result"),
        [
            (None, "null"),
            (True, "true"),
            (False, "false"),
            (-85, "-85"),
            (0, "0"),
            (5, "5"),
            (-3.14159, "-3.14159"),
            (3.14159, "3.14159"),
            ("foo", '"foo"'),
            ("foo.bar\n  baz", '"foo.bar\\n  baz"'),
            ("💗💗💗-💗💗💗", '"💗💗💗-💗💗💗"'),
            ([0], "[0]"),
            (["foo", "bar", 88, 99, 3.14], '["foo", "bar", 88, 99, 3.14]'),
            ({"pi": 3.14159}, '{"pi": 3.14159}'),
            ({"π": 3.14159}, '{"π": 3.14159}'),
        ],
    )
    def test_success_result_scalar(self, json_serializer, data, expected_result):
        request_id = random.choice([None, "1", "2", "3", 4, 5, 6])
        result = JsonRpcSuccessResult(request=JsonRpcRequest(request_id=request_id, method_name=""), data=data)
        expected = f"""{{
          "id": {json.dumps(request_id)},
          "jsonrpc": "2.0",
          "result": {expected_result}
        }}"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    @pytest.mark.parametrize(
        ("data", "expected_result"),
        [
            (None, "null"),
            (True, "true"),
            (False, "false"),
            (-85, "-85"),
            (0, "0"),
            (5, "5"),
            (-3.14159, "-3.14159"),
            (3.14159, "3.14159"),
            ("foo", '"foo"'),
            ("foo.bar\n  baz", '"foo.bar\\n  baz"'),
            ("💗💗💗-💗💗💗", '"💗💗💗-💗💗💗"'),
            ([0], "[0]"),
            (["foo", "bar", 88, 99, 3.14], '["foo", "bar", 88, 99, 3.14]'),
            ({"pi": 3.14159}, '{"pi": 3.14159}'),
            ({"π": 3.14159}, '{"π": 3.14159}'),
        ],
    )
    def test_notification_result(self, json_serializer, data, expected_result):
        result = JsonRpcSuccessResult(request=self.notif)
        expected = "null"
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_result_batch(self, json_serializer):
        results = [
            JsonRpcSuccessResult(request=self.req0, data=[10, 20, 30]),
            JsonRpcSuccessResult(request=self.notif),
            JsonRpcSuccessResult(request=self.req1, data="abcd"),
        ]
        expected = """
        [
          {"id": null, "jsonrpc": "2.0", "result": [10, 20, 30]},
          null,
          {"id": "1", "jsonrpc": "2.0", "result": "abcd"}
        ]
        """
        assert_json_data_are_equal(json_serializer.dumps(results), expected)

    @pytest.mark.parametrize(
        "value",
        [
            datetime(2025, 1, 2, 4, 5, 6),
            b"foo\x98",
        ],
    )
    def test_result_unsupported_type(self, json_serializer, value):
        result = JsonRpcSuccessResult(request=self.req1, data=value)
        with pytest.raises(RPCInternalError) as e:
            json_serializer.dumps(result)
        assert "Could not serialize JsonRpcSuccessResult" in e.value.message

    def test_result_error(self, json_serializer):
        result = JsonRpcErrorResult(request=self.req0, code=-65000, message="foo")
        expected = """{
            "id": null,
            "jsonrpc": "2.0",
            "error": {
                "code": -65000,
                "message": "foo"
            }
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_result_error_with_data(self, json_serializer):
        error_data = {"reason": "foo", "exception": "ValueError"}
        result = JsonRpcErrorResult(request=self.req1, code=65000, message="bar", data=error_data)
        expected = """{
            "id": "1",
            "jsonrpc": "2.0",
            "error": {
                "code": 65000,
                "message": "bar",
                "data": {
                    "reason": "foo",
                    "exception": "ValueError"
                }
            }
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)
