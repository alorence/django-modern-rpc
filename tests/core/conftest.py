import pytest

import modernrpc.core


@pytest.fixture(scope='function')
def rpc_registry():
    # Performing a shallow copy is ok here, since we will only add or remove methods in the registry inside tests
    # If for any reason, an existing method have to be modified inside a test, a deep copy must be prefered here to
    # ensure strict isolation between tests
    _registry_dump = {**modernrpc.core.registry._registry}
    yield modernrpc.core.registry
    modernrpc.core.registry._registry = _registry_dump
