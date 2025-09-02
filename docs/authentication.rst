.. _auth-ref:

Authentication
==============

.. versionchanged:: 2.0 Authentication system has been completely rewritten in release 2.0.
   Please carefully read this documentation to understand how the new system works

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

.. versionchanged:: 2.0 In the previous versions, all predicates had to validate incoming request to allows a procedure
   to be called

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

Auth can be a single callable or any iterable (list/tuple) of callables. They are called in the order you provide.
The first truthy result short‑circuits evaluation and authorizes the request; if none return a truthy value, an
AuthenticationError is raised.

.. code-block:: python

   from django.http.request import HttpRequest

   def via_session(request: HttpRequest):
       return request.user if request.user.is_authenticated else None

   def via_token(request: HttpRequest):
       token = request.headers.get("Authorization", "").removeprefix("Bearer ")
       return {"token": token} if token == "valid" else None

   server = RpcServer(auth=[via_session, via_token])

In the example above, via_session is tried first, then via_token if needed.

Accessing the authentication result in procedures
-------------------------------------------------

When a predicate returns a truthy value, that value is stored in the RpcRequestContext.auth_result. To access it from
within a procedure, ask the server to inject the context into a named parameter using context_target at registration
time, then read context.auth_result.

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
       return {"message": message, "who": api_key}

Notes and best practices
------------------------

- Predicates should be side‑effect free and fast; they are called on every request of protected procedures.
- Return a meaningful truthy object (e.g., the authenticated user, a claims dict, or a token string) to make it
  usable in your procedures via ctx.auth_result.
- Precedence: procedure auth > namespace auth > server auth.

Utilities
---------

Since authentication system has been rewritten from scratch in v2, the decorators previously available to retrieve
Basic Auth information from request and control the permissions of the corresponding user have been removed.

A new module `modernrpc.auth` contains some utility functions to help you reading authentication from
request (Basic Auth, Bearer token, etc.).


.. automodule:: modernrpc.auth
   :members:
   :exclude-members: extract_bearer_token

.. py:function:: modernrpc.auth.extract_bearer_token(request: HttpRequest) -> str

   Extract a Bearer token from a request object. Return the token.

   :param request: HTTP request containing the headers
   :type request: HttpRequest
   :return: Token string
   :rtype: str
