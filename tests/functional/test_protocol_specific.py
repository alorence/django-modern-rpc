import pytest

from modernrpc.exceptions import (
    RPC_METHOD_NOT_FOUND,
    RPC_INVALID_PARAMS,
    RPC_CUSTOM_ERROR_BASE,
)


def test_available_methods(jsonrpc_client, xmlrpc_client):
    methods_list = jsonrpc_client.call("system.listMethods")
    assert "json_only" in methods_list
    assert "xml_only" not in methods_list

    methods_list = xmlrpc_client.call("system.listMethods")
    assert "json_only" not in methods_list
    assert "xml_only" in methods_list


def test_specific_methods_return(jsonrpc_client, xmlrpc_client):
    assert jsonrpc_client.call("json_only") == "JSON only"
    assert xmlrpc_client.call("xml_only") == "XML only"


def test_specific_methods_not_found(jsonrpc_client, xmlrpc_client):
    exc_match = r'Method not found: "xml_only"'
    with pytest.raises(jsonrpc_client.error_response_exception, match=exc_match) as exc_info:
        jsonrpc_client.call("xml_only")
    xmlrpc_client.assert_exception_code(exc_info.value, RPC_METHOD_NOT_FOUND)

    exc_match = r'Method not found: "json_only"'
    with pytest.raises(xmlrpc_client.error_response_exception, match=exc_match) as exc_info:
        xmlrpc_client.call("json_only")
    xmlrpc_client.assert_exception_code(exc_info.value, RPC_METHOD_NOT_FOUND)


class TestJsonRpcSpecificFeatures:
    def test_exception_with_data(self, jsonrpc_client):
        exc_match = r"This exception has additional data"
        with pytest.raises(jsonrpc_client.error_response_exception, match=exc_match) as exc_info:
            jsonrpc_client.call("raise_custom_exception_with_data")
        jsonrpc_client.assert_exception_code(exc_info.value, RPC_CUSTOM_ERROR_BASE + 5)
        assert exc_info.value.data == ["a", "b", "c"]

    def test_named_args(self, jsonrpc_client):
        assert jsonrpc_client.call("divide", numerator=50, denominator=8, z=25) == 6.25

    def test_named_args_with_errors(self, jsonrpc_client):
        exc_match = r"Invalid parameters: divide\(\) got an unexpected keyword argument.+"
        with pytest.raises(jsonrpc_client.error_response_exception, match=exc_match) as exc_info:
            jsonrpc_client.call("divide", wrong_param_1=10, wrong_param_2=20, z=25)
        jsonrpc_client.assert_exception_code(exc_info.value, RPC_INVALID_PARAMS)

    def test_notify(self, jsonrpc_client):
        assert jsonrpc_client.call("add", 5, 12, notify=True) is None

    @pytest.mark.parametrize("request_id", ["abcd", 1234, -999, 19.55, -987.3, None])
    def test_valid_id(self, jsonrpc_client, request_id):
        assert jsonrpc_client.call("add", 98, 2, _id=request_id) == 100

    @pytest.mark.parametrize("request_id", [{}, {"foo": "bar"}, {"foo": 155}, [], ["a", "b"]])
    def test_invalid_id(self, jsonrpc_client, request_id):
        exc_match = (
            r'Parameter "id" has an unsupported value\. According to JSON-RPC 2\.0 '
            r"standard, it must be a String, a Number or a Null value\."
        )
        with pytest.raises(jsonrpc_client.error_response_exception, match=exc_match) as exc_info:
            jsonrpc_client.call("add", 5, 12, _id=request_id)
        assert exc_info.value.code == -32600
