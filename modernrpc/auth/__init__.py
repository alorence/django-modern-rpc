# coding: utf-8
from django.contrib.auth.models import Group
from django.utils import six


# Decorator
def set_authentication_predicate(func, predicate, params=None):
    """
    Assign a new authentication predicate to a RPC method.
    This is the most generic decorator used to implement authentication.
    Predicate is a standard function with the following signature:

    .. code:: python

       def my_predicate(request, *params):
           # Do the work of authenticating client, using info from request object
           result = True
           return result

    :param func:
    :param predicate:
    :param params:
    :return:
    """
    def decorated(rpc_method):

        if hasattr(rpc_method, 'modernrpc_auth_predicates'):
            rpc_method.modernrpc_auth_predicates.append(predicate)
            rpc_method.modernrpc_auth_predicates_params.append(params)

        else:
            rpc_method.modernrpc_auth_predicates = [predicate]
            rpc_method.modernrpc_auth_predicates_params = [params]

        return rpc_method

    return decorated(func)


def user_is_logged(user):
    return user is not None and not user.is_anonymous()


def user_is_superuser(user):
    return user is not None and user.is_superuser


def user_has_perm(user, perm):
    return user_is_superuser(user) or user.has_perm(perm)


def user_has_perms(user, perms):
    return user_is_superuser(user) or user.has_perms(perms)


def user_in_group(user, group):
    if isinstance(group, Group):
        return user_is_superuser(user) or group in user.groups
    elif isinstance(group, six.string_types):
        return user_is_superuser(user) or group in user.groups.values_list('name', flat=True)
    raise TypeError("group argument must be a string or a Group instance")


def user_in_groups(user, groups):
    return user_is_superuser(user) or all(user_in_group(user, group) for group in groups)
