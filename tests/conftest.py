from typing import Any

import pytest
from django.test import RequestFactory
from pytest_django import Settings

from modernrpc import RpcServer
from modernrpc.jsonrpc.backends import JsonRpcDeserializer, JsonRpcSerializer
from modernrpc.jsonrpc.handler import RequestIdType
from modernrpc.xmlrpc.backends import XmlRpcDeserializer, XmlRpcSerializer
from tests.helpers import (
    JSON_DESERIALIZERS_CLASSES,
    JSON_SERIALIZERS_CLASSES,
    XML_DESERIALIZERS_CLASSES,
    XML_SERIALIZERS_CLASSES,
    JsonRpcBatchRF,
    JsonRpcRF,
    XmlRpcRF,
    build_json_rpc_request_data,
    build_xml_rpc_request_data,
)


@pytest.fixture
def server() -> RpcServer:
    return RpcServer()


@pytest.fixture(
    scope="session",
    params=["application/json", "application/json-rpc", "application/jsonrequest"],
)
def jsonrpc_content_type(request: pytest.FixtureRequest):
    """
    A Content-Type value supported by JSON-RPC handler.

    Fixture parametrization will cause each JSON-RPC test to be run N times
    """
    return request.param


@pytest.fixture(
    scope="session",
    params=["application/xml", "text/xml"],
)
def xmlrpc_content_type(request: pytest.FixtureRequest) -> str:
    """
    A Content-Type value supported by XML-RPC handler.

    Fixture parametrization will cause each XML-RPC test to be run N times
    """
    return request.param


@pytest.fixture
def xmlrpc_rf(rf: RequestFactory) -> XmlRpcRF:
    def factory(
        path: str = "/rpc",
        content_type: str = "application/xml",
        method_name: str = "dummy",
        params: tuple[Any, ...] = (),
    ):
        data = build_xml_rpc_request_data(method=method_name, params=params)
        return rf.post(path, data=data, content_type=content_type)

    return factory


@pytest.fixture
def jsonrpc_rf(rf: RequestFactory) -> JsonRpcRF:
    def factory(
        path: str = "/rpc",
        content_type: str = "application/json",
        method_name: str = "dummy",
        params: tuple[Any, ...] = (),
        is_notif: bool = False,
        req_id: RequestIdType = None,
    ):
        data = build_json_rpc_request_data(method=method_name, params=params, is_notification=is_notif, req_id=req_id)
        return rf.post(path, data=data, content_type=content_type)

    return factory


@pytest.fixture
def jsonrpc_batch_rf(rf: RequestFactory) -> JsonRpcBatchRF:
    def factory(
        path: str = "/rpc",
        content_type: str = "application/json",
        requests: list[tuple[str, tuple[Any, ...], bool]] | None = None,
    ):
        data = [
            build_json_rpc_request_data(method=method_name, params=params, is_notification=is_notification)
            for method_name, params, is_notification in requests or []
        ]
        return rf.post(path, data=data, content_type=content_type)

    return factory


# The next 4 fixtures can be used to retrieve an instance of the corresponding backend
# See 'test_backends_xml.py' and 'test_backends_json.py' for example uses
@pytest.fixture(scope="session", params=XML_DESERIALIZERS_CLASSES)
def xml_deserializer(request: pytest.FixtureRequest) -> XmlRpcDeserializer:
    return request.param()


@pytest.fixture(scope="session", params=XML_SERIALIZERS_CLASSES)
def xml_serializer(request: pytest.FixtureRequest) -> XmlRpcSerializer:
    return request.param()


@pytest.fixture(scope="session", params=JSON_DESERIALIZERS_CLASSES)
def json_deserializer(request: pytest.FixtureRequest) -> JsonRpcDeserializer:
    return request.param()


@pytest.fixture(scope="session", params=JSON_SERIALIZERS_CLASSES)
def json_serializer(request: pytest.FixtureRequest) -> JsonRpcSerializer:
    return request.param()


# The next 4 fixtures can be requested with the "usefixtures" mark at class or function level to ensure that
# tests ran against live_server will be executed with all combinations. See 'test_e2e.py' for an example
@pytest.fixture(params=XML_DESERIALIZERS_CLASSES)
def all_xml_deserializers(settings: Settings, request: pytest.FixtureRequest) -> None:
    klass = request.param
    settings.MODERNRPC_XML_DESERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}


@pytest.fixture(params=XML_SERIALIZERS_CLASSES)
def all_xml_serializers(settings: Settings, request: pytest.FixtureRequest) -> None:
    klass = request.param
    settings.MODERNRPC_XML_SERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}


@pytest.fixture(params=JSON_DESERIALIZERS_CLASSES)
def all_json_deserializers(settings: Settings, request: pytest.FixtureRequest) -> None:
    klass = request.param
    settings.MODERNRPC_JSON_DESERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}


@pytest.fixture(params=JSON_SERIALIZERS_CLASSES)
def all_json_serializers(settings: Settings, request: pytest.FixtureRequest) -> None:
    klass = request.param
    settings.MODERNRPC_JSON_SERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}
