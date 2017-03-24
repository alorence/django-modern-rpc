==============
Authentication
==============

Starting from version 0.5, django-modern-rpc supports authentication. It is possible to restrict access to any
RPC method depending on conditions names "predicate".

Basics
======

To provide authentication features, django-modern-rpc introduces the concept of "predicate". It is a python function
taking a request as argument and returning a boolean:

.. code:: python

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

It is associated with RPC method using ``@set_authentication_predicate`` decorator.

.. code:: python

    from modernrpc.core import rpc_method
    from modernrpc.auth import set_authentication_predicate
    from myproject.myapp.auth import forbid_bots_access

    @rpc_method
    @set_authentication_predicate(forbid_bots_access)
    def my_rpc_method(a, b):
        return a + b

Now, the RPC method becomes unavailable to callers if User-Agent is not provided or if it has an invalid value.

If your predicate takes additional arguments, simply add them as arguments of the decorator:

.. code:: python

    @rpc_method
    @set_authentication_predicate(my_predicate_with_params, 'param_1', 42)
    def my_rpc_method(a, b):
        return a + b

It is possible to declare multiple predicates for a single method. In such case, all predicates must return
True to allow access to the method.

.. code:: python

    @rpc_method
    @set_authentication_predicate(forbid_bots_access)
    @set_authentication_predicate(my_predicate_with_params, 'param_1', 42)
    def my_rpc_method(a, b):
        return a + b

HTTP Basic Authentication support
=================================

django-modern-rpc comes with a builtin support for `HTTP Basic Auth`_. It provides a set of decorators to directly
extract user information from request, and test this user against Django authentication system:

.. _`HTTP Basic Auth`: https://www.wikiwand.com/en/Basic_access_authentication

.. code:: python

    from modernrpc.auth.basic import http_basic_auth_login_required, http_basic_auth_superuser_required, \
         http_basic_auth_permissions_required, http_basic_auth_any_of_permissions_required, \
         http_basic_auth_group_member_required, http_basic_auth_all_groups_member_required
    from modernrpc.core import rpc_method


    @rpc_method
    @http_basic_auth_login_required
    def logged_user_required(x):
        """Access allowed only to logged users"""
        return x

    @rpc_method
    @http_basic_auth_superuser_required
    def logged_superuser_required(x):
        """Access allowed only to superusers"""
        return x

    @rpc_method
    @http_basic_auth_permissions_required(permissions='auth.delete_user')
    def delete_user_perm_required(x):
        """Access allowed only to users with specified permission"""
        return x

    @rpc_method
    @http_basic_auth_any_of_permissions_required(permissions=['auth.add_user', 'auth.change_user'])
    def any_permission_required(x):
        """Access allowed only to users with at least 1 of the specified permissions"""
        return x

    @rpc_method
    @http_basic_auth_permissions_required(permissions=['auth.add_user', 'auth.change_user'])
    def all_permissions_required(x):
        """Access allowed only to users with all the specified permissions"""
        return x

    @rpc_method
    @http_basic_auth_group_member_required(groups='A')
    def in_group_A_required(x):
        """Access allowed only to users contained in specified group"""
        return x

    @rpc_method
    @http_basic_auth_group_member_required(groups=['A', 'B'])
    def in_group_A_or_B_required(x):
        """Access allowed only to users contained in at least 1 of the specified group"""
        return x

    @rpc_method
    @http_basic_auth_all_groups_member_required(groups=['A', 'B'])
    def in_groups_A_and_B_required_alt(x):
        """Access allowed only to users contained in all the specified group"""
        return x
