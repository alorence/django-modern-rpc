import base64

from django.contrib.auth import authenticate
from django.utils import six

from modernrpc import auth


def http_basic_auth_get_user(request):

    # By default, let the AuthenticationMiddleware do the job
    user = request.user

    if user.is_anonymous():
        # This was grabbed from https://www.djangosnippets.org/snippets/243/
        # Thanks to http://stackoverflow.com/a/1087736/1887976
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                # HTTP Basic auth support
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':')
                    user = authenticate(username=uname, password=passwd)

    return user


def http_basic_auth_check_user(request, *params):
    # Extract the user check function to execute
    new_params = list(params)
    check_function = new_params.pop(0)

    # Inject the username retrieved from request
    user = http_basic_auth_get_user(request)

    return check_function(user, *new_params)


def http_basic_auth_login_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged users"""

    def decorated(function):
        return auth.user_pass_test(function, http_basic_auth_check_user, [auth.check_user_is_logged])

    # If @http_basic_auth_login_required is used without any argument nor parenthesis
    if func is None:
        def decorator(f):
            return decorated(f)
        return decorator

    # If @http_basic_auth_login_required() is used with parenthesis
    return decorated(func)


def http_basic_auth_superuser_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged superusers"""
    def decorated(function):
        return auth.user_pass_test(function, http_basic_auth_check_user, [auth.check_user_is_superuser])

    # If @http_basic_auth_superuser_required is used without any argument nor parenthesis
    if func is None:
        def decorator(f):
            return decorated(f)
        return decorator

    # If @http_basic_auth_superuser_required() is used with parenthesis
    return decorated(func)


def http_basic_auth_permissions_required(permissions):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""

    def decorated(function):

        if isinstance(permissions, six.string_types):
            # Check a single permission
            return auth.user_pass_test(function, http_basic_auth_check_user, [auth.check_user_has_perm, permissions])

        # Check many permissions
        return auth.user_pass_test(function, http_basic_auth_check_user, [auth.check_user_has_perms, permissions])

    return decorated


def http_basic_auth_group_member_required(groups):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""

    def decorated(function):

        if isinstance(groups, six.string_types):
            # Check user is in a group
            return auth.user_pass_test(function, http_basic_auth_check_user, [auth.check_user_in_group, groups])

        # Check user is in many group
        return auth.user_pass_test(function, http_basic_auth_check_user, [auth.check_user_in_groups, groups])

    return decorated
