# coding: utf-8
import pytest
from django.contrib.auth.models import Permission, Group, AnonymousUser

import modernrpc.core
from . import xmlrpclib, jsonrpclib


@pytest.fixture(scope='function')
def rpc_registry():
    # With Python 3.5+, we could use _dump = {**orig_dict} to easily perform a shallow copy
    # Unfortunately, we still maintain compatibility with Python 2.7, 3.3 & 3.4
    # See https://www.python.org/dev/peps/pep-0448/
    # See https://stackoverflow.com/a/46180556/1887976
    _registry_dump = modernrpc.core.registry._registry.copy()
    yield modernrpc.core.registry
    modernrpc.core.registry._registry = _registry_dump


@pytest.fixture(scope='session')
def common_pwd():
    """The default password, used to create any user"""
    return '123456789!'


@pytest.fixture(scope='session')
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def john_doe(django_user_model, common_pwd):
    """Create and return a standard Django user"""
    return django_user_model.objects.create_user('johndoe', email='jd@example.com', password=common_pwd)


@pytest.fixture
def superuser(django_user_model, common_pwd):
    """Create and return a Django superuser"""
    return django_user_model.objects.create_superuser('admin', email='admin@example.com', password=common_pwd)


@pytest.fixture
def group_A(db):
    """Return a group named 'A'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name='A')
    return group


@pytest.fixture
def group_B(db):
    """Return a group named 'B'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name='B')
    return group


@pytest.fixture
def add_user_perm():
    """Return permission 'auth.add_user'"""
    return Permission.objects.get(codename='add_user')


@pytest.fixture
def change_user_perm():
    """Return permission 'auth.change_user'"""
    return Permission.objects.get(codename='change_user')


@pytest.fixture
def delete_user_perm():
    """Return permission 'auth.delete_user'"""
    return Permission.objects.get(codename='delete_user')


@pytest.fixture(scope='session')
def all_rpc_url(live_server):
    """Return the default RPC test endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/all-rpc/'


@pytest.fixture(scope='session')
def all_rpc_doc_url(live_server):
    """Return the URL to view configured to serve RPC documentation. See 'testsite.urls' for additional info."""
    return live_server + '/all-rpc-doc/'


@pytest.fixture(scope='session')
def json_only_url(live_server):
    """Return the JSON-RPC specific endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/json-only/'


@pytest.fixture(scope='session')
def xml_only_url(live_server):
    """Return the XML-RPC specific endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/xml-only/'


@pytest.fixture(scope='session')
def xmlrpc_client(all_rpc_url):
    """Return the default XML-RPC client"""
    return xmlrpclib.ServerProxy(all_rpc_url)


@pytest.fixture(scope='session', params=[None, "application/json-rpc", "application/jsonrequest"])
def jsonrpc_client(request, all_rpc_url):
    """Return the default JSON-RPC client"""
    client = jsonrpclib.HTTPClient(all_rpc_url)
    if request.param is not None:
        # Allow parametrization of jsonrpc client
        client.session.headers.update({"Content-Type": request.param})
    return client


def get_url_with_auth(orig_url, username, password):
    return orig_url.replace('://', '://{uname}:{pwd}@').format(uname=username, pwd=password)


@pytest.fixture
def xmlrpc_client_as_superuser(all_rpc_url, superuser, common_pwd):
    """Return the default XML-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, superuser.username, common_pwd)
    return xmlrpclib.ServerProxy(endpoint)


@pytest.fixture
def jsonrpc_client_as_superuser(all_rpc_url, superuser, common_pwd):
    """Return the default JSON-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, superuser.username, common_pwd)
    return jsonrpclib.HTTPClient(endpoint)


@pytest.fixture
def xmlrpc_client_as_user(all_rpc_url, john_doe, common_pwd):
    """Return the default XML-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, john_doe.username, common_pwd)
    return xmlrpclib.ServerProxy(endpoint)


@pytest.fixture
def jsonrpc_client_as_user(all_rpc_url, john_doe, common_pwd):
    """Return the default JSON-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, john_doe.username, common_pwd)
    return jsonrpclib.HTTPClient(endpoint)
