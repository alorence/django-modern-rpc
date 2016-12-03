# coding: utf-8
import pytest
from django.utils.six.moves import xmlrpc_client


def test_xrpc_user_is_logged(live_server, john_doe):

    orig_url = live_server.url + '/all-rpc/'
    auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))

    client = xmlrpc_client.ServerProxy(auth_url)
    assert client.logged_user_required(5) == 25


def test_xrpc_user_is_not_logged(live_server):

    with pytest.raises(xmlrpc_client.ProtocolError):
        client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
        client.logged_user_required(4)


def test_xrpc_anon_is_superuser(live_server):

    orig_url = live_server.url + '/all-rpc/'

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_superuser_required(4)


def test_xrpc_user_is_superuser(live_server, john_doe):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))

    with pytest.raises(xmlrpc_client.ProtocolError):
        # JohnDoe don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.logged_superuser_required(5)


def test_xrpc_is_superuser_ok(live_server, superuser):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(superuser.username))

    client = xmlrpc_client.ServerProxy(superuser_auth_url)
    # Superuser is OK
    assert client.logged_superuser_required(5) == 15


def test_xrpc_anon_has_single_permission(live_server):

    orig_url = live_server.url + '/all-rpc/'

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_superuser_required(4)


def test_xrpc_user_has_single_permission(live_server, john_doe, auth_permissions):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))

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


def test_xrpc_superuser_has_single_permission(live_server, superuser, auth_permissions):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(superuser.username))

    # Passing superuser credential always works
    client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert client.delete_user_perm_required(5) == 5


def test_xrpc_anon_has_multiple_permissions(live_server):

    orig_url = live_server.url + '/all-rpc/'

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(orig_url)
        client.logged_superuser_required(4)


def test_xrpc_user_has_multiple_permissions(live_server, john_doe, auth_permissions):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))

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


def test_xrpc_superuser_has_multiple_permissions(live_server, superuser):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(superuser.username))

    # Passing superuser credential always works
    client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert client.delete_user_perms_required(5) == 5


def test_xrpc_anon_in_group_A(live_server):

    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
        client.in_group_A_required(4)


def test_xrpc_user_in_group_A(live_server, john_doe, group_A):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(john_doe.username))

    with pytest.raises(xmlrpc_client.ProtocolError):
        # John Doe doesn't have permission to execute the method...
        client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        client.in_group_A_required(4)

    # ...until we put him int the right group
    john_doe.groups.add(group_A)

    client = xmlrpc_client.ServerProxy(johndoe_auth_url)
    assert client.in_group_A_required(4) == 4


def test_xrpc_superuser_in_group_A(live_server, superuser):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = orig_url.replace('http://', 'http://{}:123456@'.format(superuser.username))

    client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert client.in_group_A_required(4) == 4
