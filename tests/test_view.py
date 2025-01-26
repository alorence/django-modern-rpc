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

from modernrpc.exceptions import RPC_INTERNAL_ERROR
from modernrpc.server import RPCServer

server = RPCServer()


@server.register_procedure
def simple_procedure(foo: str, bar: int):
    if bar < 0:
        raise ValueError("bar cannot be negative")
    return f"{foo=} {bar=}"


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
class TestJsonRpcSuccess:
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


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpcSuccess:
    def test_xmlrpc_success(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="simple_procedure", params=["bar", 42])
        response = server.view(request)
        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == "foo='bar' bar=42"


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
class TestJsonRpcError:
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


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpcError:
    def test_xmlrpc_error(self, xmlrpc_rf):
        request = xmlrpc_rf(method_name="simple_procedure", params=["bar", -2])
        response = server.view(request)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)

        assert code == RPC_INTERNAL_ERROR
        assert message == "Internal error: bar cannot be negative"


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
class TestBatchMulticall:
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


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpcMulticall:
    def test_xmlrpc_multicall_basics(self, xmlrpc_rf):
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
