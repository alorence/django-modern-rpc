# coding: utf-8
import pytest

from dummy_jsonrpc_client import ServerProxy, ProtocolError


def test_jsrpc_user_is_logged(live_server, john_doe):

    client = ServerProxy(live_server.url + '/all-rpc/', login=john_doe.username, password='123456')
    assert client.logged_user_required(5) == 25

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_user_required(4)


def test_jsrpc_user_is_admin(live_server, john_doe, superuser):

    client = ServerProxy(live_server.url + '/all-rpc/', login=superuser.username, password='123456')
    # Admin is OK
    assert client.logged_superuser_required(5) == 15

    with pytest.raises(ProtocolError):
        # JohnDoe don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/', login=john_doe.username, password='123456')
        client.logged_superuser_required(5)

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_superuser_required(4)


def test_jsrpc_user_has_single_permission(live_server, john_doe, superuser, auth_permissions):

    # Passing superuser credential always works
    client = ServerProxy(live_server.url + '/all-rpc/', superuser.username, '123456')
    assert client.delete_user_perm_required(5) == 5

    # John Doe doesn't have permission to execute the method...
    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.delete_user_perm_required(5)

    # ...until we give him the right permission
    delete_user_perm = auth_permissions[0]
    john_doe.user_permissions.add(delete_user_perm)

    # Now John Doe can call the method
    client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
    client.delete_user_perm_required(5)

    john_doe.user_permissions.clear()

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_superuser_required(4)


def test_jsrpc_user_has_multiple_permissions(live_server, john_doe, superuser, auth_permissions):

    # Passing superuser credential always works
    client = ServerProxy(live_server.url + '/all-rpc/', superuser.username, '123456')
    assert client.delete_user_perms_required(5) == 5

    # John Doe doesn't have permission to execute the method...
    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.delete_user_perms_required(5)

    # Add 1 permission...
    john_doe.user_permissions.add(auth_permissions[0])

    # ... is still not sufficient
    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.delete_user_perms_required(5)

    john_doe.user_permissions.add(auth_permissions[1], auth_permissions[2])

    client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
    assert client.delete_user_perms_required(5) == 5

    john_doe.user_permissions.clear()

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_superuser_required(4)
