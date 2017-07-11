from modernrpc.auth import set_authentication_predicate
from modernrpc.auth.basic import http_basic_auth_login_required, http_basic_auth_superuser_required,\
    http_basic_auth_permissions_required, http_basic_auth_group_member_required, \
    http_basic_auth_any_of_permissions_required, http_basic_auth_all_groups_member_required
from modernrpc.core import rpc_method, REQUEST_KEY


@http_basic_auth_login_required
@rpc_method
def logged_user_required(x):
    return x


@http_basic_auth_login_required()
@rpc_method
def logged_user_required_alt(x):
    """Alternative method, to test coverage for decorator with and without parenthesis"""
    return x


@http_basic_auth_superuser_required
@rpc_method
def logged_superuser_required(x):
    return x


@http_basic_auth_superuser_required()
@rpc_method
def logged_superuser_required_alt(x):
    """Alternative method, to test coverage for decorator with and without parenthesis"""
    return x


@http_basic_auth_permissions_required(permissions='auth.delete_user')
@rpc_method
def delete_user_perm_required(x):
    return x


@http_basic_auth_any_of_permissions_required(permissions=['auth.delete_user', 'auth.add_user', 'auth.change_user'])
@rpc_method
def any_permission_required(x):
    return x


@http_basic_auth_permissions_required(permissions=['auth.delete_user', 'auth.add_user', 'auth.change_user'])
@rpc_method
def all_permissions_required(x):
    return x


@http_basic_auth_group_member_required(groups='A')
@rpc_method
def in_group_A_required(x):
    return x


@http_basic_auth_group_member_required(groups=['A'])
@http_basic_auth_group_member_required(groups='B')
@rpc_method
def in_groups_A_and_B_required(x):
    return x


@http_basic_auth_all_groups_member_required(groups=['A', 'B'])
@rpc_method
def in_groups_A_and_B_required_alt(x):
    return x


@http_basic_auth_group_member_required(groups=['A', 'B'])
@rpc_method
def in_group_A_or_B_required(x):
    return x


@http_basic_auth_login_required
@rpc_method
def display_authenticated_user(**kwargs):
    u = kwargs[REQUEST_KEY].user
    return 'username: {}'.format('Anonymous' if u.is_anonymous() else u.username)


def allow_python_callers(request):
    return 'python' in request.META.get('HTTP_USER_AGENT').lower()


def reject_python_callers(request):
    return 'python' not in request.META.get('HTTP_USER_AGENT').lower()


@rpc_method()
@set_authentication_predicate(allow_python_callers)
def get_user_agent(**kwargs):
    request = kwargs.get(REQUEST_KEY)
    return request.META.get('HTTP_USER_AGENT')


@rpc_method
@set_authentication_predicate(reject_python_callers)
def power_2(x):
    return x * x
