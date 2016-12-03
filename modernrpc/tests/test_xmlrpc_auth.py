# coding: utf-8
import pytest
from django.utils.six.moves import xmlrpc_client


def test_xrpc_user_is_logged(live_server, john_doe):

    orig_url = live_server.url + '/all-rpc/'
    auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))

    client = xmlrpc_client.ServerProxy(auth_url)
    assert client.logged_user_required(5) == 25

    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_user_required(4)


def test_xrpc_user_is_admin(live_server, john_doe, superuser):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))
    admin_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(superuser.username))

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


def test_xrpc_user_has_single_permission(live_server, john_doe, superuser, auth_permissions):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))
    admin_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(superuser.username))

    # Passing superuser credential always works
    client = xmlrpc_client.ServerProxy(admin_auth_url)
    assert client.delete_user_perm_required(5) == 5

    # John Doe doesn't have permission to execute the method...
    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.delete_user_perm_required(5)

    # ...until we give him the right permission
    delete_user_perm = auth_permissions[0]
    john_doe.user_permissions.add(delete_user_perm)

    # Now John Doe can call the method
    client = xmlrpc_client.ServerProxy(johndoe_auth_url)
    client.delete_user_perm_required(5)

    john_doe.user_permissions.clear()

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_superuser_required(4)


def test_xrpc_user_has_multiple_permissions(live_server, john_doe, superuser, auth_permissions):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))
    admin_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(superuser.username))

    # Passing superuser credential always works
    client = xmlrpc_client.ServerProxy(admin_auth_url)
    assert client.delete_user_perms_required(5) == 5

    # John Doe doesn't have permission to execute the method...
    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.delete_user_perms_required(5)

    # Add 1 permission...
    john_doe.user_permissions.add(auth_permissions[0])

    # ... is still not sufficient
    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.delete_user_perms_required(5)

    john_doe.user_permissions.add(auth_permissions[1], auth_permissions[2])

    client = xmlrpc_client.ServerProxy(johndoe_auth_url)
    assert client.delete_user_perms_required(5) == 5

    john_doe.user_permissions.clear()

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_superuser_required(4)
