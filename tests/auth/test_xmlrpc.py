# coding: utf-8
import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR
from tests import xmlrpclib


class XmlRpcBase:
    error_klass = xmlrpclib.Fault


class TestAuthAnonymousUser(XmlRpcBase):

    def test_display_username(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.display_authenticated_user()
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_logged_user_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_user_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_logged_user_required_alt(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_user_required_alt(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_logged_superuser_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_superuser_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_logged_superuser_required_alt(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.logged_superuser_required_alt(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_delete_user_perm_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.delete_user_perm_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_any_permission_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.any_permission_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_all_permissions_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.all_permissions_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_group_A_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_group_A_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_groups_A_and_B_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_groups_A_and_B_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_groups_A_and_B_required_alt(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_groups_A_and_B_required_alt(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_group_A_or_B_required(self, xmlrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client.in_group_A_or_B_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString


class TestAuthStandardUser(XmlRpcBase):

    def test_display_username(self, xmlrpc_client_as_user, john_doe):
        assert john_doe.username in xmlrpc_client_as_user.display_authenticated_user()

    def test_logged_user_required(self, xmlrpc_client_as_user):
        assert xmlrpc_client_as_user.logged_user_required(5) == 5

    def test_logged_user_required_alt(self, xmlrpc_client_as_user):
        assert xmlrpc_client_as_user.logged_user_required_alt(5) == 5

    def test_logged_superuser_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.logged_superuser_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_logged_superuser_required_alt(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.logged_superuser_required_alt(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_delete_user_perm_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.delete_user_perm_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_any_permission_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.any_permission_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_all_permissions_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.all_permissions_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_group_A_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_group_A_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_groups_A_and_B_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_groups_A_and_B_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_groups_A_and_B_required_alt(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_groups_A_and_B_required_alt(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString

    def test_in_group_A_or_B_required(self, xmlrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            xmlrpc_client_as_user.in_group_A_or_B_required(5)
        assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.faultString


class TestAuthSuperuser(XmlRpcBase):

    def test_display_username(self, xmlrpc_client_as_superuser, superuser):
        assert superuser.username in xmlrpc_client_as_superuser.display_authenticated_user()

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


def test_xmlrpc_user_permissions(xmlrpc_client_as_user, john_doe, delete_user_perm, add_user_perm, change_user_perm):
    john_doe.user_permissions.add(delete_user_perm)

    assert xmlrpc_client_as_user.delete_user_perm_required(5) == 5
    assert xmlrpc_client_as_user.any_permission_required(5) == 5

    with pytest.raises(xmlrpclib.Fault) as excpinfo:
        xmlrpc_client_as_user.all_permissions_required(5)

    assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excpinfo.value.faultString

    john_doe.user_permissions.add(add_user_perm, change_user_perm)
    assert xmlrpc_client_as_user.all_permissions_required(5) == 5


def test_xmlrpc_user_groups(xmlrpc_client_as_user, john_doe, group_A, group_B):
    john_doe.groups.add(group_A)

    assert xmlrpc_client_as_user.in_group_A_required(5) == 5
    assert xmlrpc_client_as_user.in_group_A_or_B_required(5) == 5

    with pytest.raises(xmlrpclib.Fault) as excpinfo:
        xmlrpc_client_as_user.in_groups_A_and_B_required(5)
    assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excpinfo.value.faultString

    with pytest.raises(xmlrpclib.Fault) as excpinfo:
        xmlrpc_client_as_user.in_groups_A_and_B_required_alt(5)
    assert excpinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excpinfo.value.faultString

    john_doe.groups.add(group_B)

    assert xmlrpc_client_as_user.in_groups_A_and_B_required(5) == 5
    assert xmlrpc_client_as_user.in_groups_A_and_B_required_alt(5) == 5


def test_custom_predicate_allowed(xmlrpc_client):
    assert 'xmlrpc' in xmlrpc_client.get_user_agent()


def test_custom_predicate_rejected(xmlrpc_client):
    with pytest.raises(xmlrpclib.ProtocolError) as excpinfo:
        xmlrpc_client.power_2(5)
    assert excpinfo.value.errcode == 403


def test_xmlrpc_multicall_with_auth(xmlrpc_client):
    multicall = xmlrpclib.MultiCall(xmlrpc_client)
    multicall.add(7, 3)
    multicall.logged_superuser_required(5)
    result = multicall()

    assert isinstance(result, xmlrpclib.MultiCallIterator)
    assert result[0] == 10
    with pytest.raises(xmlrpclib.Fault) as excinfo:
        print(result[1])
    assert excinfo.value.faultCode == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excinfo.value.faultString


def test_xmlrpc_multicall_with_auth_2(xmlrpc_client_as_superuser):
    multicall = xmlrpclib.MultiCall(xmlrpc_client_as_superuser)
    multicall.add(7, 3)
    multicall.logged_superuser_required(5)
    result = multicall()

    assert isinstance(result, xmlrpclib.MultiCallIterator)
    assert result[0] == 10
    assert result[1] == 5
