.. _auth-ref:

Authentication
==============

django-modern-rpc provides a mechanism to check authentication before executing a given RPC method. Authentication is implemented at the request level and is always checked before executing a procedure.

Authentication Basics
--------------------

In django-modern-rpc v2, authentication is handled through callback functions that take a request object and return a boolean or other truthy value. If the callback returns a truthy value, authentication is considered successful. If it returns a falsy value or raises an exception, authentication fails.

Authentication callbacks are passed to the ``rpc_method`` decorator using the ``auth`` parameter:

.. code-block:: python

    from modernrpc.core import rpc_method

    def my_auth_callback(request):
        """Return True if authentication succeeds, False otherwise"""
        # Check authentication logic here
        return True

    @rpc_method(auth=my_auth_callback)
    def my_authenticated_method(x, y):
        """This method requires authentication"""
        return x + y

You can also pass multiple authentication callbacks as a list. In this case, all callbacks must return a truthy value for authentication to succeed:

.. code-block:: python

    @rpc_method(auth=[callback1, callback2, callback3])
    def method_with_multiple_auth_checks(x, y):
        """This method requires all authentication callbacks to succeed"""
        return x + y

HTTP Basic Authentication
------------------------

django-modern-rpc provides utility functions to extract HTTP Basic Authentication credentials from a request:

.. code-block:: python

    from modernrpc.auth import extract_http_basic_auth
    from django.contrib.auth import authenticate

    def http_basic_auth_login_required(request):
        """Return True when request contains valid HTTP Basic Auth credentials"""
        try:
            username, password = extract_http_basic_auth(request)
            user = authenticate(username=username, password=password)
            return user is not None and user.is_active
        except Exception:
            return False

    @rpc_method(auth=http_basic_auth_login_required)
    def logged_user_required(x):
        """Access allowed only to logged users"""
        return x

You can create more specific authentication callbacks based on user properties:

.. code-block:: python

    def http_basic_auth_superuser_required(request):
        """Return True when request contains valid HTTP Basic Auth credentials for a superuser"""
        try:
            username, password = extract_http_basic_auth(request)
            user = authenticate(username=username, password=password)
            return user is not None and user.is_active and user.is_superuser
        except Exception:
            return False

    @rpc_method(auth=http_basic_auth_superuser_required)
    def logged_superuser_required(x):
        """Access allowed only to superusers"""
        return x

Bearer Token Authentication
--------------------------

django-modern-rpc also provides utility functions to extract Bearer tokens from a request:

.. code-block:: python

    from modernrpc.auth import extract_bearer_token

    def validate_token(request):
        """Return True when request contains a valid Bearer token"""
        try:
            token = extract_bearer_token(request)
            # Validate the token (e.g., using Django REST framework's TokenAuthentication)
            # Return True if valid, False otherwise
            return is_valid_token(token)
        except Exception:
            return False

    @rpc_method(auth=validate_token)
    def token_protected_method(x):
        """Access allowed only with a valid token"""
        return x

Custom Authentication Systems
---------------------------

You can create custom authentication systems by implementing callback functions that take a request object and return a boolean or other truthy value. Here's an example that restricts access based on the User-Agent header:

.. code-block:: python

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

    @rpc_method(auth=forbid_bots_access)
    def no_bots_allowed(a, b):
        return a + b

Accessing Authentication Results
------------------------------

If you need to access the result of the authentication check in your RPC method, you can use the ``context_target`` parameter:

.. code-block:: python

    @rpc_method(auth=my_auth_callback, context_target="ctx")
    def method_with_context(x, y, ctx=None):
        """This method has access to the request context"""
        # ctx.auth_result contains the result of the authentication check
        # ctx.request contains the HTTP request
        # ctx.server contains the RPC server
        # ctx.handler contains the RPC handler
        # ctx.protocol contains the protocol (XML-RPC or JSON-RPC)
        return x + y

Error Handling
-------------

When authentication fails, an ``AuthenticationError`` is raised with the message "Authentication failed when calling "<method_name>"". This error is converted to an appropriate RPC error response depending on the protocol.

For JSON-RPC, the error code is -32603 (Internal error) with the message "Authentication failed when calling "<method_name>"".

For XML-RPC, the error code is 1 with the same message.
