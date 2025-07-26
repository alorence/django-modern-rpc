Security concerns
=================

When implementing RPC services, security is a critical consideration. This section outlines important security concerns and best practices for using django-modern-rpc safely.

XML Security
-----------

Since django-modern-rpc uses builtin xmlrpc.client internally, it is vulnerable to various security issues related to
XML payloads parsing. To protect your project against these attacks, you can install the package `defusedxml` in your
environment.

Alternatively, you can install django-modern-rpc with an extra to setup all at once:

.. code-block:: bash

    pip install django-modern-rpc[defusedxml]

Once `defusedxml` can be imported, various methods are automatically patched against multiple attack vectors, including:

- XML External Entity (XXE) attacks
- Billion Laughs attack
- Quadratic Blowup attack
- External Entity Expansion

For more information, check the `defusedxml project's`_ README.

.. _defusedxml project's: https://github.com/tiran/defusedxml

Authentication
-------------

Always use authentication for RPC methods that modify data or access sensitive information. django-modern-rpc provides a flexible authentication system that can be integrated with Django's authentication system or custom authentication mechanisms.

See the :ref:`auth-ref` section for details on implementing authentication.

Key security recommendations:

- Use HTTPS for all RPC endpoints to prevent credentials and data from being intercepted
- Implement proper authentication for sensitive operations
- Consider using token-based authentication for machine-to-machine communication
- Implement rate limiting to prevent brute force attacks

Access Control
-------------

Beyond authentication, implement proper access control to ensure users can only access the RPC methods they are authorized to use:

.. code-block:: python

    def check_user_permissions(request):
        """Check if the user has the required permissions"""
        try:
            username, password = extract_http_basic_auth(request)
            user = authenticate(username=username, password=password)
            if user is None or not user.is_active:
                return False

            # Check if user has specific permissions
            return user.has_perm('app.can_use_rpc_api')
        except Exception:
            return False

    @rpc_method(auth=check_user_permissions)
    def sensitive_operation(data):
        # Perform operation
        return result

Input Validation
--------------

Always validate input data to prevent injection attacks and unexpected behavior:

.. code-block:: python

    @rpc_method
    def create_user(username, email, role):
        # Validate input
        if not isinstance(username, str) or len(username) < 3:
            raise RPCInvalidParams("Username must be a string with at least 3 characters")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise RPCInvalidParams("Invalid email format")

        if role not in ['user', 'admin', 'editor']:
            raise RPCInvalidParams("Invalid role")

        # Process validated input
        # ...

CSRF Protection
-------------

By default, Django's CSRF protection applies to all POST requests, including RPC requests. If you need to exempt your RPC views from CSRF protection (e.g., for machine-to-machine communication), you can use the `csrf_exempt` decorator:

.. code-block:: python

    from django.views.decorators.csrf import csrf_exempt
    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # CSRF protection disabled for this endpoint
        path('api/rpc/', csrf_exempt(RPCEntryPoint.as_view())),

        # CSRF protection enabled for this endpoint (default)
        path('api/protected-rpc/', RPCEntryPoint.as_view()),
    ]

However, disabling CSRF protection should be done with caution and only when necessary, such as for APIs that use token-based authentication.

Rate Limiting
-----------

To prevent abuse of your RPC endpoints, consider implementing rate limiting. You can use Django packages like `django-ratelimit` or implement custom rate limiting:

.. code-block:: python

    from django.core.cache import cache
    from modernrpc.exceptions import RPCInternalError

    def rate_limit_auth(request):
        """Rate limit RPC calls by IP address"""
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f'rpc_rate_limit_{ip}'

        # Get current count
        count = cache.get(cache_key, 0)

        # Check if limit exceeded
        if count >= 100:  # 100 requests per minute
            return False

        # Increment count
        cache.set(cache_key, count + 1, 60)  # 60 seconds expiry
        return True

    @rpc_method(auth=rate_limit_auth)
    def rate_limited_method(x, y):
        return x + y

Logging and Monitoring
--------------------

Implement proper logging and monitoring to detect and respond to security incidents:

- Log authentication failures
- Monitor for unusual patterns of RPC calls
- Set up alerts for potential security issues

You can configure django-modern-rpc to log exceptions by setting `MODERNRPC_LOG_EXCEPTIONS = True` in your settings.py (this is the default).

Security Checklist
----------------

- [ ] Use HTTPS for all RPC endpoints
- [ ] Install and use defusedxml for XML-RPC
- [ ] Implement proper authentication for sensitive operations
- [ ] Validate all input data
- [ ] Consider CSRF protection requirements
- [ ] Implement rate limiting
- [ ] Set up logging and monitoring
- [ ] Regularly update django-modern-rpc and its dependencies
- [ ] Follow Django's security best practices
