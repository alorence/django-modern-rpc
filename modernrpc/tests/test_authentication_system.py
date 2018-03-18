# coding: utf-8
import pytest
from jsonrpcclient.exceptions import ReceivedErrorResponse
from jsonrpcclient.http_client import HTTPClient

from modernrpc.exceptions import RPC_INTERNAL_ERROR
from . import python_xmlrpc


# TODO: this should be unused at the end...
def get_url_with_auth(orig_url, username, password):
    return orig_url.replace('://', '://{uname}:{pwd}@').format(uname=username, pwd=password)


class XmlRpcBase:

    error_klass = python_xmlrpc.ProtocolError


class TestAuthAnonymousUser(XmlRpcBase):

    def test_logged_user_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_user_required(5)
        assert excpinfo.value.errcode == 403

    def test_logged_user_required_alt(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_user_required_alt(5)
        assert excpinfo.value.errcode == 403

    def test_logged_superuser_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_superuser_required(5)
        assert excpinfo.value.errcode == 403

    def test_logged_superuser_required_alt(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_superuser_required_alt(5)
        assert excpinfo.value.errcode == 403

    def test_delete_user_perm_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.delete_user_perm_required(5)
        assert excpinfo.value.errcode == 403

    def test_any_permission_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.any_permission_required(5)
        assert excpinfo.value.errcode == 403

    def test_all_permissions_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.all_permissions_required(5)
        assert excpinfo.value.errcode == 403

    def test_in_group_A_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_group_A_required(5)
        assert excpinfo.value.errcode == 403

    def test_in_groups_A_and_B_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_groups_A_and_B_required(5)
        assert excpinfo.value.errcode == 403

    def test_in_groups_A_and_B_required_alt(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_groups_A_and_B_required_alt(5)
        assert excpinfo.value.errcode == 403

    def test_in_group_A_or_B_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_group_A_or_B_required(5)
        assert excpinfo.value.errcode == 403


class TestAuthStandardUser(XmlRpcBase):

    def test_logged_user_required(self, xmlrpc_client_as_user):
        assert xmlrpc_client_as_user.logged_user_required(5) == 5

    def test_logged_user_required_alt(self, xmlrpc_client_as_user):
        assert xmlrpc_client_as_user.logged_user_required_alt(5) == 5

    def test_logged_superuser_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.logged_superuser_required(5)
        assert excpinfo.value.errcode == 403

    def test_logged_superuser_required_alt(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.logged_superuser_required_alt(5)
        assert excpinfo.value.errcode == 403

    def test_delete_user_perm_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.delete_user_perm_required(5)
        assert excpinfo.value.errcode == 403

    def test_any_permission_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.any_permission_required(5)
        assert excpinfo.value.errcode == 403

    def test_all_permissions_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.all_permissions_required(5)
        assert excpinfo.value.errcode == 403

    def test_in_group_A_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_group_A_required(5)
        assert excpinfo.value.errcode == 403

    def test_in_groups_A_and_B_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_groups_A_and_B_required(5)
        assert excpinfo.value.errcode == 403

    def test_in_groups_A_and_B_required_alt(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_groups_A_and_B_required_alt(5)
        assert excpinfo.value.errcode == 403

    def test_in_group_A_or_B_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_group_A_or_B_required(5)
        assert excpinfo.value.errcode == 403


class TestAuthSuperuser(XmlRpcBase):

    def test_logged_user_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.logged_user_required(5) == 5

    def test_logged_user_required_alt(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.logged_user_required_alt(5) == 5

    def test_logged_superuser_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.logged_superuser_required(5) == 5

    def test_logged_superuser_required_alt(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.logged_superuser_required_alt(5) == 5

    def test_delete_user_perm_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.delete_user_perm_required(5) == 5

    def test_any_permission_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.any_permission_required(5) == 5

    def test_all_permissions_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.all_permissions_required(5) == 5

    def test_in_group_A_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.in_group_A_required(5) == 5

    def test_in_groups_A_and_B_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.in_groups_A_and_B_required(5) == 5

    def test_in_groups_A_and_B_required_alt(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.in_groups_A_and_B_required_alt(5) == 5

    def test_in_group_A_or_B_required(self, xmlrpc_client_as_superuser):
        assert xmlrpc_client_as_superuser.in_group_A_or_B_required(5) == 5



def test_xmlrpc_user_permissions(live_server, john_doe, common_pwd, delete_user_perm, add_user_perm, change_user_perm):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = python_xmlrpc.ServerProxy(johndoe_auth_url)

    john_doe.user_permissions.add(delete_user_perm)

    assert c.delete_user_perm_required(5) == 5
    assert c.any_permission_required(5) == 5

    with pytest.raises(python_xmlrpc.ProtocolError) as exc_info:
        c.all_permissions_required(5)

    assert exc_info.value.errcode == 403

    john_doe.user_permissions.add(add_user_perm, change_user_perm)
    assert c.all_permissions_required(5) == 5


def test_xmlrpc_user_groups(live_server, john_doe, common_pwd, group_A, group_B):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = python_xmlrpc.ServerProxy(johndoe_auth_url)

    john_doe.groups.add(group_A)

    assert c.in_group_A_required(5) == 5
    assert c.in_group_A_or_B_required(5) == 5

    assert pytest.raises(python_xmlrpc.ProtocolError, c.in_groups_A_and_B_required, 5).value.errcode == 403
    assert pytest.raises(python_xmlrpc.ProtocolError, c.in_groups_A_and_B_required_alt, 5).value.errcode == 403

    john_doe.groups.add(group_B)

    assert c.in_groups_A_and_B_required(5) == 5
    assert c.in_groups_A_and_B_required_alt(5) == 5


def test_jsonrpc_anon_user_auth(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')

    assert pytest.raises(ReceivedErrorResponse, c.request, 'logged_user_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'logged_user_required_alt', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'logged_superuser_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'logged_superuser_required_alt', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'delete_user_perm_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'any_permission_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'all_permissions_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'in_group_A_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required', 5).value.code == RPC_INTERNAL_ERROR
    e = pytest.raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required_alt', 5)
    assert e.value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'in_group_A_or_B_required', 5).value.code == RPC_INTERNAL_ERROR


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

    assert pytest.raises(ReceivedErrorResponse, c.request, 'logged_superuser_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'logged_superuser_required_alt', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'delete_user_perm_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'any_permission_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'all_permissions_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'in_group_A_required', 5).value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required', 5).value.code == RPC_INTERNAL_ERROR
    e = pytest.raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required_alt', 5)
    assert e.value.code == RPC_INTERNAL_ERROR
    assert pytest.raises(ReceivedErrorResponse, c.request, 'in_group_A_or_B_required', 5).value.code == RPC_INTERNAL_ERROR


def test_jsonrpc_user_permissions(live_server, john_doe, common_pwd, delete_user_perm, add_user_perm, change_user_perm):

    johndoe_auth_url = get_url_with_auth(live_server.url + '/all-rpc/', john_doe.username, common_pwd)
    c = HTTPClient(johndoe_auth_url)

    john_doe.user_permissions.add(delete_user_perm)

    assert c.delete_user_perm_required(5) == 5
    assert c.any_permission_required(5) == 5

    with pytest.raises(ReceivedErrorResponse) as exc_info:
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

    assert pytest.raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required', 5).value.code == RPC_INTERNAL_ERROR
    e = pytest.raises(ReceivedErrorResponse, c.request, 'in_groups_A_and_B_required_alt', 5)
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

    c = python_xmlrpc.ServerProxy(live_server.url + '/all-rpc/')
    assert 'xmlrpc' in c.get_user_agent()


def test_custom_predicate_rejected(live_server):

    c = HTTPClient(live_server.url + '/all-rpc/')
    with pytest.raises(ReceivedErrorResponse) as exc_info:
        c.power_2(5)
    assert exc_info.value.code == RPC_INTERNAL_ERROR

    c = python_xmlrpc.ServerProxy(live_server.url + '/all-rpc/')
    with pytest.raises(python_xmlrpc.ProtocolError) as exc_info:
        c.power_2(5)
    assert exc_info.value.errcode == 403
