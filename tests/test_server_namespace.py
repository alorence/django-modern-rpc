import random

import pytest
from conftest import ALL_PROTOCOLS

from modernrpc import RpcServer
from modernrpc.core import Protocol
from modernrpc.exceptions import RPCMethodNotFound
from modernrpc.handlers import JsonRpcHandler, XmlRpcHandler
from modernrpc.server import RpcNamespace


class TestInitialRpcServer:
    @pytest.mark.parametrize("proto", ALL_PROTOCOLS)
    def test_procedure_unregistered(self, proto):
        with pytest.raises(RPCMethodNotFound):
            RpcServer().get_procedure("foo", proto)

    def test_supported_handlers(self):
        """Check that a fresh RPCServer 'supported_handlers' is correct with its initialization"""
        assert list(RpcServer().supported_handlers) == [JsonRpcHandler, XmlRpcHandler]

        assert list(RpcServer(supported_protocol=Protocol.JSON_RPC).supported_handlers) == [JsonRpcHandler]
        assert list(RpcServer(supported_protocol=Protocol.XML_RPC).supported_handlers) == [XmlRpcHandler]

    def test_get_jsonrpc_handler(self, rf, jsonrpc_content_type):
        """Check that correct RPC handler is retrieved from request's Content-Type header"""

        # Build a dummy request. The only important thing is its "Content-Type"
        request = rf.post(path="dummy", content_type=jsonrpc_content_type)

        # Server supports all protocols: OK
        assert isinstance(RpcServer().get_handler(request), JsonRpcHandler)

        # Server supports only JSON-RPC: OK
        handler = RpcServer(supported_protocol=Protocol.JSON_RPC).get_handler(request)
        assert isinstance(handler, JsonRpcHandler)

        # Server supports only XML-RPC: NOK
        handler = RpcServer(supported_protocol=Protocol.XML_RPC).get_handler(request)
        assert handler is None

    def test_get_xmlrpc_handler(self, rf, xmlrpc_content_type):
        """Check that correct RPC handler is retrieved from request's Content-Type header"""

        # Build a dummy request. The only important thing is its "Content-Type"
        request = rf.post(path="dummy", content_type=xmlrpc_content_type)

        # Server supports all protocols: OK
        assert isinstance(RpcServer().get_handler(request), XmlRpcHandler)

        # Server supports only XML-RPC: OK
        handler = RpcServer(supported_protocol=Protocol.XML_RPC).get_handler(request)
        assert isinstance(handler, XmlRpcHandler)

        # Server supports only JSON-RPC: NOK
        handler = RpcServer(supported_protocol=Protocol.JSON_RPC).get_handler(request)
        assert handler is None

    def test_system_procedures(self):
        server = RpcServer()

        assert "system.listMethods" in server.procedures
        assert "system.methodSignature" in server.procedures
        assert "system.methodHelp" in server.procedures
        assert "system.multicall" in server.procedures


def dummy_procedure():
    return True


class TestRpcServerRegistration:
    @pytest.mark.parametrize("proto", ALL_PROTOCOLS)
    def test_procedure_registration(self, proto):
        dummy_server = RpcServer()

        dummy_server.register_procedure(dummy_procedure)
        wrapper = dummy_server.get_procedure("dummy_procedure", proto)

        assert wrapper.function == dummy_procedure
        assert wrapper.name == "dummy_procedure"

    @pytest.mark.parametrize("proto", ALL_PROTOCOLS)
    def test_procedure_registration_custom_name(self, proto):
        dummy_server = RpcServer()

        dummy_server.register_procedure(dummy_procedure, name="foo")

        wrapper = dummy_server.get_procedure("foo", proto)
        assert wrapper.function == dummy_procedure
        assert wrapper.name == "foo"

        with pytest.raises(RPCMethodNotFound):
            dummy_server.get_procedure("dummy_procedure", proto)

    @pytest.mark.parametrize("proto", ALL_PROTOCOLS)
    def test_procedure_registration_with_invalid_name(self, proto):
        dummy_server = RpcServer()

        with pytest.raises(ValueError, match=r'method names starting with "rpc." are reserved for system extensions'):
            dummy_server.register_procedure(dummy_procedure, name="rpc.foo")

        with pytest.raises(RPCMethodNotFound):
            dummy_server.get_procedure("rpc.foo", proto)


namespace = RpcNamespace()


@namespace.register_procedure(name="randint")
def dummy():
    return random.randint(0, 5)


class TestRpcNamespace:
    def test_unregistered(self):
        server = RpcServer()

        assert "dummy" not in server.procedures
        assert "randint" not in server.procedures

    def test_ns_registration(self):
        server = RpcServer()
        server.register_namespace(namespace, "foo")

        assert "dummy" not in server.procedures
        assert "foo.randint" in server.procedures

    def test_forbidden_ns_registration(self):
        server = RpcServer()

        with pytest.raises(ValueError, match=r'method names starting with "rpc." are reserved for system extensions'):
            server.register_namespace(namespace, "rpc")

        assert "dummy" not in server.procedures
        assert "randint" not in server.procedures
        assert "rpc.randint" not in server.procedures
        assert "rpc.dummy" not in server.procedures


class TestJsonRpcHandler:
    handler = JsonRpcHandler()

    def test_response_content_type(self):
        assert self.handler.response_content_type() == "application/json"


class TestXmlRpcHandler:
    handler = XmlRpcHandler()

    def test_response_content_type(self):
        assert self.handler.response_content_type() == "application/xml"
