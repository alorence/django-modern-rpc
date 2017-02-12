# coding: utf-8
import pytest

from dummy_jsonrpc_client import ServerProxy, ProtocolError


def test_jsrpc_user_is_logged(live_server, john_doe):

    client = ServerProxy(live_server.url + '/all-rpc/', login=john_doe.username, password='123456')
    assert client.logged_user_required(5) == 25


def test_jsrpc_user_is_not_logged(live_server):

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_user_required(4)


def test_jsrpc_anon_is_superuser(live_server):

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_superuser_required(4)


def test_jsrpc_user_is_superuser(live_server, john_doe):

    with pytest.raises(ProtocolError):
        # JohnDoe don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/', login=john_doe.username, password='123456')
        client.logged_superuser_required(5)


def test_jsrpc_is_superuser_ok(live_server, superuser):

    client = ServerProxy(live_server.url + '/all-rpc/', login=superuser.username, password='123456')
    # Superuser is OK
    assert client.logged_superuser_required(5) == 15


def test_jsrpc_anon_has_single_permission(live_server):

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_superuser_required(4)


def test_jsrpc_user_has_single_permission(live_server, john_doe, auth_permissions):

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


def test_jsrpc_superuser_has_single_permission(live_server, superuser):

    # Passing superuser credential always works
    client = ServerProxy(live_server.url + '/all-rpc/', superuser.username, '123456')
    assert client.delete_user_perm_required(5) == 5


def test_jsrpc_anon_has_multiple_permissions(live_server):

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.logged_superuser_required(4)


def test_jsrpc_user_has_multiple_permissions(live_server, john_doe, auth_permissions):

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


def test_jsrpc_superuser_has_multiple_permissions(live_server, superuser):

    # Passing superuser credential always works
    client = ServerProxy(live_server.url + '/all-rpc/', superuser.username, '123456')
    assert client.delete_user_perms_required(5) == 5


def test_jsrpc_anon_in_group_A(live_server):

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.in_group_A_required(4)


def test_jsrpc_user_in_group_A(live_server, john_doe, group_A):

    with pytest.raises(ProtocolError):
        # John Doe doesn't have permission to execute the method...
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.in_group_A_required(4)

    # ...until we put him int the right group
    john_doe.groups.add(group_A)

    client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
    assert client.in_group_A_required(4) == 4


def test_jsrpc_superuser_in_group_A(live_server, superuser):

    client = ServerProxy(live_server.url + '/all-rpc/', superuser.username, '123456')
    assert client.in_group_A_required(4) == 4


def test_jsrpc_anon_in_A_and_B(live_server):

    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.in_groups_A_and_B_required(4)


def test_jsrpc_user_in_A_and_B(live_server, john_doe, group_A, group_B):

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.in_groups_A_and_B_required(4)

    john_doe.groups.add(group_A)

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.in_groups_A_and_B_required(4)

    john_doe.groups.add(group_B)

    client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
    assert client.in_groups_A_and_B_required(4) == 4


def test_jsrpc_superuser_in_A_and_B(live_server, superuser):

    client = ServerProxy(live_server.url + '/all-rpc/', superuser.username, '123456')
    assert client.in_groups_A_and_B_required(4) == 4


def test_jsrpc_anon_in_A_or_B(live_server):
    with pytest.raises(ProtocolError):
        # Anonymous user don't have sufficient permissions
        client = ServerProxy(live_server.url + '/all-rpc/')
        client.in_group_A_or_B_required(9)


def test_jsrpc_user_in_A_or_B(live_server, john_doe, group_A, group_B):
    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.in_group_A_or_B_required(9)

    john_doe.groups.add(group_A)
    assert client.in_group_A_or_B_required(9) == 9

    john_doe.groups.clear()

    with pytest.raises(ProtocolError):
        client = ServerProxy(live_server.url + '/all-rpc/', john_doe.username, '123456')
        client.in_group_A_or_B_required(9)

    john_doe.groups.add(group_B)
    assert client.in_group_A_or_B_required(9) == 9


def test_jsrpc_superuser_in_A_or_B(live_server, superuser):

    client = ServerProxy(live_server.url + '/all-rpc/', superuser.username, '123456')
    assert client.in_group_A_or_B_required(4) == 4

