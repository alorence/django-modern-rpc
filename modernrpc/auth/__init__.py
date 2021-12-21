# coding: utf-8

from django.contrib.auth.models import Group


# Decorator
def set_authentication_predicate(predicate, params=()):
    """
    Assign a new authentication predicate to an RPC method.
    This is the most generic decorator used to implement authentication.
    Predicate is a standard function with the following signature:

    .. code:: python

       def my_predicate(request, *params):
           # Inspect request and extract required information

           if <condition>:
               # The condition to execute the method are met
               return True
           return False

    :param predicate:
    :param params:
    :return:
    """

    def wrapper(rpc_method):

        if hasattr(rpc_method, "modernrpc_auth_predicates"):
            rpc_method.modernrpc_auth_predicates.append(predicate)
            rpc_method.modernrpc_auth_predicates_params.append(params)

        else:
            rpc_method.modernrpc_auth_predicates = [predicate]
            rpc_method.modernrpc_auth_predicates_params = [params]

        return rpc_method

    return wrapper


def user_is_authenticated(user):
    return user.is_authenticated


def user_is_anonymous(user):
    return user.is_anonymous


def user_is_superuser(user):
    return user.is_superuser


def user_has_perm(user, perm):
    return user_is_superuser(user) or user.has_perm(perm)


def user_has_all_perms(user, perms):
    """Returns True if the given user have all given permissions"""
    return user_is_superuser(user) or user.has_perms(perms)


def user_has_any_perm(user, perms):
    return user_is_superuser(user) or any(user_has_perm(user, perm) for perm in perms)


def user_in_group(user, group):
    """Returns True if the given user is in given group"""
    if isinstance(group, Group):
        return user_is_superuser(user) or group in user.groups.all()
    if isinstance(group, str):
        return user_is_superuser(user) or user.groups.filter(name=group).exists()
    raise TypeError("'group' argument must be a string or a Group instance")


def user_in_any_group(user, groups):
    """Returns True if the given user is in at least 1 of the given groups"""
    return user_is_superuser(user) or any(
        user_in_group(user, group) for group in groups
    )


def user_in_all_groups(user, groups):
    """Returns True if the given user is in all given groups"""
    return user_is_superuser(user) or all(
        user_in_group(user, group) for group in groups
    )
