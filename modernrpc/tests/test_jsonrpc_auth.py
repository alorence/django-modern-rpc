# coding: utf-8
import pytest
from django.contrib.auth.models import Permission

from dummy_jsonrpc_client import ServerProxy, ProtocolError


def test_jsrpc_user_is_logged(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')

    client = ServerProxy(live_server.url + '/all-rpc/', login='johndoe', password='123456')
    assert client.logged_user_required(5) == 25

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_user_required(4)


def test_jsrpc_user_is_admin(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')
    django_user_model.objects.create_superuser('admin', email='admin@example.com', password='123456')

    client = ServerProxy(live_server.url + '/all-rpc/', login='admin', password='123456')
    # Admin is OK
    assert client.superuser_required(5) == 15

    with pytest.raises(ProtocolError):
        # JohnDoe don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/', login='johndoe', password='123456')
        client.superuser_required(5)

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.superuser_required(4)


def test_jsrpc_user_has_single_permission(live_server, django_user_model):

    jd = django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')
    django_user_model.objects.create_superuser('admin', email='admin@example.com', password='123456')

    # Passing superuser credential always works
    client = ServerProxy(live_server.url + '/all-rpc/', 'admin', '123456')
    assert client.delete_user_perm_required(5) == 5

    # John Doe doesn't have permission to execute the method...
    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', 'johndoe', '123456')
        client.delete_user_perm_required(5)

    # ...until we give him the right permission
    jd.user_permissions.add(Permission.objects.get_by_natural_key('delete_user', 'auth', 'user'))

    # Now John Doe can call the method
    client = ServerProxy(live_server.url + '/all-rpc/', 'johndoe', '123456')
    client.delete_user_perm_required(5)
