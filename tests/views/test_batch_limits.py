import json
from http import HTTPStatus
from typing import Any

import pytest
from asgiref.sync import async_to_sync
from django.http import HttpRequest, HttpResponse
from pytest_django import Settings

from modernrpc import RpcServer
from modernrpc.exceptions import RPC_INVALID_REQUEST
from tests.helpers import JsonRpcBatchRF, XmlRpcRF, extract_xmlrpc_fault_data, extract_xmlrpc_success_result


def call_view(server: RpcServer, request: HttpRequest, use_async_view: bool) -> HttpResponse:
    if use_async_view:
        return async_to_sync(server.async_view)(request)
    return server.view(request)


class TestMaxBatchSizeConfiguration:
    def test_default_value(self) -> None:
        assert RpcServer().max_batch_size == 100

    def test_from_settings(self, settings: Settings) -> None:
        settings.MODERNRPC_MAX_BATCH_SIZE = 5
        assert RpcServer().max_batch_size == 5

    @pytest.mark.parametrize("value", [3, None])
    def test_init_arg_overrides_settings(self, settings: Settings, value: int | None) -> None:
        settings.MODERNRPC_MAX_BATCH_SIZE = 5
        assert RpcServer(max_batch_size=value).max_batch_size == value


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
@pytest.mark.parametrize("use_async_view", [False, True], ids=["sync_view", "async_view"])
class TestJsonRpcBatchLimit:
    @staticmethod
    def batch(size: int, *, notifications: bool = False) -> list[tuple[str, tuple[Any, ...], bool]]:
        return [("simple_procedure", ("x", i), notifications) for i in range(size)]

    def test_batch_at_limit(self, jsonrpc_batch_rf: JsonRpcBatchRF, server: RpcServer, use_async_view: bool) -> None:
        server.max_batch_size = 5
        request = jsonrpc_batch_rf(requests=self.batch(5))

        response = call_view(server, request, use_async_view)

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) == 5
        assert all("result" in item for item in data)

    @pytest.mark.parametrize("notifications", [False, True], ids=["requests", "notifications"])
    def test_batch_over_limit(
        self,
        jsonrpc_batch_rf: JsonRpcBatchRF,
        server: RpcServer,
        use_async_view: bool,
        notifications: bool,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        server.max_batch_size = 5
        executed: list[Any] = []
        monkeypatch.setattr(server.procedures["simple_procedure"], "execute", executed.append)
        monkeypatch.setattr(server.procedures["simple_procedure"], "aexecute", executed.append)
        request = jsonrpc_batch_rf(requests=self.batch(6, notifications=notifications))

        response = call_view(server, request, use_async_view)

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert data == {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": RPC_INVALID_REQUEST,
                "message": "Invalid request: too many calls in a single request (6), maximum is 5",
            },
        }
        # No procedure has been executed
        assert executed == []

    def test_batch_no_limit(self, jsonrpc_batch_rf: JsonRpcBatchRF, server: RpcServer, use_async_view: bool) -> None:
        server.max_batch_size = None
        request = jsonrpc_batch_rf(requests=self.batch(150))

        response = call_view(server, request, use_async_view)

        assert response.status_code == HTTPStatus.OK
        assert len(json.loads(response.content)) == 150


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
@pytest.mark.parametrize("use_async_view", [False, True], ids=["sync_view", "async_view"])
class TestXmlRpcMulticallLimits:
    @staticmethod
    def calls(size: int) -> list[dict[str, Any]]:
        return [{"methodName": "simple_procedure", "params": ("x", i)} for i in range(size)]

    def test_multicall_at_limit(
        self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer, use_async_view: bool
    ) -> None:
        server = server_using_sync_or_async_multicall
        server.max_batch_size = 5
        request = xmlrpc_rf(method_name="system.multicall", params=(self.calls(5),))

        response = call_view(server, request, use_async_view)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [[f"foo='x' bar={i}"] for i in range(5)]

    def test_multicall_over_limit(
        self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer, use_async_view: bool
    ) -> None:
        server = server_using_sync_or_async_multicall
        server.max_batch_size = 5
        request = xmlrpc_rf(method_name="system.multicall", params=(self.calls(6),))

        response = call_view(server, request, use_async_view)

        assert response.status_code == HTTPStatus.OK
        code, message = extract_xmlrpc_fault_data(response)
        assert code == RPC_INVALID_REQUEST
        assert message == "Invalid request: too many calls in a single request (6), maximum is 5"

    def test_multicall_no_limit(
        self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer, use_async_view: bool
    ) -> None:
        server = server_using_sync_or_async_multicall
        server.max_batch_size = None
        request = xmlrpc_rf(method_name="system.multicall", params=(self.calls(150),))

        response = call_view(server, request, use_async_view)

        assert response.status_code == HTTPStatus.OK
        assert len(extract_xmlrpc_success_result(response)) == 150

    def test_recursive_multicall_forbidden(
        self, xmlrpc_rf: XmlRpcRF, server_using_sync_or_async_multicall: RpcServer, use_async_view: bool
    ) -> None:
        server = server_using_sync_or_async_multicall
        nested = {"methodName": "system.multicall", "params": [self.calls(2)]}
        request = xmlrpc_rf(method_name="system.multicall", params=([*self.calls(1), nested, *self.calls(1)],))

        response = call_view(server, request, use_async_view)

        assert response.status_code == HTTPStatus.OK
        assert extract_xmlrpc_success_result(response) == [
            ["foo='x' bar=0"],
            {"faultCode": RPC_INVALID_REQUEST, "faultString": "Invalid request: recursive system.multicall forbidden"},
            ["foo='x' bar=0"],
        ]
