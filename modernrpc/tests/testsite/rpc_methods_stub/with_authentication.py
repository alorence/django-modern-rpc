from modernrpc.auth import login_required, superuser_required, permissions_required
from modernrpc.core import rpc_method


@login_required
@rpc_method
def logged_user_required(x):
    return x*x


@login_required()
@rpc_method
def logged_user_required_alt(x):
    """Alternative method, to test coverage for decorator with and without parenthesis"""
    return x*x


@superuser_required
@rpc_method
def logged_superuser_required(x):
    return x + 10


@superuser_required()
@rpc_method
def logged_superuser_required_alt(x):
    """Alternative method, to test coverage for decorator with and without parenthesis"""
    return x + 10


@permissions_required(permissions='auth.delete_user')
@rpc_method
def delete_user_perm_required(x):
    return x


@permissions_required(permissions=['auth.delete_user', 'auth.add_user', 'auth.change_user'])
@rpc_method
def delete_user_perms_required(x):
    return x
