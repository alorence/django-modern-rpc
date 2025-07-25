import importlib
from unittest.mock import Mock

import pytest

from modernrpc import RpcServer
from modernrpc.constants import SYSTEM_NAMESPACE_DOTTED_PATH


@pytest.fixture
def server(monkeypatch):
    """Create a fresh instance of RpcServer with a mocked 'on_error' method and some fake procedures registered."""
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

    monkeypatch.setattr(server, "on_error", Mock(side_effect=server.on_error))

    return server


@pytest.fixture(params=[True, False])
def server_using_sync_or_async_multicall(request, settings, server, monkeypatch):
    """
    Create a new instance of RpcServer with a mocked 'on_error' method and some fake procedures registered.
    The fixture is parametrized to run tests with sync and async system.multicall versions.
    """
    server_should_use_async_multicall = request.param

    if server_should_use_async_multicall:
        settings.MODERNRPC_XMLRPC_ASYNC_MULTICALL = True
    else:
        settings.MODERNRPC_XMLRPC_ASYNC_MULTICALL = False

    # settings.MODERNRPC_XMLRPC_ASYNC_MULTICALL is checked at module level when it is first imported
    # Reload the imported module the new server instanciation will register the right system.multicall version
    system_procedures_module, _ = SYSTEM_NAMESPACE_DOTTED_PATH.rsplit(".", 1)
    importlib.reload(importlib.import_module(system_procedures_module))

    new_server = RpcServer()
    monkeypatch.setattr(new_server, "on_error", Mock(side_effect=new_server.on_error))

    for proc in server.procedures.values():
        if "system" not in proc.name:
            new_server.register_procedure(proc.func_or_coro)

    return new_server
