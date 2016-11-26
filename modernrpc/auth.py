# coding: utf-8


def user_pass_test(func=None, test_function=None, params=None):

    def decorated(function):

        function.modernrpc_auth_check_function = test_function
        function.modernrpc_auth_check_params = params
        return function

    # If @rpc_method is used without any argument nor parenthesis
    if func is None:
        def decorator(f):
            return decorated(f)
        return decorator

    # If @rpc_method() is used with parenthesis (with or without arguments)
    return decorated(func)


def check_user_is_logged(user):
    if user:
        return not user.is_anonymous()
    return False


def check_user_is_admin(user):
    if user:
        return user.is_admin()
    return False


def check_user_has_perm(user, perm):
    if user:
        return user.has_perm(perm)
    return False


def check_user_has_perms(user, perms):
    if user:
        return user.has_perms(perms)
    return False


def login_required(func=None):

    def decorated(function):
        return user_pass_test(function, check_user_is_logged)

    # If @rpc_method is used without any argument nor parenthesis
    if func is None:
        def decorator(f):
            return decorated(f)
        return decorator

    # If @rpc_method() is used with parenthesis (with or without arguments)
    return decorated(func)
