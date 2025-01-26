from datetime import datetime

import pytest
from helpers import assert_json_data_are_equal

from modernrpc.exceptions import RPCInternalError, RPCInvalidRequest, RPCParseError
from modernrpc.handlers.base import JsonRpcErrorResult, JsonRpcRequest, JsonRpcSuccessResult


class TestJsonDeserializer:
    """
    This class will test the JsonRpcDeserializer classes.
    It will ensure that a given request payload is parsed correctly and the extracted data
    have correct type and value
    """

    def test_method_name_no_params(self, json_deserializer):
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

    def test_int_args(self, json_deserializer):
        payload = """{
          "id": "20",
          "jsonrpc": "2.0",
          "method": "hello",
          "params": [-1, 0, -3, 9, 199855547225]
        }"""
        request = json_deserializer.loads(payload)
        assert request.args == [-1, 0, -3, 9, 199855547225]

    def test_float_args(self, json_deserializer):
        payload = """{
          "id": "20",
          "jsonrpc": "2.0",
          "method": "hello",
          "params": [-6.2, 9.4, 123456789.123456789]
        }"""
        request = json_deserializer.loads(payload)
        assert request.args == [-6.2, 9.4, 123456789.123456789]

    def test_notification(self, json_deserializer):
        payload = """{
          "jsonrpc": "2.0",
          "method": "💗",
          "params": {
            "a": [1, 3, 5, "foo", 954.3],
            "b": {"x": 0, "y": false}
          }
        }
        """
        request = json_deserializer.loads(payload)
        assert request.jsonrpc == "2.0"
        assert request.is_notification is True
        assert request.method_name == "💗"
        assert request.args == []
        assert request.kwargs == {
            "a": [1, 3, 5, "foo", 954.3],
            "b": {"x": 0, "y": False},
        }

    def test_multicall(self, json_deserializer):
        payload = """
        [
          {"jsonrpc": "2.0", "id": 33, "method": "foo", "params": {"a": 5, "b": null}},
          {"jsonrpc": "2.0", "method": "bar", "params": ["abcd", 123.5]}
        ]
        """
        requests = json_deserializer.loads(payload)
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


class TestJsonDeserializerErrors:
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


class TestJsonSerializer:
    notif = JsonRpcRequest(method_name="webhook")
    req0 = JsonRpcRequest(request_id=None, method_name="foo")
    req1 = JsonRpcRequest(request_id="1", method_name="bar")
    req2 = JsonRpcRequest(request_id=2, method_name="foo.bar")

    def test_result_none(self, json_serializer):
        result = JsonRpcSuccessResult(request=self.req0, data=None)
        expected = """{
            "id": null,
            "jsonrpc": "2.0",
            "result": null
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    @pytest.mark.parametrize(("py_val", "json_val"), [(True, "true"), (False, "false")])
    def test_result_bool(self, json_serializer, py_val, json_val):
        result = JsonRpcSuccessResult(request=self.req1, data=py_val)
        expected = (
            """{
                "id": "1",
                "jsonrpc": "2.0",
                "result": %s
            }"""  # noqa: UP031
            % json_val
        )
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_result_int(self, json_serializer):
        result = JsonRpcSuccessResult(request=self.req2, data=123)
        expected = """{
            "id": 2,
            "jsonrpc": "2.0",
            "result": 123
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_result_str(self, json_serializer):
        result = JsonRpcSuccessResult(request=self.req2, data="9999")
        expected = """{
            "id": 2,
            "jsonrpc": "2.0",
            "result": "9999"
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_result_float(self, json_serializer):
        result = JsonRpcSuccessResult(request=self.req1, data=3.14)
        expected = """{
            "id": "1",
            "jsonrpc": "2.0",
            "result": 3.14
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_result_list(self, json_serializer):
        result = JsonRpcSuccessResult(request=self.req0, data=[10, 20, 30])
        expected = """{
            "id": null,
            "jsonrpc": "2.0",
            "result": [
                10, 20, 30
            ]
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_result_dict(self, json_serializer):
        res = {
            "foo": "bar",
            "bar": "baz",
            "array": [1, 2, 3],
            "is_empty": True,
            "data": {
                "foo": "bar",
                "tic": "tac",
                "hello": None,
            },
        }
        result = JsonRpcSuccessResult(request=self.req0, data=res)
        expected = """{
            "id": null,
            "jsonrpc": "2.0",
            "result": {
                "array": [1, 2, 3],
                "bar": "baz",
                "data": {"foo": "bar", "hello": null, "tic": "tac"},
                "foo": "bar",
                "is_empty": true
            }
        }"""
        assert_json_data_are_equal(json_serializer.dumps(result), expected)

    def test_notification_result(self, json_serializer):
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

    def test_result_datetime(self, json_serializer):
        result = JsonRpcSuccessResult(request=self.req1, data=datetime(2025, 1, 2, 4, 5, 6))
        with pytest.raises(RPCInternalError) as e:
            json_serializer.dumps(result)
        assert "Could not serialize JsonRpcSuccessResult" in e.value.message

    def test_result_binary(self, json_serializer):
        result = JsonRpcSuccessResult(request=self.req1, data=b"\x98")
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
