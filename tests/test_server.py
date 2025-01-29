import pytest

from modernrpc.core import Protocol
from modernrpc.exceptions import RPCMethodNotFound
from modernrpc.handlers import JsonRpcHandler, XmlRpcHandler
from modernrpc.server import RPCServer


class TestRPCServerBase:
    def test_procedure_unregistered(self):
        with pytest.raises(RPCMethodNotFound):
            RPCServer().get_procedure("foo")

    def test_supported_handlers(self):
        """Check that a fresh RPCServer 'supported_handlers' is correct with its initialization"""
        assert list(RPCServer().supported_handlers) == [JsonRpcHandler, XmlRpcHandler]

        assert list(RPCServer(supported_protocol=Protocol.JSON_RPC).supported_handlers) == [JsonRpcHandler]
        assert list(RPCServer(supported_protocol=Protocol.XML_RPC).supported_handlers) == [XmlRpcHandler]

    def test_get_jsonrpc_handler(self, rf, jsonrpc_content_type):
        """Check that correct RPC handler is retrieved from request's Content-Type header"""

        # Build a dummy request. The only important thing is its "Content-Type"
        request = rf.post(path="dummy", content_type=jsonrpc_content_type)

        # Server supports all protocols: OK
        assert isinstance(RPCServer().get_handler(request), JsonRpcHandler)

        # Server supports only JSON-RPC: OK
        handler = RPCServer(supported_protocol=Protocol.JSON_RPC).get_handler(request)
        assert isinstance(handler, JsonRpcHandler)

        # Server supports only XML-RPC: NOK
        handler = RPCServer(supported_protocol=Protocol.XML_RPC).get_handler(request)
        assert handler is None

    def test_get_xmlrpc_handler(self, rf, xmlrpc_content_type):
        """Check that correct RPC handler is retrieved from request's Content-Type header"""

        # Build a dummy request. The only important thing is its "Content-Type"
        request = rf.post(path="dummy", content_type=xmlrpc_content_type)

        # Server supports all protocols: OK
        assert isinstance(RPCServer().get_handler(request), XmlRpcHandler)

        # Server supports only XML-RPC: OK
        handler = RPCServer(supported_protocol=Protocol.XML_RPC).get_handler(request)
        assert isinstance(handler, XmlRpcHandler)

        # Server supports only JSON-RPC: NOK
        handler = RPCServer(supported_protocol=Protocol.JSON_RPC).get_handler(request)
        assert handler is None

    def test_system_procedures(self):
        server = RPCServer()

        assert "system.listMethods" in server.procedures
        assert "system.methodSignature" in server.procedures
        assert "system.methodHelp" in server.procedures
        assert "system.multicall" in server.procedures


# Define a server with basic config to register procedures
dummy_server = RPCServer()


@dummy_server.register_procedure
def dummy_procedure():
    return True


class TestRpcServerRegistration:
    def test_procedure_registration(self):
        wrapper = dummy_server.get_procedure("dummy_procedure")
        assert wrapper.function == dummy_procedure
        assert wrapper.name == "dummy_procedure"
