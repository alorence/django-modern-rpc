import json
from http import HTTPStatus

import pytest

from modernrpc import RpcServer


class TestNonRpcResponses:
    @pytest.fixture
    def server(self):
        return RpcServer()

    @pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "DELETE", "PATCH", "PUT"])
    def test_invalid_method(self, rf, server, method):
        response = server.view(rf.generic(method, "/rpc"))

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_redirection(self, rf, server):
        server.redirect_get_request_target = "/foo"

        response = server.view(rf.get("/rpc"))

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response.headers["Location"] == "/foo"

    def test_no_content_type(self, rf, server):
        response = server.view(rf.post("/rpc", data="Hello World!!", content_type=""))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == (
            b"Unable to handle your request, the Content-Type header is mandatory to allow server to "
            b"determine which handler can interpret your request."
        )

    def test_invalid_content_type(self, rf, server):
        response = server.view(rf.post("/rpc", data="Hello World!!", content_type="text/html"))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == b"Unable to handle your request, unsupported Content-Type text/html."


class TestNonRpcResponsesAsync:
    @pytest.fixture
    def server(self):
        return RpcServer()

    @pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "DELETE", "PATCH", "PUT"])
    async def test_invalid_method(self, async_rf, server, method):
        response = await server.async_view(async_rf.generic(method, "/rpc"))

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    async def test_redirection(self, async_rf, server):
        server.redirect_get_request_target = "/foo"

        response = await server.async_view(async_rf.get("/rpc"))

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response.headers["Location"] == "/foo"

    async def test_no_content_type(self, async_rf, server):
        response = await server.async_view(async_rf.post("/rpc", data="Hello World!!", content_type=""))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == (
            b"Unable to handle your request, the Content-Type header is mandatory to allow server to "
            b"determine which handler can interpret your request."
        )

    async def test_invalid_content_type(self, async_rf, server):
        response = await server.async_view(async_rf.post("/rpc", data="Hello World!!", content_type="text/html"))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content == b"Unable to handle your request, unsupported Content-Type text/html."


MALFORMED_JSONRPC_PAYLOADS = [
    pytest.param('"just a string"', id="string_root"),
    pytest.param("[1, 2, 3]", id="batch_of_ints"),
    pytest.param('{"jsonrpc": "2.0", "method": {}, "id": 1}', id="dict_method_name"),
    pytest.param('{"jsonrpc": "2.0", "method": ["a"], "id": 1}', id="list_method_name"),
]


class TestMalformedJsonRpcRequests:
    """Malformed JSON-RPC payloads must produce a proper "Invalid request" error response, never an HTTP 500"""

    @pytest.fixture
    def server(self):
        return RpcServer()

    @pytest.mark.parametrize("payload", MALFORMED_JSONRPC_PAYLOADS)
    def test_invalid_request_error_response(self, rf, server, payload):
        response = server.view(rf.post("/rpc", data=payload, content_type="application/json"))

        assert response.status_code == HTTPStatus.OK
        result = json.loads(response.content)
        assert result["error"]["code"] == -32600
        assert "Invalid request" in result["error"]["message"]


class TestMalformedJsonRpcRequestsAsync:
    """Malformed JSON-RPC payloads must produce a proper "Invalid request" error response, never an HTTP 500"""

    @pytest.fixture
    def server(self):
        return RpcServer()

    @pytest.mark.parametrize("payload", MALFORMED_JSONRPC_PAYLOADS)
    async def test_invalid_request_error_response(self, async_rf, server, payload):
        response = await server.async_view(async_rf.post("/rpc", data=payload, content_type="application/json"))

        assert response.status_code == HTTPStatus.OK
        result = json.loads(response.content)
        assert result["error"]["code"] == -32600
        assert "Invalid request" in result["error"]["message"]
