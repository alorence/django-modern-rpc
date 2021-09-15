import pytest
from django.contrib.auth.models import Permission, AnonymousUser, Group

from tests.conftest import get_url_with_auth
from .. import xmlrpclib, jsonrpclib


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
