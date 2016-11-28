# coding: utf-8
import pytest
from django.utils.six.moves import xmlrpc_client


def test_xrpc_user_is_logged(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')

    orig_url = live_server.url + '/all-rpc/'
    auth_url = orig_url.replace('http://', 'http://johndoe:123456@')

    client = xmlrpc_client.ServerProxy(auth_url)
    assert client.logged_user_required(5) == 25

    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_user_required(4)


def test_xrpc_user_is_admin(live_server, django_user_model):

    django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')
    django_user_model.objects.create_superuser('admin', email='admin@example.com', password='123456')

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://johndoe:123456@')
    admin_auth_url = orig_url.replace('http://', 'http://admin:123456@')

    client = xmlrpc_client.ServerProxy(admin_auth_url)
    # Admin is OK
    assert client.logged_superuser_required(5) == 15

    with pytest.raises(xmlrpc_client.ProtocolError):
        # JohnDoe don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.logged_superuser_required(5)

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_superuser_required(4)


def test_xrpc_user_has_single_permission(live_server, django_user_model, auth_permissions):

    jd = django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')
    django_user_model.objects.create_superuser('admin', email='admin@example.com', password='123456')

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://johndoe:123456@')
    admin_auth_url = orig_url.replace('http://', 'http://admin:123456@')

    # Passing superuser credential always works
    client = xmlrpc_client.ServerProxy(admin_auth_url)
    assert client.delete_user_perm_required(5) == 5

    # John Doe doesn't have permission to execute the method...
    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.delete_user_perm_required(5)

    # ...until we give him the right permission
    delete_user_perm = auth_permissions[0]
    jd.user_permissions.add(delete_user_perm)

    # Now John Doe can call the method
    client = xmlrpc_client.ServerProxy(johndoe_auth_url)
    client.delete_user_perm_required(5)

    jd.user_permissions.clear()


def test_xrpc_user_has_multiple_permissions(live_server, django_user_model, auth_permissions):

    jd = django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')
    django_user_model.objects.create_superuser('admin', email='admin@example.com', password='123456')

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://johndoe:123456@')
    admin_auth_url = orig_url.replace('http://', 'http://admin:123456@')

    # Passing superuser credential always works
    client = xmlrpc_client.ServerProxy(admin_auth_url)
    assert client.delete_user_perms_required(5) == 5

    # John Doe doesn't have permission to execute the method...
    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.delete_user_perms_required(5)

    # Add 1 permission...
    jd.user_permissions.add(auth_permissions[0])

    # ... is still not sufficient
    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.delete_user_perms_required(5)

    jd.user_permissions.add(auth_permissions[1], auth_permissions[2])

    client = xmlrpc_client.ServerProxy(johndoe_auth_url)
    assert client.delete_user_perms_required(5) == 5

    jd.user_permissions.clear()
