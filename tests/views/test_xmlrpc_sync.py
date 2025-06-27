import re
from http import HTTPStatus

import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPC_INVALID_PARAMS, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR
from tests.helpers import extract_xmlrpc_fault_data, extract_xmlrpc_success_result


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
class TestXmlRpcSyncView:
    def test_standard_call(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", 42])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == "foo='bar' bar=42"
        on_error_mock.assert_not_called()

    def test_procedure_exception(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", -2])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INTERNAL_ERROR
        assert message == "Internal error: bar cannot be negative"
        on_error_mock.assert_called_once()

    def test_invalid_xml_payload_request(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", 11])
        request._body = request.body.replace(b"<value>", b"!value>")  # noqa: SLF001

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_PARSE_ERROR
        assert "Parse error, unable to read the request:" in message
        on_error_mock.assert_called_once()

    def test_invalid_params(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name=method_name, params=["bar", "baz", -111])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert re.match(
            rf"Invalid parameters: [\w.<>]*{method_name}\(\) takes 2 positional arguments but 3 were given", message
        )
        on_error_mock.assert_called_once()

    def test_invalid_result(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_unserializable_result_procedure" if asynchronous else "unserializable_result_procedure"
        request = xmlrpc_rf(method_name=method_name, params=[])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INTERNAL_ERROR
        assert "Unable to serialize result data: Ellipsis" in message
        on_error_mock.assert_called_once()

    def test_system_list_methods(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        request = xmlrpc_rf(method_name="system.listMethods")

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [
            "system.listMethods",
            "system.methodSignature",
            "system.methodHelp",
            "system.multicall",
            "simple_procedure",
            "unserializable_result_procedure",
            "async_simple_procedure",
            "async_unserializable_result_procedure",
        ]
        on_error_mock.assert_not_called()

    def test_system_method_signature(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name="system.methodSignature", params=[method_name])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [["undef", "str", "int"]]
        on_error_mock.assert_not_called()

    def test_system_method_help(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = xmlrpc_rf(method_name="system.methodHelp", params=[method_name])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert (
            extract_xmlrpc_success_result(response)
            == "Return a simple string when given 'bar' is positive, raise ValueError when 'bar' is negative"
        )
        on_error_mock.assert_not_called()

    def test_system_method_signature_invalid_arg(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        request = xmlrpc_rf(method_name="system.methodSignature", params=["non_existant_method"])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'
        on_error_mock.assert_called_once()

    def test_system_method_help_invalid_arg(self, xmlrpc_rf, server, asynchronous, on_error_mock):
        request = xmlrpc_rf(method_name="system.methodHelp", params=["non_existant_method"])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'
        on_error_mock.assert_called_once()


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers", "async_multicall_settings")
class TestXmlRpcSyncMulticall:
    def test_multicall_standard(self, xmlrpc_rf, server, on_error_mock):
        mc_params = [
            [
                {"methodName": "simple_procedure", "params": ("xxx", 20)},
                {"methodName": "simple_procedure", "params": ("yyy", -20)},
                {"methodName": "async_simple_procedure", "params": ("xxx", 20)},
                {"methodName": "async_simple_procedure", "params": ("yyy", -20)},
            ]
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [
            ["foo='xxx' bar=20"],
            {"faultCode": -32603, "faultString": "Internal error: bar cannot be negative"},
            ["foo='xxx' bar=20"],
            {"faultCode": -32603, "faultString": "Internal error: bar cannot be negative"},
        ]
        assert on_error_mock.call_count == 2

    def test_multicall_invalid_params_1(self, xmlrpc_rf, server, on_error_mock):
        mc_params = ["foo.bar"]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: system.multicall first argument should be a list, str given."
        on_error_mock.assert_called_once()

    def test_multicall_invalid_params_2(self, xmlrpc_rf, server, on_error_mock):
        mc_params = [
            {
                "calls": [
                    {"methodName": "simple_procedure", "params": ("xxx", 20)},
                    {"methodName": "simple_procedure", "params": ("yyy", -20)},
                    {"methodName": "async_simple_procedure", "params": ("xxx", 20)},
                    {"methodName": "async_simple_procedure", "params": ("yyy", -20)},
                ]
            }
        ]
        request = xmlrpc_rf(method_name="system.multicall", params=mc_params)

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == "Invalid parameters: system.multicall first argument should be a list, dict given."
        on_error_mock.assert_called_once()
