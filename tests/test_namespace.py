import random

from modernrpc import RPCServer
from modernrpc.server import RPCNamespace

namespace = RPCNamespace()


@namespace.register_procedure(name="randint")
def dummy():
    return random.randint(0, 5)


class TestNamespace:
    def test_unregistered(self):
        server = RPCServer()

        assert "dummy" not in server.procedures
        assert "randint" not in server.procedures

    def test_ns_registration(self):
        server = RPCServer()
        server.register_namespace(namespace, "foo")

        assert "foo.randint" in server.procedures
