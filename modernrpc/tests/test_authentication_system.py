# coding: utf-8
import pytest
from django.utils.six.moves import xmlrpc_client

import dummy_jsonrpc_client as jsonrpc_client


def get_url_with_auth(orig_url, username, password):
    return orig_url.replace('://', '://{uname}:{pwd}@').format(uname=username, pwd=password)


def test_user_is_logged(live_server, john_doe, common_pwd):

    orig_url = live_server.url + '/all-rpc/'
    auth_url = get_url_with_auth(orig_url, john_doe.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(auth_url)
    assert x_client.logged_user_required(5) == 25

    j_client = jsonrpc_client.ServerProxy(auth_url)
    assert j_client.logged_user_required(5) == 25


def test_user_is_not_logged(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.logged_user_required(4)

    j_client = jsonrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.logged_user_required(4)


def test_anon_is_superuser(live_server):

    orig_url = live_server.url + '/all-rpc/'

    x_client = xmlrpc_client.ServerProxy(orig_url)
    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        x_client.logged_superuser_required(4)

    j_client = jsonrpc_client.ServerProxy(orig_url)
    with pytest.raises(jsonrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        j_client.logged_superuser_required(4)


def test_user_is_superuser(live_server, john_doe, common_pwd):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = get_url_with_auth(orig_url, john_doe.username, common_pwd)

    with pytest.raises(xmlrpc_client.ProtocolError):
        # JohnDoe don't have sufficient permissions
        x_client = xmlrpc_client.ServerProxy(johndoe_auth_url)
        x_client.logged_superuser_required(5)

    with pytest.raises(jsonrpc_client.ProtocolError):
        # JohnDoe don't have sufficient permissions
        j_client = jsonrpc_client.ServerProxy(johndoe_auth_url)
        j_client.logged_superuser_required(5)


def test_is_superuser_ok(live_server, superuser, common_pwd):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = get_url_with_auth(orig_url, superuser.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(superuser_auth_url)
    # Superuser is OK
    assert x_client.logged_superuser_required(5) == 15

    j_client = jsonrpc_client.ServerProxy(superuser_auth_url)
    # Superuser is OK
    assert j_client.logged_superuser_required(5) == 15


def test_anon_has_single_permission(live_server):

    orig_url = live_server.url + '/all-rpc/'

    x_client = xmlrpc_client.ServerProxy(orig_url)
    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        x_client.logged_superuser_required(4)

    j_client = jsonrpc_client.ServerProxy(orig_url)
    with pytest.raises(jsonrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        j_client.logged_superuser_required(4)


def test_user_has_single_permission(live_server, john_doe, common_pwd, auth_permissions):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = get_url_with_auth(orig_url, john_doe.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(johndoe_auth_url)
    # John Doe doesn't have permission to execute the method...
    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.delete_user_perm_required(5)
    # ...until we give him the right permission
    delete_user_perm = auth_permissions[0]
    john_doe.user_permissions.add(delete_user_perm)
    # Now John Doe can call the method
    x_client.delete_user_perm_required(5)
    john_doe.user_permissions.clear()

    j_client = jsonrpc_client.ServerProxy(johndoe_auth_url)
    # John Doe doesn't have permission to execute the method...
    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.delete_user_perm_required(5)

    # ...until we give him the right permission
    delete_user_perm = auth_permissions[0]
    john_doe.user_permissions.add(delete_user_perm)

    # Now John Doe can call the method
    j_client.delete_user_perm_required(5)


def test_superuser_has_single_permission(live_server, superuser, common_pwd):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = get_url_with_auth(orig_url, superuser.username, common_pwd)

    # Passing superuser credential always works
    x_client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert x_client.delete_user_perm_required(5) == 5

    # Passing superuser credential always works
    j_client = jsonrpc_client.ServerProxy(superuser_auth_url)
    assert j_client.delete_user_perm_required(5) == 5


def test_anon_has_multiple_permissions(live_server):

    orig_url = live_server.url + '/all-rpc/'

    x_client = xmlrpc_client.ServerProxy(orig_url)
    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        x_client.logged_superuser_required(4)

    j_client = jsonrpc_client.ServerProxy(orig_url)
    with pytest.raises(jsonrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        j_client.logged_superuser_required(4)


def test_user_has_multiple_permissions(live_server, john_doe, common_pwd, auth_permissions):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = get_url_with_auth(orig_url, john_doe.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(johndoe_auth_url)
    # John Doe doesn't have permission to execute the method...
    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.delete_user_perms_required(5)
    # Add 1 permission...
    john_doe.user_permissions.add(auth_permissions[0])
    # ... is still not sufficient
    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.delete_user_perms_required(5)
    john_doe.user_permissions.add(auth_permissions[1], auth_permissions[2])
    assert x_client.delete_user_perms_required(5) == 5

    john_doe.user_permissions.clear()

    j_client = jsonrpc_client.ServerProxy(johndoe_auth_url)
    # John Doe doesn't have permission to execute the method...
    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.delete_user_perms_required(5)

    # Add 1 permission...
    john_doe.user_permissions.add(auth_permissions[0])

    # ... is still not sufficient
    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.delete_user_perms_required(5)
    john_doe.user_permissions.add(auth_permissions[1], auth_permissions[2])
    assert j_client.delete_user_perms_required(5) == 5

    john_doe.user_permissions.clear()


def test_superuser_has_multiple_permissions(live_server, superuser, common_pwd):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = get_url_with_auth(orig_url, superuser.username, common_pwd)

    # Passing superuser credential always works
    x_client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert x_client.delete_user_perms_required(5) == 5

    # Passing superuser credential always works
    j_client = jsonrpc_client.ServerProxy(superuser_auth_url)
    assert j_client.delete_user_perms_required(5) == 5


def test_anon_in_group_A(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        x_client.in_group_A_required(4)

    j_client = jsonrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(jsonrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        j_client.in_group_A_required(4)


def test_user_in_group_A(live_server, john_doe, common_pwd, group_A):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = get_url_with_auth(orig_url, john_doe.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(johndoe_auth_url)

    with pytest.raises(xmlrpc_client.ProtocolError):
        # John Doe doesn't have permission to execute the method...
        x_client.in_group_A_required(4)
    # ...until we put him int the right group
    john_doe.groups.add(group_A)
    assert x_client.in_group_A_required(4) == 4

    john_doe.groups.clear()

    j_client = jsonrpc_client.ServerProxy(johndoe_auth_url)
    with pytest.raises(jsonrpc_client.ProtocolError):
        # John Doe doesn't have permission to execute the method...
        j_client.in_group_A_required(4)

    # ...until we put him int the right group
    john_doe.groups.add(group_A)
    assert j_client.in_group_A_required(4) == 4


def test_superuser_in_group_A(live_server, superuser, common_pwd):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = get_url_with_auth(orig_url, superuser.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert x_client.in_group_A_required(4) == 4

    j_client = jsonrpc_client.ServerProxy(superuser_auth_url)
    assert j_client.in_group_A_required(4) == 4


def test_anon_in_A_and_B(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        x_client.in_groups_A_and_B_required(4)

    with pytest.raises(jsonrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        j_client = jsonrpc_client.ServerProxy(live_server.url + '/all-rpc/')
        j_client.in_groups_A_and_B_required(4)


def test_user_in_A_and_B(live_server, john_doe, common_pwd, group_A, group_B):

    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = get_url_with_auth(orig_url, john_doe.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(johndoe_auth_url)

    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.in_groups_A_and_B_required(4)
    john_doe.groups.add(group_A)
    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.in_groups_A_and_B_required(4)
    john_doe.groups.add(group_B)
    assert x_client.in_groups_A_and_B_required(4) == 4

    john_doe.groups.clear()

    j_client = jsonrpc_client.ServerProxy(johndoe_auth_url)
    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.in_groups_A_and_B_required(4)
    john_doe.groups.add(group_A)
    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.in_groups_A_and_B_required(4)
    john_doe.groups.add(group_B)
    assert j_client.in_groups_A_and_B_required(4) == 4


def test_superuser_in_A_and_B(live_server, superuser, common_pwd):

    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = get_url_with_auth(orig_url, superuser.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert x_client.in_groups_A_and_B_required(4) == 4

    j_client = jsonrpc_client.ServerProxy(superuser_auth_url)
    assert j_client.in_groups_A_and_B_required(4) == 4


def test_anon_in_A_or_B(live_server):

    x_client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(xmlrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        x_client.in_group_A_or_B_required(4)

    j_client = jsonrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(jsonrpc_client.ProtocolError):
        # Anonymous user don't have sufficient permissions
        j_client.in_group_A_or_B_required(9)


def test_user_in_A_or_B(live_server, john_doe, common_pwd, group_A, group_B):
    orig_url = live_server.url + '/all-rpc/'
    johndoe_auth_url = get_url_with_auth(orig_url, john_doe.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(johndoe_auth_url)

    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.in_group_A_or_B_required(4)

    john_doe.groups.add(group_A)
    assert x_client.in_group_A_or_B_required(9) == 9

    john_doe.groups.clear()

    with pytest.raises(xmlrpc_client.ProtocolError):
        x_client.in_group_A_or_B_required(4)

    john_doe.groups.add(group_B)
    assert x_client.in_group_A_or_B_required(9) == 9

    john_doe.groups.clear()

    j_client = jsonrpc_client.ServerProxy(johndoe_auth_url)
    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.in_group_A_or_B_required(9)

    john_doe.groups.add(group_A)
    assert j_client.in_group_A_or_B_required(9) == 9

    john_doe.groups.clear()

    with pytest.raises(jsonrpc_client.ProtocolError):
        j_client.in_group_A_or_B_required(9)

    john_doe.groups.add(group_B)
    assert j_client.in_group_A_or_B_required(9) == 9


def test_superuser_in_A_or_B(live_server, superuser, common_pwd):
    orig_url = live_server.url + '/all-rpc/'
    superuser_auth_url = get_url_with_auth(orig_url, superuser.username, common_pwd)

    x_client = xmlrpc_client.ServerProxy(superuser_auth_url)
    assert x_client.in_group_A_or_B_required(4) == 4

    j_client = jsonrpc_client.ServerProxy(superuser_auth_url)
    assert j_client.in_group_A_or_B_required(4) == 4
