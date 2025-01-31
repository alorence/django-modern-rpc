import json
import random
from http import HTTPStatus

import pytest
from helpers import (
    extract_jsonrpc_fault_data,
    extract_jsonrpc_success_result,
    extract_xmlrpc_fault_data,
    extract_xmlrpc_success_result,
)

from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPC_INVALID_PARAMS, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR
from modernrpc.server import RpcServer

server = RpcServer()


@server.register_procedure
def simple_procedure(foo: str, bar: int):
    """A simple test procedure..."""
    if bar < 0:
        raise ValueError("bar cannot be negative")
    return f"{foo=} {bar=}"


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpc:
    def test_success(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="simple_procedure", params=["bar", 42])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == "foo='bar' bar=42"

    def test_error(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="simple_procedure", params=["bar", -2])
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)

        assert code == RPC_INTERNAL_ERROR
        assert message == "Internal error: bar cannot be negative"

    def test_invalid_xml_payload_request(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="simple_procedure", params=["bar", 11])
        request._body = request.body.replace(b"<value>", b"!value>")  # noqa: SLF001
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_PARSE_ERROR
        assert "Parse error, unable to read the request: mismatched tag" in message

    def test_invalid_params(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="simple_procedure", params=["bar", "baz", -111])
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)

        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: simple_procedure() takes 2 positional arguments but 3 were given"

    def test_system_list_methods(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="system.listMethods")
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [
            "system.listMethods",
            "system.methodSignature",
            "system.methodHelp",
            "system.multicall",
            "simple_procedure",
        ]

    def test_system_method_signature(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="system.methodSignature", params=["simple_procedure"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [["undef", "str", "int"]]

    def test_system_method_help(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="system.methodHelp", params=["simple_procedure"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == "A simple test procedure..."

    def test_system_method_signature_invalid_arg(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="system.methodSignature", params=["non_existant_method"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'

    def test_system_method_help_invalid_arg(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="system.methodHelp", params=["non_existant_method"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpcMulticall:
    def test_multicall_standard(self, xmlrpc_rf):
        mc_params = [
            [
                {"methodName": "simple_procedure", "params": ("xxx", 20)},
                {"methodName": "simple_procedure", "params": ("yyy", -20)},
            ]
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [
            ["foo='xxx' bar=20"],
            {"faultCode": -32603, "faultString": "Internal error: bar cannot be negative"},
        ]

    def test_multicall_invalid_params_1(self, xmlrpc_rf):
        mc_params = ["foo.bar"]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: system.multicall first argument should be a list, str given."

    def test_multicall_invalid_params_2(self, xmlrpc_rf):
        mc_params = [
            {
                "calls": [
                    {"methodName": "simple_procedure", "params": ("xxx", 20)},
                    {"methodName": "simple_procedure", "params": ("yyy", -20)},
                ]
            }
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: system.multicall first argument should be a list, dict given."


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
class TestJsonRpc:
    def test_jsonrpc_success(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="simple_procedure", params=["bar", 42])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_jsonrpc_success_result(response) == "foo='bar' bar=42"

    def test_jsonrpc_notification_success(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="simple_procedure", params=["bar", 42], is_notification=True)
        response = server.view(request)
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b""

    def test_jsonrpc_error(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="simple_procedure", params=["bar", -2])
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)

        assert code == RPC_INTERNAL_ERROR
        assert message == "Internal error: bar cannot be negative"

    def test_jsonrpc_notification_error(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="simple_procedure", params=["bar", -2], is_notification=True)
        response = server.view(request)
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b""

    def test_invalid_json_payload_request(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="simple_procedure", params=["bar", 11])
        request._body = request.body.replace(b'"', b"**")  # noqa: SLF001
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_PARSE_ERROR
        assert message == "Parse error, unable to read the request: Expecting property name enclosed in double quotes"

    def test_invalid_params(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="simple_procedure", params=["bar", "baz", -111])
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)

        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: simple_procedure() takes 2 positional arguments but 3 were given"

    def test_system_list_methods(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="system.listMethods")
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_jsonrpc_success_result(response) == [
            "system.listMethods",
            "system.methodSignature",
            "system.methodHelp",
            "system.multicall",
            "simple_procedure",
        ]

    def test_system_method_signature(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="system.methodSignature", params=["simple_procedure"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_jsonrpc_success_result(response) == [["undef", "str", "int"]]

    def test_system_method_help(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="system.methodHelp", params=["simple_procedure"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_jsonrpc_success_result(response) == "A simple test procedure..."

    def test_system_method_signature_invalid_arg(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="system.methodSignature", params=["non_existant_method"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'

    def test_system_method_help_invalid_arg(self, jsonrpc_rf):
        request = jsonrpc_rf(method_name="system.methodHelp", params=["non_existant_method"])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
class TestJsonRpcBatch:
    def test_jsonrpc_batch_basics(self, jsonrpc_batch_rf):
        request = jsonrpc_batch_rf(
            requests=[("simple_procedure", (chr(i), random.randint(-8, 12)), False) for i in range(97, 123)]
        )
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) == 26

    def test_jsonrpc_batch_all_notif(self, jsonrpc_batch_rf):
        request = jsonrpc_batch_rf(
            requests=[("simple_procedure", (chr(i), random.randint(-8, 12)), True) for i in range(97, 123)]
        )
        response = server.view(request)

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b""
