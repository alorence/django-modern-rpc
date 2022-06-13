Authentication
==============

django-modern-rpc provides a mechanism to check authentication before executing a given RPC method. It implemented at
request level and is always checked before executing procedure.

.. versionchanged:: 1.0.0
   In previous releases, authentication failures caused the view to return a 403 status code on response to standard
   (single) request, while batch requests / multicall always returned a 200 status with an error message. For
   consistency with XML-RPC specs, an authentication failure now returns a 200 response with a proper
   error (```error: -32603, message: Authentication failed when calling "<method_name>"```).

HTTP Basic Auth
---------------

django-modern-rpc comes with a builtin support for `HTTP Basic Authentication`_. It provides a set of decorators
to directly extract user information from request and test this user against Django authentication system.

.. _`HTTP Basic Authentication`: https://en.wikipedia.org/wiki/Basic_access_authentication

.. code:: python

    from modernrpc.auth.basic import (
        http_basic_auth_login_required,
        http_basic_auth_superuser_required,
        http_basic_auth_permissions_required,
        http_basic_auth_any_of_permissions_required,
        http_basic_auth_group_member_required,
        http_basic_auth_all_groups_member_required
    )
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


Custom authentication system
----------------------------

To provide authentication features, django-modern-rpc introduce concept of "predicate". This example will show you how
to build a custom authentication system to restrict RPC method execution to clients that present a User-Agent different
from a known list of bots.

.. code:: python

    def forbid_bots_access(request):
        """Return True when request has a User-Agent different from provided list"""
        if "User-Agent" not in request.headers:
            # No User-Agent provided, the request must be rejected
            return False

        forbidden_bots = [
            'Googlebot',  # Google
            'Bingbot',  # Microsoft
            'Slurp',  # Yahoo
            'DuckDuckBot',  # DuckDuckGo
            'Baiduspider',  # Baidu
            'YandexBot',  # Yandex
            'facebot',  # Facebook
        ]

        req_user_agent = request.headers["User-Agent"].lower()
        for bot_user_agent in [ua.lower() for ua in forbidden_bots]:
            # If we detect the caller is one of the bots listed above...
            if bot_user_agent in req_user_agent:
                # ... forbid access
                return False

        # In all other cases, allow access
        return True

.. note::
    A predicate always takes a request as argument and returns a boolean value

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

In addition, you can provide arguments to your predicate using ``params``:

.. code:: python

    @rpc_method
    @set_authentication_predicate(my_predicate_with_params, params=('param_1', 42))
    def my_rpc_method(a, b):
        return a + b

It is possible to declare multiple predicates for a single method. In such case, all predicates must return
True to allow access to the method.

.. code:: python

    @rpc_method
    @set_authentication_predicate(forbid_bots_access)
    @set_authentication_predicate(my_predicate_with_params, params=('param_1', 42))
    def my_rpc_method(a, b):
        return a + b
