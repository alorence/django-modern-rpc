import base64

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.utils import six

from modernrpc import auth


def http_basic_auth_check_user(request, user_validation_func, *args):
    """
    Inspect the given request and extract the user / password from HTTP_AUTHORIZATION header.
    Then try to use it to authenticate against Django User model. If user can be authenticated, it is returned.
    If no user is found, an anonymous user object is returned.
    :param request: The request to inspect
    :param user_validation_func:
    :return:
    """
    return user_validation_func(http_basic_auth_get_user(request), *args)


def http_basic_auth_get_user(request):
    """Inspect the given request to find a logged user. If not found, the header HTTP_AUTHORIZATION
    is read for 'Basic Auth' login and password, and try to authenticate against default UserModel.
    Always return a User instance (possibly anonymous, meaning authentication failed)"""

    try:
        # If standard middlewares already authenticated a user, use it
        if not request.user.is_anonymous():
            return request.user
    except AttributeError:
        pass

    # This was grabbed from https://www.djangosnippets.org/snippets/243/
    # Thanks to http://stackoverflow.com/a/1087736/1887976
    if 'HTTP_AUTHORIZATION' in request.META:
        auth_data = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth_data) == 2 and auth_data[0].lower() == "basic":
            uname, passwd = base64.b64decode(auth_data[1]).decode('utf-8').split(':')
            login(request, authenticate(username=uname, password=passwd))

    # In all cases, return the current request's user (may be anonymous user if no login succeed)
    try:
        return request.user
    except AttributeError:
        return AnonymousUser()


# Decorator
def http_basic_auth_login_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged users"""

    def decorated(_func):
        return auth.set_authentication_predicate(_func, http_basic_auth_check_user, [auth.user_is_logged])

    # If @http_basic_auth_login_required() is used (with parenthesis)
    if func is None:
        return decorated

    # If @http_basic_auth_login_required is used without parenthesis
    return decorated(func)


# Decorator
def http_basic_auth_superuser_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged superusers"""
    def decorated(_func):
        return auth.set_authentication_predicate(_func, http_basic_auth_check_user, [auth.user_is_superuser])

    # If @http_basic_auth_superuser_required() is used (with parenthesis)
    if func is None:
        return decorated

    # If @http_basic_auth_superuser_required is used without parenthesis
    return decorated(func)


# Decorator
def http_basic_auth_permissions_required(permissions):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""
    def decorated(func):
        if isinstance(permissions, six.string_types):
            # Check a single permission
            return auth.set_authentication_predicate(func, http_basic_auth_check_user,
                                                     [auth.user_has_perm, permissions])

        # Check many permissions
        return auth.set_authentication_predicate(func, http_basic_auth_check_user,
                                                 [auth.user_has_all_perms, permissions])
    return decorated


# Decorator
def http_basic_auth_any_of_permissions_required(permissions):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""
    def decorated(func):
        # Check many permissions
        return auth.set_authentication_predicate(func, http_basic_auth_check_user,
                                                 [auth.user_has_any_perm, permissions])
    return decorated


# Decorator
def http_basic_auth_group_member_required(groups):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""
    def decorated(func):

        if isinstance(groups, six.string_types):
            # Check user is in a group
            return auth.set_authentication_predicate(func, http_basic_auth_check_user, [auth.user_in_group, groups])

        # Check user is in many group
        return auth.set_authentication_predicate(func, http_basic_auth_check_user, [auth.user_in_any_group, groups])

    return decorated


# Decorator
def http_basic_auth_all_groups_member_required(groups):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""
    def decorated(func):
        # Check user is in many group
        return auth.set_authentication_predicate(func, http_basic_auth_check_user, [auth.user_in_all_groups, groups])

    return decorated
