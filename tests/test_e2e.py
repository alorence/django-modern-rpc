import xmlrpc.client

import pytest


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpcE2E:
    def test_xml_rpc_basic_call(self, live_server):
        server = xmlrpc.client.ServerProxy(live_server.url + "/rpc", verbose=True)
        result = server.math.add(5, 8, 10)
        assert result == 23

    def test_basic_xml_rpc_multicall(self, live_server):
        server = xmlrpc.client.ServerProxy(live_server.url + "/rpc", verbose=True)
        multicall = xmlrpc.client.MultiCall(server)
        multicall.math.add(1, 3, 5)
        multicall.math.add(98, -1)

        result = multicall()
        assert result[0] == 9
        assert result[1] == 97

    def test_xml_rpc_multicall_with_errors(self, live_server):
        server = xmlrpc.client.ServerProxy(live_server.url + "/rpc", verbose=True)
        multicall = xmlrpc.client.MultiCall(server)
        multicall.math.add(1, 3, 5)
        multicall.math.divide(98, 0)

        result = multicall()
        assert result[0] == 9
        with pytest.raises(xmlrpc.client.Fault):
            assert result[1]

    def test_xml_rpc_multicall(self, live_server):
        server = xmlrpc.client.ServerProxy(live_server.url + "/rpc", verbose=True)
        multicall = xmlrpc.client.MultiCall(server)
        multicall.math.add(1, 3, 5)
        multicall.math.divide(13.0, 2)
        multicall.math.add(99.1, 0.9)
        multicall.math.divide(20, 0)
        multicall.math.divide(20, 2)
        result = multicall()

        assert result[0] == 9
        assert result[1] == 6.5
        assert result[2] == 100.0
        with pytest.raises(xmlrpc.client.Fault):
            assert result[3]
        assert result[4] == 10


@pytest.mark.usefixtures("all_json_deserializers", "all_json_serializers")
class TestJsonRpcE2E: ...
