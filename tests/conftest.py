from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from modernrpc import RpcServer
from tests.helpers import (
    JSON_DESERIALIZERS_CLASSES,
    JSON_SERIALIZERS_CLASSES,
    XML_DESERIALIZERS_CLASSES,
    XML_SERIALIZERS_CLASSES,
    build_json_rpc_request_data,
    build_xml_rpc_request_data,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest

    from modernrpc.jsonrpc.backends import JsonRpcDeserializer, JsonRpcSerializer
    from modernrpc.xmlrpc.backends import XmlRpcDeserializer, XmlRpcSerializer


@pytest.fixture
def server():
    return RpcServer()


@pytest.fixture(
    scope="session",
    params=["application/json", "application/json-rpc", "application/jsonrequest"],
)
def jsonrpc_content_type(request):
    """
    A Content-Type value supported by JSON-RPC handler.

    Fixture parametrization will cause each JSON-RPC test to be run N times
    """
    return request.param


@pytest.fixture(
    scope="session",
    params=["application/xml", "text/xml"],
)
def xmlrpc_content_type(request):
    """
    A Content-Type value supported by XML-RPC handler.

    Fixture parametrization will cause each XML-RPC test to be run N times
    """
    return request.param


@pytest.fixture
def xmlrpc_rf(rf) -> Callable[..., HttpRequest]:
    def factory(path="/rpc", content_type="application/xml", method_name="dummy", params=()):
        data = build_xml_rpc_request_data(method=method_name, params=params)
        return rf.post(path, data=data, content_type=content_type)

    return factory


@pytest.fixture
def jsonrpc_rf(rf) -> Callable[..., HttpRequest]:
    def factory(
        path="/rpc", content_type="application/json", method_name="dummy", params=(), is_notif=False, req_id=None
    ):
        data = build_json_rpc_request_data(method=method_name, params=params, is_notification=is_notif, req_id=req_id)
        return rf.post(path, data=data, content_type=content_type)

    return factory


@pytest.fixture
def jsonrpc_batch_rf(rf) -> Callable[..., HttpRequest]:
    def factory(path="/rpc", content_type="application/json", requests: list[str, tuple, bool] | None = None):
        data = [
            build_json_rpc_request_data(method=method_name, params=params, is_notification=is_notification)
            for method_name, params, is_notification in requests or []
        ]
        return rf.post(path, data=data, content_type=content_type)

    return factory


# The next 4 fixtures can be used to retrieve an instance of the corresponding backend
# See 'test_backends_xml.py' and 'test_backends_json.py' for example uses
@pytest.fixture(scope="session", params=XML_DESERIALIZERS_CLASSES)
def xml_deserializer(request) -> XmlRpcDeserializer:
    return request.param()


@pytest.fixture(scope="session", params=XML_SERIALIZERS_CLASSES)
def xml_serializer(request) -> XmlRpcSerializer:
    return request.param()


@pytest.fixture(scope="session", params=JSON_DESERIALIZERS_CLASSES)
def json_deserializer(request) -> JsonRpcDeserializer:
    return request.param()


@pytest.fixture(scope="session", params=JSON_SERIALIZERS_CLASSES)
def json_serializer(request) -> JsonRpcSerializer:
    return request.param()


# The next 4 fixtures can be requested with "usefixtures" mark at class or function level to ensure that
# tests ran against live_server will be executed with all combinations. See 'test_e2e.py' for an example
@pytest.fixture(params=XML_DESERIALIZERS_CLASSES)
def all_xml_deserializers(settings, request):
    klass = request.param
    settings.MODERNRPC_XML_DESERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}


@pytest.fixture(params=XML_SERIALIZERS_CLASSES)
def all_xml_serializers(settings, request):
    klass = request.param
    settings.MODERNRPC_XML_SERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}


@pytest.fixture(params=JSON_DESERIALIZERS_CLASSES)
def all_json_deserializers(settings, request):
    klass = request.param
    settings.MODERNRPC_JSON_DESERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}


@pytest.fixture(params=JSON_SERIALIZERS_CLASSES)
def all_json_serializers(settings, request):
    klass = request.param
    settings.MODERNRPC_JSON_SERIALIZER = {"class": f"{klass.__module__}.{klass.__name__}"}
