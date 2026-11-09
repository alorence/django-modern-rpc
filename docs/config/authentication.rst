.. _auth-ref:

Authentication
==============

.. versionchanged:: 2.0 Authentication system has been completely rewritten. Please carefully read this
   page to understand how the new system works

Overview
--------

Django‑modern‑rpc lets you protect procedures using small authentication predicates. A predicate is a callable that
receives the Django HttpRequest and returns a truthy value when the caller is authorized, or a falsy value otherwise.

Key points:

- You can configure authentication at three levels: server, namespace, and procedure.
- Predicates are evaluated in their definition order with OR semantics: the first predicate that returns a truthy value
  authorizes the call; if all return falsy, the call fails with AuthenticationError.
- The truthy value returned by the successful predicate is stored into RpcRequestContext.auth_result so it’s available
  to your procedure (see Accessing the authentication result below).

.. versionchanged:: 2.0 In the previous versions, all predicates had to validate the incoming request to allow a
   procedure to be called

Configuration levels
--------------------

1) Server level (default for all procedures)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pass auth=<predicate or sequence of predicates> to RpcServer to define a default for all procedures registered on this
server, unless overridden by a namespace or a procedure.

Example:

.. code-block:: python

   from django.http.request import HttpRequest
   from modernrpc import RpcServer

   def is_staff(request: HttpRequest):
       # Example using Django auth
       return request.user if (request.user.is_authenticated and request.user.is_staff) else None

   server = RpcServer(auth=is_staff)

.. warning::
   This example relies on Django session authentication (``request.user``). RPC views are exempted from CSRF
   protection, read :ref:`CSRF and session authentication` before using session-based predicates.

2) Namespace level (default within a namespace)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

RpcNamespace accepts the same auth parameter. Procedures registered on the namespace inherit that default unless they
override it.

.. code-block:: python

   from django.http.request import HttpRequest
   from modernrpc import RpcNamespace

   def has_api_key(request: HttpRequest):
       return request.headers.get("X-API-Key") == "secret" or None

   api = RpcNamespace(auth=has_api_key)

   @api.register_procedure
   def ping():
       return "pong"

   server.register_namespace(api, "api")

3) Procedure level (highest precedence)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can override auth at registration time for a given function. This takes precedence over namespace and server.

.. code-block:: python

   from django.http.request import HttpRequest

   def is_superuser(request: HttpRequest):
       return request.user if (request.user.is_authenticated and request.user.is_superuser) else None

   @server.register_procedure(name="admin.reset", auth=is_superuser)
   def reset_counters():
       ...

Multiple predicates and evaluation order
----------------------------------------

Auth can be a single callable or any iterable (list/tuple) of callables. They are called in the order they are provided.
The first truthy result short‑circuits evaluation and authorizes the request; if none return a truthy value, an
``AuthenticationError`` is raised.

.. code-block:: python

   from django.http.request import HttpRequest

   def via_token(request: HttpRequest):
       token = request.headers.get("Authorization", "").removeprefix("Bearer ")
       return {"token": token} if token == "valid" else None

   def via_session(request: HttpRequest):
       return request.user if request.user.is_authenticated else None

   server = RpcServer(auth=[via_session, via_token])

In the example above, ``via_session`` is tried first, then ``via_token`` if needed.

.. warning::
   This example relies on Django session authentication (``request.user``). RPC views are exempted from CSRF
   protection, read :ref:`CSRF and session authentication` before using session-based predicates.

Accessing the authentication result in procedures
-------------------------------------------------

When a predicate returns a truthy value, that value is stored in ``RpcRequestContext.auth_result``. To access it from
within a procedure, ask the server to inject the context into a named parameter using ``context_target`` at
registration, then read ``context.auth_result``.

.. code-block:: python

   from django.http.request import HttpRequest
   from modernrpc import RpcServer, RpcRequestContext

   server = RpcServer()

   def has_api_key(request: HttpRequest):
       return request.headers.get("X-API-Key") or None

   @server.register_procedure(name="echo.secure", context_target="ctx", auth=has_api_key)
   def echo_secure(message: str, ctx: RpcRequestContext):
       # ctx is a modernrpc.core.RpcRequestContext
       api_key = ctx.auth_result  # value returned by has_api_key
       return {"message": message, "clear-text-api-key": api_key}

Notes and best practices
------------------------

- Predicates should be side‑effect free and fast; they are called on every request of protected procedures.
- Return a meaningful truthy object (e.g., the authenticated user, a claims dict, or a token string) to make it
  usable in your procedures via ``ctx.auth_result``.
- Precedence: procedure auth > namespace auth > server auth.
- Prefer header-based authentication (Basic, Bearer token, API key) over Django session. See
  :ref:`CSRF and session authentication`.

Security considerations
-----------------------

CSRF and session authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

RPC views (``server.view`` and ``server.async_view``) are always exempted from Django's CSRF protection. This is
required for an RPC API: most clients (``xmlrpc.client``, scripts, other servers, mobile apps) are not browsers and
cannot provide a CSRF token.

When authentication is based on HTTP headers (Basic auth, Bearer token, API key...), this is not a problem: a malicious
web page cannot make the victim's browser add these headers automatically.

When a predicate relies on the Django session (``request.user``), the session cookie **is** sent automatically by the
browser, including with requests initiated by another website. In this case, the only remaining protections are:

- **Content-Type check**: django-modern-rpc only accepts requests with an ``application/json`` (or variant),
  ``text/xml`` or ``application/xml`` content type. A cross-site HTML form cannot send such a request.
- **CORS preflight**: these content types are not "CORS-safelisted", so a cross-origin ``fetch()`` or
  ``XMLHttpRequest`` triggers a preflight request first. By default, Django does not answer it with the required
  ``Access-Control-Allow-*`` headers, and the browser does not send the actual request.

These protections are effective by default, but they rely entirely on your CORS configuration. They are bypassed if:

- your project allows credentialed cross-origin requests to the RPC endpoint from untrusted or overly broad origins,
  for example with `django-cors-headers`_ configured with ``CORS_ALLOW_CREDENTIALS = True`` and
  ``CORS_ALLOW_ALL_ORIGINS = True`` or wide regex patterns;
- an allowed origin (for example another subdomain) is compromised or hosts untrusted content.

In such a situation, a malicious page can call your procedures with the identity of a logged-in user.

.. _django-cors-headers: https://github.com/adamchainz/django-cors-headers

Recommendations:

- **Prefer header-based authentication** for RPC endpoints. The helpers in ``modernrpc.auth`` (see :ref:`Utilities`
  below) help extract credentials from the request:

  .. code-block:: python

     from django.contrib.auth import authenticate
     from django.http import HttpRequest
     from modernrpc import RpcServer
     from modernrpc.auth import extract_http_basic_auth

     def basic_auth_user(request: HttpRequest):
         try:
             username, password = extract_http_basic_auth(request)
         except ValueError:
             return None
         return authenticate(request, username=username, password=password)

     server = RpcServer(auth=basic_auth_user)

- If you use session-based predicates (typically for a JavaScript client served from the same site), make sure the
  RPC endpoint is not reachable through credentialed cross-origin requests: do not enable CORS with credentials on
  this URL, or restrict ``CORS_ALLOWED_ORIGINS`` to origins you fully trust.
- Keep Django's session cookie defaults (``SESSION_COOKIE_SAMESITE = "Lax"``) or make them stricter. ``SameSite``
  prevents the cookie from being sent with requests from other sites, but not from other subdomains of the same site.

Utilities
---------

Since the authentication system has been rewritten from scratch in v2, the decorators previously available to retrieve
Basic Auth information from the request and control the permissions of the corresponding user have been removed.

A new module, ``modernrpc.auth``, contains some utility functions to help you read authentication data from
the request (Basic Auth, Bearer token, etc.).


.. automodule:: modernrpc.auth
   :members:
   :exclude-members: extract_bearer_token

.. py:function:: modernrpc.auth.extract_bearer_token(request: HttpRequest) -> str

   Extract a Bearer token from a request object. Return the token.

   :param request: HTTP request containing the headers
   :type request: HttpRequest
   :return: Token string
   :rtype: str
