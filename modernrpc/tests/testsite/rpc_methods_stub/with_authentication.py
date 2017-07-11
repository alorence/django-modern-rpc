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


def forbid_bots_access(request):
    forbidden_bots = [
        'Googlebot',  # Google
        'Bingbot',  # Microsoft
        'Slurp',  # Yahoo
        'DuckDuckBot',  # DuckDuckGo
        'Baiduspider',  # Baidu
        'YandexBot',  # Yandex
        'facebot',  # Facebook
    ]
    incoming_UA = request.meta.get('HTTP_USER_AGENT')
    if not incoming_UA:
        return False

    for bot_ua in forbidden_bots:
        # If we detect the caller is one of the bots listed above...
        if bot_ua.lower() in incoming_UA.lower():
            # ... forbid access
            return False

    # In all other cases, allow access
    return True


@rpc_method()
@set_authentication_predicate(forbid_bots_access)
def custom_auth_predicate(x):
    return x * x
