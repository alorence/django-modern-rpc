import xmlrpc.client
from http import HTTPStatus

import jsonrpcclient
import pytest
import requests

from modernrpc.exceptions import RPC_INTERNAL_ERROR


@pytest.fixture(params=["/rpc", "/async_rpc"], ids=["sync", "async"])
def server_path(request):
    """Return the URL path to the RPC server, for both sync and async versions"""
    return request.param


@pytest.mark.usefixtures("all_xml_deserializers", "all_xml_serializers")
class TestXmlRpc:
    def test_xml_rpc_standard_call(self, live_server, server_path):
        server = xmlrpc.client.ServerProxy(live_server.url + server_path, verbose=True)
        result = server.math.add(5, 8, 10)
        assert result == 23

    def test_xml_rpc_procedure_exception(self, live_server, server_path):
        server = xmlrpc.client.ServerProxy(live_server.url + server_path, verbose=True)

        with pytest.raises(xmlrpc.client.Fault) as exc_info:
            server.math.divide(9, 0)

        assert exc_info.value.faultCode == RPC_INTERNAL_ERROR
        assert exc_info.value.faultString == "Internal error: division by zero"

    def test_basic_xml_rpc_multicall(self, live_server, server_path):
        server = xmlrpc.client.ServerProxy(live_server.url + server_path, verbose=True)
        multicall = xmlrpc.client.MultiCall(server)
        multicall.math.add(1, 3, 5)
        multicall.math.add(98, -1)

        result = multicall()
        assert result[0] == 9
        assert result[1] == 97

    def test_xml_rpc_multicall_with_errors(self, live_server, server_path):
        server = xmlrpc.client.ServerProxy(live_server.url + server_path, verbose=True)
        multicall = xmlrpc.client.MultiCall(server)
        multicall.math.add(1, 3, 5)
        multicall.math.divide(98, 0)

        result = multicall()
        assert result[0] == 9
        with pytest.raises(xmlrpc.client.Fault):
            assert result[1]

    def test_xml_rpc_multicall(self, live_server, server_path):
        server = xmlrpc.client.ServerProxy(live_server.url + server_path, verbose=True)
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
class TestJsonRpc:
    def test_json_rpc_standard_call(self, live_server, server_path):
        request = jsonrpcclient.request(method="math.add", params=(5, 8, 10))
        response = requests.post(live_server.url + server_path, json=request)
        data = jsonrpcclient.parse_json(response.text)

        assert response.status_code == HTTPStatus.OK
        assert isinstance(data, jsonrpcclient.Ok)
        assert data.result == 23

    def test_json_rpc_basic_notification(self, live_server, server_path):
        request = jsonrpcclient.notification(method="math.add", params=(5, 8, 10))
        response = requests.post(live_server.url + server_path, json=request)

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.text == ""

    def test_json_rpc_procedure_exception(self, live_server, server_path):
        request = jsonrpcclient.request(method="math.divide", params=(12, 0))
        response = requests.post(live_server.url + server_path, json=request)
        data = jsonrpcclient.parse_json(response.text)

        assert response.status_code == HTTPStatus.OK
        assert isinstance(data, jsonrpcclient.Error)
        assert data.code == RPC_INTERNAL_ERROR
        assert data.message == "Internal error: division by zero"

    def test_json_rpc_batch_call(self, live_server, server_path):
        reqs = [
            jsonrpcclient.request(method="math.add", params=(5, 8, 10)),
            jsonrpcclient.request(method="math.divide", params=(13.0, 2)),
            jsonrpcclient.request(method="math.add", params=(99.1, 0.9)),
            jsonrpcclient.request(method="math.divide", params=(20, 0)),
            jsonrpcclient.request(method="math.divide", params=(20, 2)),
        ]
        response = requests.post(live_server.url + server_path, json=reqs)

        assert response.status_code == HTTPStatus.OK

        data: list[jsonrpcclient.Ok | jsonrpcclient.Error] = list(jsonrpcclient.parse(response.json()))
        assert len(data) == 5

        assert isinstance(data[0], jsonrpcclient.Ok)
        assert data[0].result == 23

        assert isinstance(data[1], jsonrpcclient.Ok)
        assert data[1].result == 6.5

        assert isinstance(data[2], jsonrpcclient.Ok)
        assert data[2].result == 100

        assert isinstance(data[3], jsonrpcclient.Error)
        assert data[3].code == RPC_INTERNAL_ERROR
        assert data[3].message == "Internal error: division by zero"

        assert isinstance(data[4], jsonrpcclient.Ok)
        assert data[4].result == 10


class TestCommonErrors:
    @pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "DELETE", "PATCH", "PUT"])
    def test_invalid_method(self, live_server, server_path, method):
        res = requests.request(method, live_server.url + server_path)

        assert res.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_no_content_type(self, live_server, server_path):
        res = requests.post(live_server.url + server_path, data="Hello World !", headers={"content-type": ""})

        assert res.status_code == HTTPStatus.BAD_REQUEST
        assert res.text == (
            "Unable to handle your request, the Content-Type header is mandatory to allow server to "
            "determine which handler can interpret your request."
        )

    def test_invalid_content_type(self, live_server, server_path):
        res = requests.post(live_server.url + server_path, data="Hello World !", headers={"content-type": "text/html"})

        assert res.status_code == HTTPStatus.BAD_REQUEST
        assert res.text == "Unable to handle your request, unsupported Content-Type text/html."
