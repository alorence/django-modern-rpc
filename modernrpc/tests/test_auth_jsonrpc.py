# coding: utf-8

import jsonrpcclient.exceptions
import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR


class JsonRpcBase:

    error_klass = jsonrpcclient.exceptions.ReceivedErrorResponse


class TestAuthAnonymousUser(JsonRpcBase):

    def test_display_username(self, jsonrpc_client):
        with pytest.raises(Exception) as excpinfo:
            jsonrpc_client.display_authenticated_user()
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_logged_user_required(self, jsonrpc_client):
        with pytest.raises(Exception) as excpinfo:
            jsonrpc_client.logged_user_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_logged_user_required_alt(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.logged_user_required_alt(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_logged_superuser_required(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.logged_superuser_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_logged_superuser_required_alt(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.logged_superuser_required_alt(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_delete_user_perm_required(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.delete_user_perm_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_any_permission_required(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.any_permission_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_all_permissions_required(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.all_permissions_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_group_A_required(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.in_group_A_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_groups_A_and_B_required(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.in_groups_A_and_B_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_groups_A_and_B_required_alt(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.in_groups_A_and_B_required_alt(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_group_A_or_B_required(self, jsonrpc_client):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client.in_group_A_or_B_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message


class TestAuthStandardUser(JsonRpcBase):

    def test_display_username(self, jsonrpc_client_as_user, john_doe):
        assert john_doe.username in jsonrpc_client_as_user.display_authenticated_user()

    def test_logged_user_required(self, jsonrpc_client_as_user):
        assert jsonrpc_client_as_user.logged_user_required(5) == 5

    def test_logged_user_required_alt(self, jsonrpc_client_as_user):
        assert jsonrpc_client_as_user.logged_user_required_alt(5) == 5

    def test_logged_superuser_required(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.logged_superuser_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_logged_superuser_required_alt(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.logged_superuser_required_alt(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_delete_user_perm_required(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.delete_user_perm_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_any_permission_required(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.any_permission_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_all_permissions_required(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.all_permissions_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_group_A_required(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.in_group_A_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_groups_A_and_B_required(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.in_groups_A_and_B_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_groups_A_and_B_required_alt(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.in_groups_A_and_B_required_alt(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message

    def test_in_group_A_or_B_required(self, jsonrpc_client_as_user):
        with pytest.raises(self.error_klass) as excpinfo:
            jsonrpc_client_as_user.in_group_A_or_B_required(5)
        assert excpinfo.value.code == RPC_INTERNAL_ERROR
        assert 'Authentication failed' in excpinfo.value.message


class TestAuthSuperuser(JsonRpcBase):

    def test_display_username(self, jsonrpc_client_as_superuser, superuser):
        assert superuser.username in jsonrpc_client_as_superuser.display_authenticated_user()

    def test_logged_user_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.logged_user_required(5) == 5

    def test_logged_user_required_alt(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.logged_user_required_alt(5) == 5

    def test_logged_superuser_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.logged_superuser_required(5) == 5

    def test_logged_superuser_required_alt(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.logged_superuser_required_alt(5) == 5

    def test_delete_user_perm_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.delete_user_perm_required(5) == 5

    def test_any_permission_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.any_permission_required(5) == 5

    def test_all_permissions_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.all_permissions_required(5) == 5

    def test_in_group_A_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.in_group_A_required(5) == 5

    def test_in_groups_A_and_B_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.in_groups_A_and_B_required(5) == 5

    def test_in_groups_A_and_B_required_alt(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.in_groups_A_and_B_required_alt(5) == 5

    def test_in_group_A_or_B_required(self, jsonrpc_client_as_superuser):
        assert jsonrpc_client_as_superuser.in_group_A_or_B_required(5) == 5


def test_jsonrpc_user_permissions(jsonrpc_client_as_user, john_doe, delete_user_perm, add_user_perm, change_user_perm):

    john_doe.user_permissions.add(delete_user_perm)

    assert jsonrpc_client_as_user.delete_user_perm_required(5) == 5
    assert jsonrpc_client_as_user.any_permission_required(5) == 5

    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse) as excpinfo:
        jsonrpc_client_as_user.all_permissions_required(5)

    assert excpinfo.value.code == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excpinfo.value.message

    john_doe.user_permissions.add(add_user_perm, change_user_perm)
    assert jsonrpc_client_as_user.all_permissions_required(5) == 5


def test_jsonrpc_user_groups_1(jsonrpc_client_as_user, john_doe, group_A, group_B):

    john_doe.groups.add(group_A)

    assert jsonrpc_client_as_user.in_group_A_required(5) == 5
    assert jsonrpc_client_as_user.in_group_A_or_B_required(5) == 5


def test_jsonrpc_user_groups_2(jsonrpc_client_as_user, john_doe, group_A, group_B):

    john_doe.groups.add(group_A)

    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse) as excpinfo:
        jsonrpc_client_as_user.in_groups_A_and_B_required(5)
    assert excpinfo.value.code == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excpinfo.value.message

    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse) as excpinfo:
        jsonrpc_client_as_user.in_groups_A_and_B_required_alt(5)
    assert excpinfo.value.code == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excpinfo.value.message


def test_jsonrpc_user_groups_3(jsonrpc_client_as_user, john_doe, group_A, group_B):

    john_doe.groups.add(group_A, group_B)

    assert jsonrpc_client_as_user.in_groups_A_and_B_required(5) == 5
    assert jsonrpc_client_as_user.in_groups_A_and_B_required_alt(5) == 5


def test_custom_predicate_allowed(jsonrpc_client):

    assert 'python-requests' in jsonrpc_client.get_user_agent()


def test_custom_predicate_rejected(jsonrpc_client):

    with pytest.raises(jsonrpcclient.exceptions.ReceivedErrorResponse) as excpinfo:
        jsonrpc_client.power_2(5)
    assert excpinfo.value.code == RPC_INTERNAL_ERROR
    assert 'Authentication failed' in excpinfo.value.message
