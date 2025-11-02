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
        server.redirect_to = "/foo"

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
        server.redirect_to = "/foo"

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
