from unittest.mock import Mock

import pytest

from modernrpc import RpcServer


@pytest.fixture
def server():
    server = RpcServer()

    @server.register_procedure
    def simple_procedure(foo: str, bar: int):
        """Return a simple string when the given 'bar' is positive, raise ValueError when it is negative"""
        if bar < 0:
            raise ValueError("bar cannot be negative")
        return f"{foo=} {bar=}"

    @server.register_procedure
    def unserializable_result_procedure():
        """Return an object that cannot be serialized by default backends"""
        return ...

    @server.register_procedure
    async def async_simple_procedure(foo: str, bar: int):
        """Return a simple string when the given 'bar' is positive, raise ValueError when it is negative"""
        if bar < 0:
            raise ValueError("bar cannot be negative")
        return f"{foo=} {bar=}"

    @server.register_procedure
    async def async_unserializable_result_procedure():
        """Return an object that cannot be serialized by default backends"""
        return ...

    return server


@pytest.fixture
def on_error_mock(monkeypatch, server):
    mock = Mock(side_effect=server.on_error)
    monkeypatch.setattr(server, "on_error", mock)
    return mock
