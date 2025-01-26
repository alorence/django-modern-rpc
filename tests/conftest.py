from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.models import AnonymousUser, Group, Permission

from modernrpc.backends.builtin_json import BuiltinJSON
from modernrpc.backends.builtin_xmlrpc import BuiltinXmlRpc
from modernrpc.backends.simple_json import SimpleJSON
from modernrpc.backends.xml2dict import XML2Dict
from tests.helpers import build_json_rpc_request_data, build_xml_rpc_request_data

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest

    from modernrpc.backends.base import JsonRpcDeserializer, JsonRpcSerializer, XmlRpcDeserializer, XmlRpcSerializer


@pytest.fixture(scope="session")
def common_pwd():
    """The default password, used to create any user"""
    return "123456789!"


@pytest.fixture(scope="session")
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def john_doe(django_user_model, common_pwd):
    """Create and return a standard Django user"""
    return django_user_model.objects.create_user("johndoe", email="jd@example.com", password=common_pwd)


@pytest.fixture
def superuser(django_user_model, common_pwd):
    """Create and return a Django superuser"""
    return django_user_model.objects.create_superuser("admin", email="admin@example.com", password=common_pwd)


@pytest.fixture
def group_a(transactional_db):
    """Return a group named 'A'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name="A")
    return group


@pytest.fixture
def group_b(transactional_db):
    """Return a group named 'B'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name="B")
    return group


@pytest.fixture
def add_user_perm(transactional_db):
    """Return permission 'auth.add_user'"""
    return Permission.objects.get(codename="add_user")


@pytest.fixture
def change_user_perm(transactional_db):
    """Return permission 'auth.change_user'"""
    return Permission.objects.get(codename="change_user")


@pytest.fixture
def delete_user_perm(transactional_db):
    """Return permission 'auth.delete_user'"""
    return Permission.objects.get(codename="delete_user")


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
    def factory(path="/rpc", content_type="application/json", method_name="dummy", params=(), is_notification=False):
        data = build_json_rpc_request_data(method=method_name, params=params, is_notification=is_notification)
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


# List all backends supported in tests for deserialization (data to request object) and
# serialization (result to response data). These constants will be used to define some parametrized fixtures
# in order to ensure every test is run with all backends combinations
XML_DESERIALIZERS_CLASSES = [BuiltinXmlRpc, XML2Dict]
XML_SERIALIZERS_CLASSES = [BuiltinXmlRpc, XML2Dict]
JSON_DESERIALIZERS_CLASSES = [BuiltinJSON, SimpleJSON]
JSON_SERIALIZERS_CLASSES = [BuiltinJSON, SimpleJSON]


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
