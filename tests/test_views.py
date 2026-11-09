import json
from http import HTTPStatus
from typing import Any

import pytest
from django.http import HttpResponse
from django.test import AsyncRequestFactory, RequestFactory

from modernrpc import RpcServer
from modernrpc.exceptions import RPCInvalidRequest


class TestNonRpcResponses:
    @pytest.fixture
    def server(self) -> RpcServer:
        return RpcServer()

    @pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "DELETE", "PATCH", "PUT"])
    def test_invalid_method(self, rf: RequestFactory, server: RpcServer, method: str) -> None:
        response = server.view(rf.generic(method, "/rpc"))

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_redirection(self, rf: RequestFactory, server: RpcServer) -> None:
        server.redirect_get_request_target = "/foo"

        response = server.view(rf.get("/rpc"))

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response.headers["Location"] == "/foo"

    def test_no_content_type(self, rf: RequestFactory, server: RpcServer) -> None:
        response = server.view(rf.post("/rpc", data="Hello World!!", content_type=""))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == (
            b"Unable to handle your request, the Content-Type header is mandatory to allow server to "
            b"determine which handler can interpret your request."
        )

    def test_invalid_content_type(self, rf: RequestFactory, server: RpcServer) -> None:
        response = server.view(rf.post("/rpc", data="Hello World!!", content_type="text/html"))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == b"Unable to handle your request, unsupported Content-Type text/html."


class TestNonRpcResponsesAsync:
    @pytest.fixture
    def server(self) -> RpcServer:
        return RpcServer()

    @pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "DELETE", "PATCH", "PUT"])
    async def test_invalid_method(self, async_rf: AsyncRequestFactory, server: RpcServer, method: str):
        response = await server.async_view(async_rf.generic(method, "/rpc"))

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    async def test_redirection(self, async_rf: AsyncRequestFactory, server: RpcServer):
        server.redirect_get_request_target = "/foo"

        response = await server.async_view(async_rf.get("/rpc"))

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response.headers["Location"] == "/foo"

    async def test_no_content_type(self, async_rf: AsyncRequestFactory, server: RpcServer):
        response = await server.async_view(async_rf.post("/rpc", data="Hello World!!", content_type=""))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == (
            b"Unable to handle your request, the Content-Type header is mandatory to allow server to "
            b"determine which handler can interpret your request."
        )

    async def test_invalid_content_type(self, async_rf: AsyncRequestFactory, server: RpcServer):
        response = await server.async_view(async_rf.post("/rpc", data="Hello World!!", content_type="text/html"))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == b"Unable to handle your request, unsupported Content-Type text/html."


MALFORMED_JSONRPC_PAYLOADS = [
    pytest.param('"just a string"', id="string_root"),
    pytest.param("[]", id="empty_batch"),
    pytest.param('{"jsonrpc": "2.0", "method": {}, "id": 1}', id="dict_method_name"),
    pytest.param('{"jsonrpc": "2.0", "method": ["a"], "id": 1}', id="list_method_name"),
]


class TestMalformedJsonRpcRequests:
    """Malformed JSON-RPC payloads must produce a proper "Invalid request" error response, never an HTTP 500"""

    @pytest.fixture
    def server(self) -> RpcServer:
        return RpcServer()

    @pytest.mark.parametrize("payload", MALFORMED_JSONRPC_PAYLOADS)
    def test_invalid_request_error_response(self, rf: RequestFactory, server: RpcServer, payload: Any) -> None:
        response = server.view(rf.post("/rpc", data=payload, content_type="application/json"))

        assert response.status_code == HTTPStatus.OK
        result = json.loads(response.content)
        assert result["error"]["code"] == -32600
        assert "Invalid request" in result["error"]["message"]


class TestMalformedJsonRpcRequestsAsync:
    """Malformed JSON-RPC payloads must produce a proper "Invalid request" error response, never an HTTP 500"""

    @pytest.fixture
    def server(self) -> RpcServer:
        return RpcServer()

    @pytest.mark.parametrize("payload", MALFORMED_JSONRPC_PAYLOADS)
    async def test_invalid_request_error_response(self, async_rf: AsyncRequestFactory, server: RpcServer, payload: Any):
        response = await server.async_view(async_rf.post("/rpc", data=payload, content_type="application/json"))

        assert response.status_code == HTTPStatus.OK
        result = json.loads(response.content)
        assert result["error"]["code"] == -32600
        assert "Invalid request" in result["error"]["message"]


MIXED_BATCH_PAYLOAD = json.dumps(
    [
        {"jsonrpc": "2.0", "id": 1, "method": "system.listMethods"},
        1,
        {"jsonrpc": "2.0", "id": 2},
        {"jsonrpc": "2.0", "method": "system.listMethods"},
        {"jsonrpc": "2.0", "id": 3, "method": "system.methodHelp", "params": ["system.listMethods"]},
    ]
)


def check_mixed_batch_response(response: HttpResponse) -> None:
    """Each invalid item gets its own Invalid Request error with a null id, valid items are executed normally"""
    assert response.status_code == HTTPStatus.OK
    results = json.loads(response.content)
    assert isinstance(results, list)
    # 5 items in the batch, 1 is a notification
    assert len(results) == 4

    assert results[0]["id"] == 1
    assert "system.listMethods" in results[0]["result"]

    for invalid in results[1:3]:
        assert invalid["id"] is None
        assert invalid["error"]["code"] == -32600
        assert invalid["error"]["message"].startswith("Invalid request:")

    assert results[3]["id"] == 3
    assert results[3]["result"] == "Returns a list of all procedures exposed by the server"


class TestJsonRpcBatchWithInvalidItems:
    @pytest.fixture
    def server(self) -> RpcServer:
        return RpcServer()

    def test_sync_view(self, rf: RequestFactory, server: RpcServer) -> None:
        response = server.view(rf.post("/rpc", data=MIXED_BATCH_PAYLOAD, content_type="application/json"))
        check_mixed_batch_response(response)

    async def test_async_view(self, async_rf: AsyncRequestFactory, server: RpcServer) -> None:
        response = await server.async_view(
            async_rf.post("/rpc", data=MIXED_BATCH_PAYLOAD, content_type="application/json")
        )
        check_mixed_batch_response(response)

    def test_invalid_items_go_through_error_handler(self, rf: RequestFactory) -> None:
        handled: list[BaseException] = []
        server = RpcServer(error_handler=lambda exc, _ctx: handled.append(exc))

        server.view(rf.post("/rpc", data=MIXED_BATCH_PAYLOAD, content_type="application/json"))

        assert len(handled) == 2
        assert all(isinstance(exc, RPCInvalidRequest) for exc in handled)
