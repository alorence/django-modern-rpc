from modernrpc.auth.basic import http_basic_auth_login_required, http_basic_auth_superuser_required,\
    http_basic_auth_permissions_required, http_basic_auth_group_member_required
from modernrpc.core import rpc_method


@http_basic_auth_login_required
@rpc_method
def logged_user_required(x):
    return x*x


@http_basic_auth_login_required()
@rpc_method
def logged_user_required_alt(x):
    """Alternative method, to test coverage for decorator with and without parenthesis"""
    return x*x


@http_basic_auth_superuser_required
@rpc_method
def logged_superuser_required(x):
    return x + 10


@http_basic_auth_superuser_required()
@rpc_method
def logged_superuser_required_alt(x):
    """Alternative method, to test coverage for decorator with and without parenthesis"""
    return x + 10


@http_basic_auth_permissions_required(permissions='auth.delete_user')
@rpc_method
def delete_user_perm_required(x):
    return x


@http_basic_auth_permissions_required(permissions=['auth.delete_user', 'auth.add_user', 'auth.change_user'])
@rpc_method
def delete_user_perms_required(x):
    return x


@http_basic_auth_group_member_required(groups='A')
@rpc_method
def in_group_A_required(x):
    return x


@http_basic_auth_group_member_required(groups=['A', 'B'])
@rpc_method
def in_groups_AB_required(x):
    return x
