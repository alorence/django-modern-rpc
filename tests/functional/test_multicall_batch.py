# coding: utf-8
import pytest

from modernrpc.exceptions import (
    RPC_INTERNAL_ERROR,
    RPC_METHOD_NOT_FOUND,
    RPC_INVALID_REQUEST,
)


def test_xmlrpc_multicall(xmlrpc_client):
    result = xmlrpc_client.multicall(
        [
            ("add", [5, 10]),
            ("divide", [30, 5]),
            ("add", [8, 8]),
            ("divide", [6, 2]),
        ]
    )
    assert isinstance(result, xmlrpc_client.multicall_result_klass)
    assert list(result) == [15, 6, 16, 3]


def test_xmlrpc_multicall_with_unknown_method(xmlrpc_client):
    result = xmlrpc_client.multicall(
        [
            ("add", [5, 10]),
            ("unknown_method", []),
            ("add", [8, 8]),
        ]
    )
    assert isinstance(result, xmlrpc_client.multicall_result_klass)
    assert result[0] == 15
    assert result[2] == 16

    exc_match = r'Method not found: "unknown_method"'
    with pytest.raises(
        xmlrpc_client.error_response_exception, match=exc_match
    ) as exc_info:
        assert result[1]
    xmlrpc_client.assert_exception_code(exc_info.value, RPC_METHOD_NOT_FOUND)


def test_xmlrpc_multicall_with_zero_division_error(xmlrpc_client):
    result = xmlrpc_client.multicall(
        [
            ("add", [5, 10]),
            ("divide", [30, 0]),
            ("add", [8, 8]),
        ]
    )
    assert isinstance(result, xmlrpc_client.multicall_result_klass)
    assert result[0] == 15
    assert result[2] == 16

    exc_match = r"division by zero"
    with pytest.raises(
        xmlrpc_client.error_response_exception, match=exc_match
    ) as exc_info:
        assert result[1]
    xmlrpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)


def test_jsonrpc_multicall_error(jsonrpc_client):
    exc_match = r'Method not found: "system.multicall"'
    with pytest.raises(
        jsonrpc_client.error_response_exception, match=exc_match
    ) as exc_info:
        jsonrpc_client.call("system.multicall")
    jsonrpc_client.assert_exception_code(exc_info.value, RPC_METHOD_NOT_FOUND)


def test_jsonrpc_batch(jsonrpc_client):
    result = jsonrpc_client.batch_request(
        [
            ("add", [5, 10]),
            ("divide", [77, 11]),
            ("add", [8, 8]),
        ]
    )
    assert isinstance(result, jsonrpc_client.batch_result_klass)
    assert result == [
        {"id": 0, "jsonrpc": "2.0", "result": 15},
        {"id": 1, "jsonrpc": "2.0", "result": 7},
        {"id": 2, "jsonrpc": "2.0", "result": 16},
    ]


def test_jsonrpc_batch_with_unknown_method(jsonrpc_client):
    result = jsonrpc_client.batch_request(
        [
            ("add", [5, 10]),
            ("unknown_method", []),
            ("add", [8, 8]),
        ]
    )
    assert isinstance(result, jsonrpc_client.batch_result_klass)
    assert result == [
        {"id": 0, "jsonrpc": "2.0", "result": 15},
        {
            "id": 1,
            "jsonrpc": "2.0",
            "error": {
                "code": RPC_METHOD_NOT_FOUND,
                "message": 'Method not found: "unknown_method"',
            },
        },
        {"id": 2, "jsonrpc": "2.0", "result": 16},
    ]


def test_jsonrpc_batch_with_zero_division_error(jsonrpc_client):
    result = jsonrpc_client.batch_request(
        [
            ("add", [5, 10]),
            ("divide", [9, 0]),
            ("add", [8, 8]),
        ]
    )
    assert isinstance(result, jsonrpc_client.batch_result_klass)
    assert result == [
        {"id": 0, "jsonrpc": "2.0", "result": 15},
        {
            "id": 1,
            "jsonrpc": "2.0",
            "error": {
                "code": RPC_INTERNAL_ERROR,
                "message": "Internal error: division by zero",
            },
        },
        {"id": 2, "jsonrpc": "2.0", "result": 16},
    ]


def test_jsonrpc_batch_with_named_params(jsonrpc_client):
    result = jsonrpc_client.batch_request(
        [
            ("add", {"a": 5, "b": 10}),
            ("divide", {"numerator": 30, "denominator": 5}),
            ("method_with_kwargs", []),
            ("method_with_kwargs_2", [6]),
            ("method_with_kwargs_2", {"x": 25}),
        ]
    )
    assert isinstance(result, jsonrpc_client.batch_result_klass)
    assert result == [
        {"id": 0, "jsonrpc": "2.0", "result": 15},
        {"id": 1, "jsonrpc": "2.0", "result": 6},
        {"id": 2, "jsonrpc": "2.0", "result": "__json_rpc"},
        {"id": 3, "jsonrpc": "2.0", "result": [6, "__json_rpc"]},
        {"id": 4, "jsonrpc": "2.0", "result": [25, "__json_rpc"]},
    ]


def test_jsonrpc_batch_with_notify(jsonrpc_client):
    result = jsonrpc_client.batch_request(
        [
            ("add", {"a": 5, "b": 10}),
            ("method_with_kwargs", [], "notify_only"),
            ("divide", {"numerator": 30, "denominator": 5}),
        ]
    )

    assert isinstance(result, jsonrpc_client.batch_result_klass)
    assert len(result) == 2
    assert result == [
        {"jsonrpc": "2.0", "id": 0, "result": 15},
        {"jsonrpc": "2.0", "id": 1, "result": 6},
    ]


def test_jsonrpc_batch_with_only_notify(jsonrpc_client):
    result = jsonrpc_client.batch_request(
        [
            ("add", {"a": 5, "b": 10}, "notify_only"),
            ("method_with_kwargs", [], "notify_only"),
            ("divide", {"numerator": 30, "denominator": 5}, "notify_only"),
        ]
    )
    assert result is None


def test_jsonrpc_batch_invalid_request(live_server, endpoint_path):
    import requests

    headers = {"content-type": "application/json"}
    result = requests.post(
        live_server.url + endpoint_path, data="[1, 2, 3]", headers=headers
    ).json()

    assert isinstance(result, list)
    assert len(result) == 3

    expected_error_message = 'Invalid request: Missing parameter "method"'
    assert result == [
        {
            "id": None,
            "jsonrpc": "2.0",
            "error": {"code": RPC_INVALID_REQUEST, "message": expected_error_message},
        },
        {
            "id": None,
            "jsonrpc": "2.0",
            "error": {"code": RPC_INVALID_REQUEST, "message": expected_error_message},
        },
        {
            "id": None,
            "jsonrpc": "2.0",
            "error": {"code": RPC_INVALID_REQUEST, "message": expected_error_message},
        },
    ]
