import pytest

import modernrpc.core


@pytest.fixture(scope='function')
def rpc_registry():
    # With Python 3.5+, we could use _dump = {**orig_dict} to easily perform a shallow copy
    # Unfortunately, we still maintain compatibility with Python 2.7
    # See https://www.python.org/dev/peps/pep-0448/
    # See https://stackoverflow.com/a/46180556/1887976
    _registry_dump = modernrpc.core.registry._registry.copy()
    yield modernrpc.core.registry
    modernrpc.core.registry._registry = _registry_dump
