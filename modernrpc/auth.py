# coding: utf-8

from django.contrib.auth.models import Group
from django.utils import six


def user_pass_test(func, test_function, params=None):
    """Decorator. Specify an RPC method is only available to logged user validating the given test_function"""

    def decorated(function):
        function.modernrpc_auth_check_function = test_function
        function.modernrpc_auth_check_params = params
        return function

    return decorated(func)


def check_user_is_logged(user):
    return user is not None and not user.is_anonymous()


def login_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged users"""

    def decorated(function):
        return user_pass_test(function, check_user_is_logged)

    # If @login_required is used without any argument nor parenthesis
    if func is None:
        def decorator(f):
            return decorated(f)
        return decorator

    # If @login_required() is used with parenthesis
    return decorated(func)


def check_user_is_superuser(user):
    return user is not None and user.is_superuser


def superuser_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged superusers"""
    def decorated(function):
        return user_pass_test(function, check_user_is_superuser)

    # If @superuser_required is used without any argument nor parenthesis
    if func is None:
        def decorator(f):
            return decorated(f)
        return decorator

    # If @superuser_required() is used with parenthesis
    return decorated(func)


def check_user_has_perm(user, perm):
    return user is not None and user.has_perm(perm)


def check_user_has_perms(user, perms):
    return user is not None and user.has_perms(perms)


def permissions_required(permissions):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""

    def decorated(function):
        if isinstance(permissions, six.string_types):
            # Check a single permission
            return user_pass_test(function, check_user_has_perm, [permissions])

        # Check many permissions
        return user_pass_test(function, check_user_has_perms, [permissions])

    return decorated


def check_user_in_group(user, group):
    group_name = group.name if isinstance(group, Group) else group
    return user.is_superuser or group_name in user.groups.values_list('name', flat=True)


def check_user_in_groups(user, groups):
    groups_names = [group.name if isinstance(group, Group) else group for group in groups]
    return user.is_superuser or all(group_name in user.groups.values_list('name', flat=True) for group_name in groups_names)


def in_groups(groups):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""

    def decorated(function):
        if isinstance(groups, six.string_types):
            # Check a single permission
            return user_pass_test(function, check_user_in_group, [groups])

        # Check many permissions
        return user_pass_test(function, check_user_in_groups, [groups])


    return decorated
