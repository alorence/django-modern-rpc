import pytest


@pytest.mark.benchmark(group="xml-deserialize")
def test_xml_deserialize(benchmark, xml_deserializer, xmlrpc_request):
    benchmark(xml_deserializer.loads, xmlrpc_request)


@pytest.mark.benchmark(group="json-deserialize")
def test_json_deserialize(benchmark, json_deserializer, jsonrpc_request):
    benchmark(json_deserializer.loads, jsonrpc_request)


@pytest.mark.benchmark(group="xml-serialize")
def test_xml_serialize(benchmark, xml_serializer, xmlrpc_result):
    res = benchmark(xml_serializer.dumps, xmlrpc_result)
    assert res


@pytest.mark.benchmark(group="json-serialize")
def test_json_serialize(benchmark, json_serializer, jsonrpc_result):
    benchmark(json_serializer.dumps, jsonrpc_result)
