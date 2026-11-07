import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from modernrpc.jsonrpc.backends import JsonRpcDeserializer, JsonRpcSerializer
from modernrpc.jsonrpc.handler import JsonRpcSuccessResult
from modernrpc.xmlrpc.backends import XmlRpcDeserializer, XmlRpcSerializer
from modernrpc.xmlrpc.handler import XmlRpcSuccessResult


@pytest.mark.benchmark(group="xml-deserialize")
def test_xml_deserialize(
    benchmark: BenchmarkFixture, xml_deserializer: XmlRpcDeserializer, xmlrpc_request: str
) -> None:
    benchmark(xml_deserializer.loads, xmlrpc_request)


@pytest.mark.benchmark(group="json-deserialize")
def test_json_deserialize(
    benchmark: BenchmarkFixture, json_deserializer: JsonRpcDeserializer, jsonrpc_request: str
) -> None:
    benchmark(json_deserializer.loads, jsonrpc_request)


@pytest.mark.benchmark(group="xml-serialize")
def test_xml_serialize(
    benchmark: BenchmarkFixture, xml_serializer: XmlRpcSerializer, xmlrpc_result: XmlRpcSuccessResult
) -> None:
    res = benchmark(xml_serializer.dumps, xmlrpc_result)
    assert res


@pytest.mark.benchmark(group="json-serialize")
def test_json_serialize(
    benchmark: BenchmarkFixture, json_serializer: JsonRpcSerializer, jsonrpc_result: JsonRpcSuccessResult
) -> None:
    benchmark(json_serializer.dumps, jsonrpc_result)
