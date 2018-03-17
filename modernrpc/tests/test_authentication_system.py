# coding: utf-8
from django.utils.six.moves import xmlrpc_client
from jsonrpcclient.exceptions import ReceivedErrorResponse
from jsonrpcclient.http_client import HTTPClient
from pytest import raises

from modernrpc.exceptions import RPC_INTERNAL_ERROR


def get_url_with_auth(orig_url, username, password):
    return orig_url.replace('://', '://{uname}:{pwd}@').format(uname=username, pwd=password)


def test_xmlrpc_anon_user_auth(live_server):

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    assert raises(xmlrpc_client.ProtocolError, c.logged_user_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.logged_user_required_alt, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.logged_superuser_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.logged_superuser_required_alt, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.delete_user_perm_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.any_permission_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.all_permissions_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_group_A_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_groups_A_and_B_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_groups_A_and_B_required_alt, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_group_A_or_B_required, 5).value.errcode == 403


def test_xmlrpc_superuser_auth(live_server, superuser, common_pwd):

    admin_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', superuser.username, common_pwd)
    c = xmlrpc_client.ServerProxy(admin_auth_url)

    assert c.logged_user_required(5) == 5
    assert c.logged_user_required_alt(5) == 5
    assert c.logged_superuser_required(5) == 5
    assert c.logged_superuser_required_alt(5) == 5
    assert c.delete_user_perm_required(5) == 5
    assert c.any_permission_required(5) == 5
    assert c.all_permissions_required(5) == 5
    assert c.in_group_A_required(5) == 5
    assert c.in_groups_A_and_B_required(5) == 5
    assert c.in_groups_A_and_B_required_alt(5) == 5
    assert c.in_group_A_or_B_required(5) == 5


def test_xmlrpc_user_auth(live_server, john_doe, common_pwd):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = xmlrpc_client.ServerProxy(johndoe_auth_url)

    assert c.logged_user_required(5) == 5
    assert c.logged_user_required_alt(5) == 5

    assert raises(xmlrpc_client.ProtocolError, c.logged_superuser_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.logged_superuser_required_alt, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.delete_user_perm_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.all_permissions_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.any_permission_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_group_A_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_groups_A_and_B_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_groups_A_and_B_required_alt, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_group_A_or_B_required, 5).value.errcode == 403


def test_xmlrpc_user_permissions(live_server, john_doe, common_pwd, delete_user_perm, add_user_perm, change_user_perm):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = xmlrpc_client.ServerProxy(johndoe_auth_url)

    john_doe.user_permissions.add(delete_user_perm)

    assert c.delete_user_perm_required(5) == 5
    assert c.any_permission_required(5) == 5

    with raises(xmlrpc_client.ProtocolError) as exc_info:
        c.all_permissions_required(5)

    assert exc_info.value.errcode == 403

    john_doe.user_permissions.add(add_user_perm, change_user_perm)
    assert c.all_permissions_required(5) == 5


def test_xmlrpc_user_groups(live_server, john_doe, common_pwd, group_A, group_B):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = xmlrpc_client.ServerProxy(johndoe_auth_url)

    john_doe.groups.add(group_A)

    assert c.in_group_A_required(5) == 5
    assert c.in_group_A_or_B_required(5) == 5

    assert raises(xmlrpc_client.ProtocolError, c.in_groups_A_and_B_required, 5).value.errcode == 403
    assert raises(xmlrpc_client.ProtocolError, c.in_groups_A_and_B_required_alt, 5).value.errcode == 403

    john_doe.groups.add(group_B)

    assert c.in_groups_A_and_B_required(5) == 5
    assert c.in_groups_A_and_B_required_alt(5) == 5


def test_jsonrpc_anon_user_auth(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    assert raises(ReceivedErrorResponse, c.request, 'logged_user_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'logged_user_required_alt', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'logged_superuser_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'logged_superuser_required_alt', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'delete_user_perm_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'any_permission_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'all_permissions_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'in_group_A_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required', 5).value.code == RPC_INTERNAL_ERROR
    e = raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required_alt', 5)
    assert e.value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'in_group_A_or_B_required', 5).value.code == RPC_INTERNAL_ERROR


def test_jsonrpc_superuser_auth(live_server, superuser, common_pwd):

    admin_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', superuser.username, common_pwd)
    c = HTTPClient(admin_auth_url)

    assert c.logged_user_required(5) == 5
    assert c.logged_user_required_alt(5) == 5
    assert c.logged_superuser_required(5) == 5
    assert c.logged_superuser_required_alt(5) == 5
    assert c.delete_user_perm_required(5) == 5
    assert c.any_permission_required(5) == 5
    assert c.all_permissions_required(5) == 5
    assert c.in_group_A_required(5) == 5
    assert c.in_groups_A_and_B_required(5) == 5
    assert c.in_groups_A_and_B_required_alt(5) == 5
    assert c.in_group_A_or_B_required(5) == 5


def test_jsonrpc_user_auth(live_server, john_doe, common_pwd):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = HTTPClient(johndoe_auth_url)

    assert c.logged_user_required(5) == 5
    assert c.logged_user_required_alt(5) == 5

    assert raises(ReceivedErrorResponse, c.request, 'logged_superuser_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'logged_superuser_required_alt', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'delete_user_perm_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'any_permission_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'all_permissions_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'in_group_A_required', 5).value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required', 5).value.code == RPC_INTERNAL_ERROR
    e = raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required_alt', 5)
    assert e.value.code == RPC_INTERNAL_ERROR
    assert raises(ReceivedErrorResponse, c.request, 'in_group_A_or_B_required', 5).value.code == RPC_INTERNAL_ERROR


def test_jsonrpc_user_permissions(live_server, john_doe, common_pwd, delete_user_perm, add_user_perm, change_user_perm):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = HTTPClient(johndoe_auth_url)

    john_doe.user_permissions.add(delete_user_perm)

    assert c.delete_user_perm_required(5) == 5
    assert c.any_permission_required(5) == 5

    with raises(ReceivedErrorResponse) as exc_info:
        c.all_permissions_required(5)

    assert exc_info.value.code == RPC_INTERNAL_ERROR

    john_doe.user_permissions.add(add_user_perm, change_user_perm)
    assert c.all_permissions_required(5) == 5


def test_jsonrpc_user_groups(live_server, john_doe, common_pwd, group_A, group_B):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = HTTPClient(johndoe_auth_url)

    john_doe.groups.add(group_A)

    assert c.in_group_A_required(5) == 5
    assert c.in_group_A_or_B_required(5) == 5

    assert raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required', 5).value.code == RPC_INTERNAL_ERROR
    e = raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required_alt', 5)
    assert e.value.code == RPC_INTERNAL_ERROR

    john_doe.groups.add(group_B)

    assert c.in_groups_A_and_B_required(5) == 5
    assert c.in_groups_A_and_B_required_alt(5) == 5


def test_http_basic_auth_user_in_request(live_server, john_doe, superuser, common_pwd):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = HTTPClient(johndoe_auth_url)

    assert 'username: johndoe' == c.display_authenticated_user()

    c = HTTPClient(live_server.url + '/all-rpc/')
    c.session.auth = (superuser.username, common_pwd)

    assert 'username: admin' == c.display_authenticated_user()


def test_custom_predicate_allowed(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    assert 'python-requests' in c.get_user_agent()

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    assert 'xmlrpc' in c.get_user_agent()


def test_custom_predicate_rejected(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    with raises(ReceivedErrorResponse) as exc_info:
        c.power_2(5)
    assert exc_info.value.code == RPC_INTERNAL_ERROR

    c = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    with raises(xmlrpc_client.ProtocolError) as exc_info:
        c.power_2(5)
    assert exc_info.value.errcode == 403
