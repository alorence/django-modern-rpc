import json
import random
from http import HTTPStatus

import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR, RPC_INVALID_PARAMS, RPC_METHOD_NOT_FOUND, RPC_PARSE_ERROR
from tests.helpers import extract_jsonrpc_fault_data, extract_jsonrpc_success_result


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
class TestJsonRpcSyncView:
    def test_standard_call(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name=method_name, params=["bar", 42])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_jsonrpc_success_result(response) == "foo='bar' bar=42"
        on_error_mock.assert_not_called()

    def test_notification_call(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name=method_name, params=["bar", 42], is_notif=True)

        response = server.view(request)

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b""
        on_error_mock.assert_not_called()

    def test_procedure_exception(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name=method_name, params=["bar", -2])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_INTERNAL_ERROR
        assert message == "Internal error: bar cannot be negative"
        on_error_mock.assert_called_once()

    def test_notification_exception(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name=method_name, params=["bar", -2], is_notif=True)

        response = server.view(request)

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b""
        on_error_mock.assert_called_once()

    def test_invalid_json_payload_request(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name=method_name, params=["bar", 11])
        request._body = request.body.replace(b'"', b"**")  # noqa: SLF001

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_PARSE_ERROR
        assert "Parse error, unable to read the request:" in message
        on_error_mock.assert_called_once()

    def test_invalid_params(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name=method_name, params=["bar", "baz", -111])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_INVALID_PARAMS
        assert message == f"Invalid parameters: {method_name}() takes 2 positional arguments but 3 were given"
        on_error_mock.assert_called_once()

    def test_invalid_result(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_unserializable_result_procedure" if asynchronous else "unserializable_result_procedure"
        request = jsonrpc_rf(method_name=method_name, params=[], req_id=33)

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_INTERNAL_ERROR
        assert "Unable to serialize result data: {'id': 33, 'jsonrpc': '2.0', 'result': Ellipsis}" in message
        on_error_mock.assert_called_once()

    def test_system_list_methods(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        request = jsonrpc_rf(method_name="system.listMethods")

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_jsonrpc_success_result(response) == [
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

    def test_system_method_signature(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name="system.methodSignature", params=[method_name])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert extract_jsonrpc_success_result(response) == [["undef", "str", "int"]]
        on_error_mock.assert_not_called()

    def test_system_method_help(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_rf(method_name="system.methodHelp", params=[method_name])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        assert (
            extract_jsonrpc_success_result(response)
            == "Return a simple string when given 'bar' is positive, raise ValueError when 'bar' is negative"
        )
        on_error_mock.assert_not_called()

    def test_system_method_signature_invalid_arg(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        request = jsonrpc_rf(method_name="system.methodSignature", params=["non_existant_method"])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'
        on_error_mock.assert_called_once()

    def test_system_method_help_invalid_arg(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        request = jsonrpc_rf(method_name="system.methodHelp", params=["non_existant_method"])

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "non_existant_method"'
        on_error_mock.assert_called_once()

    def test_system_multicall_unavailable(self, jsonrpc_rf, server, asynchronous, on_error_mock):
        # Multicall is not exposed to JSON-RPC requests. Batch request must be used in this case
        mc_params = [
            [
                {"methodName": "simple_procedure", "params": ("xxx", 20)},
                {"methodName": "simple_procedure", "params": ("yyy", -20)},
            ]
        ]
        request = jsonrpc_rf(method_name="system.multicall", params=mc_params)

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_jsonrpc_fault_data(response)
        assert code == RPC_METHOD_NOT_FOUND
        assert message == 'Method not found: "system.multicall"'
        on_error_mock.assert_called_once()


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
class TestJsonRpcSyncBatch:
    def test_jsonrpc_batch_basics(self, jsonrpc_batch_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_batch_rf(
            requests=[(method_name, (chr(i), random.randint(-8, 12)), False) for i in range(97, 123)]
        )

        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) == 26
        on_error_mock.assert_called()

    def test_jsonrpc_batch_all_notif(self, jsonrpc_batch_rf, server, asynchronous, on_error_mock):
        method_name = "async_simple_procedure" if asynchronous else "simple_procedure"
        request = jsonrpc_batch_rf(
            requests=[(method_name, (chr(i), random.randint(-8, 12)), True) for i in range(97, 123)]
        )

        response = server.view(request)

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.content == b""
        on_error_mock.assert_called()
