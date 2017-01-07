# coding: utf-8
from django.contrib.auth.models import Group


def user_pass_test(func, test_function, params=None):
    """
    TBD
    """

    def decorated(rpc_method):

        if hasattr(rpc_method, 'modernrpc_auth_check_functions'):
            rpc_method.modernrpc_auth_check_functions.append(test_function)
            rpc_method.modernrpc_auth_check_params.append(params)

        else:
            rpc_method.modernrpc_auth_check_functions = [test_function]
            rpc_method.modernrpc_auth_check_params = [params]

        return rpc_method

    return decorated(func)


def check_user_is_logged(user):
    return user is not None and not user.is_anonymous()


def check_user_is_superuser(user):
    return user is not None and user.is_superuser


def check_user_has_perm(user, perm):

    if user is None:
        return False
    elif user.is_superuser:
        return True

    return user is not None and (user.is_superuser or user.has_perm(perm))


def check_user_has_perms(user, perms):

    if user is None:
        return False
    elif user.is_superuser:
        return True

    return user is not None and (user.is_superuser or user.has_perms(perms))


def check_user_in_group(user, group):

    if user is None:
        return False
    elif user.is_superuser:
        return True

    group_name = group.name if isinstance(group, Group) else group
    return group_name in user.groups.values_list('name', flat=True)


def check_user_in_groups(user, groups):

    if user is None:
        return False
    elif user.is_superuser:
        return True

    groups_names = [group.name if isinstance(group, Group) else group for group in groups]
    return all(group_name in user.groups.values_list('name', flat=True) for group_name in groups_names)
