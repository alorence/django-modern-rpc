# coding: utf-8
import pytest
from django.contrib.auth.models import Permission, Group, AnonymousUser
from jsonrpcclient import http_client as jsonrpcclient

from . import python_xmlrpc

# Password used by all tests users created here
COMMON_PASSWORD = '123456'


@pytest.fixture
def common_pwd():
    return COMMON_PASSWORD


@pytest.fixture
@pytest.mark.django_db()
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
@pytest.mark.django_db()
def john_doe(django_user_model):
    return django_user_model.objects.create_user('johndoe', email='jd@example.com', password=COMMON_PASSWORD)


@pytest.fixture
@pytest.mark.django_db()
def superuser(django_user_model):
    return django_user_model.objects.create_superuser('admin', email='admin@example.com', password=COMMON_PASSWORD)


@pytest.fixture
def group_A(db):
    group, _ = Group.objects.get_or_create(name='A')
    return group


@pytest.fixture
def group_B(db):
    group, _ = Group.objects.get_or_create(name='B')
    return group


@pytest.fixture
@pytest.mark.django_db()
def add_user_perm():
    return Permission.objects.get(codename='add_user')


@pytest.fixture
@pytest.mark.django_db()
def change_user_perm():
    return Permission.objects.get(codename='change_user')


@pytest.fixture
@pytest.mark.django_db()
def delete_user_perm():
    return Permission.objects.get(codename='delete_user')


@pytest.fixture(scope='session')
def live_server_url(live_server):
    return live_server.url


@pytest.fixture(scope='session')
def all_rpc_url(live_server):
    return live_server + '/all-rpc/'


@pytest.fixture(scope='session')
def all_rpc_doc_url(live_server):
    return live_server + '/all-rpc-doc/'


@pytest.fixture(scope='session')
def json_only_url(live_server):
    return live_server + '/json-only/'


@pytest.fixture(scope='session')
def xml_only_url(live_server):
    return live_server + '/xml-only/'


@pytest.fixture(scope='session')
def xmlrpc_client(all_rpc_url):
    return python_xmlrpc.ServerProxy(all_rpc_url)


@pytest.fixture(scope='session')
def jsonrpc_client(all_rpc_url):
    return jsonrpcclient.HTTPClient(all_rpc_url)
