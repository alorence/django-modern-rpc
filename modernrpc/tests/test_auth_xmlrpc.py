# coding: utf-8
import pytest

from . import python_xmlrpc


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


def test_xmlrpc_user_permissions(xmlrpc_client_as_user, john_doe, delete_user_perm, add_user_perm, change_user_perm):

    john_doe.user_permissions.add(delete_user_perm)

    assert xmlrpc_client_as_user.delete_user_perm_required(5) == 5
    assert xmlrpc_client_as_user.any_permission_required(5) == 5

    with pytest.raises(python_xmlrpc.ProtocolError) as exc_info:
        xmlrpc_client_as_user.all_permissions_required(5)

    assert exc_info.value.errcode == 403

    john_doe.user_permissions.add(add_user_perm, change_user_perm)
    assert xmlrpc_client_as_user.all_permissions_required(5) == 5


def test_xmlrpc_user_groups(xmlrpc_client_as_user, john_doe, group_A, group_B):

    john_doe.groups.add(group_A)

    assert xmlrpc_client_as_user.in_group_A_required(5) == 5
    assert xmlrpc_client_as_user.in_group_A_or_B_required(5) == 5

    assert pytest.raises(python_xmlrpc.ProtocolError, xmlrpc_client_as_user.in_groups_A_and_B_required, 5).value.errcode == 403
    assert pytest.raises(python_xmlrpc.ProtocolError, xmlrpc_client_as_user.in_groups_A_and_B_required_alt, 5).value.errcode == 403

    john_doe.groups.add(group_B)

    assert xmlrpc_client_as_user.in_groups_A_and_B_required(5) == 5
    assert xmlrpc_client_as_user.in_groups_A_and_B_required_alt(5) == 5


def test_custom_predicate_allowed(xmlrpc_client):

    assert 'xmlrpc' in xmlrpc_client.get_user_agent()


def test_custom_predicate_rejected(xmlrpc_client):

    with pytest.raises(python_xmlrpc.ProtocolError) as exc_info:
        xmlrpc_client.power_2(5)
    assert exc_info.value.errcode == 403
