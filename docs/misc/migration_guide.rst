Migration guide
===============

From 2.1 to 2.2
---------------

Version 2.2 hardens the default behavior of the library against information leaks and denial of service. Most
projects can upgrade without any change, but a few default behaviors have changed. This section lists them, with the
way to adapt your project or restore the previous behavior. See the :doc:`changelog` for the complete list of changes.

Error messages of unexpected exceptions are hidden
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Exceptions raised by your procedures that don't inherit from ``RPCException`` (``ValueError``, ``KeyError``, database
errors...) and serialization errors are now returned to clients with a generic message. The details are logged
using the ``modernrpc.server`` logger, with ``ERROR`` level and traceback.

.. code-block:: text

   v2.1: {"code": -32603, "message": "Internal error: division by zero"}
   v2.2: {"code": -32603, "message": "Internal error"}

If your clients rely on these messages:

- **Recommended**: raise an ``RPCException`` subclass from your procedure for errors that are part of your API
  (see :ref:`Custom exceptions`), or convert specific exceptions from an error handler (see
  :ref:`Customize error handling`). Their message is always returned to the client.
- Restore the previous behavior globally with ``MODERNRPC_EXPOSE_INTERNAL_ERRORS = True``, or for a single server with
  ``RpcServer(expose_internal_errors=True)``. Avoid it in production, see :ref:`Internal errors`.

If your ``error_handler`` already logs every exception, you may want to silence the new log entries by adjusting the
level of the ``modernrpc.server`` logger in your ``LOGGING`` configuration.

Invalid parameters errors
^^^^^^^^^^^^^^^^^^^^^^^^^

Arguments are now checked against the procedure signature before the call. This has 2 consequences:

- The message of Invalid Params errors (``-32602``) changed. For example, ``Invalid parameters: add() takes 2
  positional arguments but 3 were given`` is now ``Invalid parameters: too many positional arguments``. Update your
  clients or tests if they check this message.
- A ``TypeError`` raised from inside a procedure was previously returned as an Invalid Params error. It is now handled
  as any other unexpected exception: Internal Error (``-32603``), with a generic message by default.

Number of calls per request is limited
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

JSON-RPC batch requests and XML-RPC ``system.multicall`` now accept at most 100 calls by default. A request exceeding
the limit is rejected with an Invalid Request error (``-32600``), and none of its calls is executed.

If your clients legitimately send larger batches, raise the limit globally with ``MODERNRPC_MAX_BATCH_SIZE``, or for
a single server:

.. code-block:: python

   server = RpcServer(max_batch_size=500)  # or None to disable the limit (not recommended)

In addition, a ``system.multicall`` can't contain a call to ``system.multicall`` anymore. Such a call gets an Invalid
Request fault (``-32600``) in the results list, the other calls are executed normally.

JSON-RPC batch requests with invalid items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As required by the JSON-RPC 2.0 specification, invalid items of a batch request (not an object, missing ``method``...)
now get their own Invalid Request error (``-32600``) with a ``null`` id in the response list, while valid items are
executed. Previously, the whole batch was rejected with a single error object. An empty batch (``[]``) now returns an
Invalid Request error instead of an empty response.

No change is needed unless you wrote a custom JSON-RPC unmarshaller or deserializer, or overrode
``JsonRpcHandler.process_batch_request()`` / ``aprocess_batch_request()``. In this case, note that the items of a
batch are now typed ``JsonRpcBatchItem``: either a ``JsonRpcRequest``, or the ``RPCInvalidRequest`` exception
describing an invalid item.

HTTP Basic Auth credentials are not percent-decoded anymore
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``modernrpc.auth.extract_http_basic_auth()`` now returns username and password exactly as sent by the client, as
specified by RFC 7617. Previously, ``urllib.parse.unquote()`` was applied, so a password like ``p%40ss`` was returned
as ``p@ss``.

Usual clients (Python's ``xmlrpc.client``, ``requests``...) already decode credentials embedded in the URL before
sending them, so most projects are not affected. If your clients send percent-encoded credentials on purpose, apply
``unquote()`` in your authentication predicate:

.. code-block:: python

   from urllib.parse import unquote
   from modernrpc.auth import extract_http_basic_auth

   def my_predicate(request):
       username, password = map(unquote, extract_http_basic_auth(request))
       ...

Other changes
^^^^^^^^^^^^^

- ``typing-extensions`` is now a required dependency on all Python versions.
- ``modernrpc.constants.NOT_SET`` is now a ``typing_extensions.Sentinel`` instance, and the internal enum
  ``modernrpc.constants.Default`` has been removed. Compare with ``is NOT_SET`` if you used it in your code.
- If your authentication predicates rely on the Django session (``request.user``), read
  :ref:`CSRF and session authentication`.

From 1.1 to 2.0
---------------

This section will guide you to update an existing setup of django-modern-rpc 1.0 or 1.1 to the latest v2 release.

Update settings
^^^^^^^^^^^^^^^

MODERNRPC_METHODS_MODULES
*************************

In v2, the new Server / Namespace system will automatically import your decorated procedures. This setting is now
useless, you can simply delete it from your settings.

MODERNRPC_LOG_EXCEPTIONS
************************

This setting has been removed. In v2, exception logging can be handled through the ``error_handler`` callback
on ``RpcServer``. See :ref:`Customize error handling` for details. You can simply delete this setting from your
configuration.

MODERNRPC_DOC_FORMAT
********************

This setting still exists in v2. Accepted values are ``""`` (empty string, default), ``"rst"`` or ``"md"``
(also accepts ``"markdown"``). No migration action is needed, but note that automatic HTML documentation through
entry points has been removed. Docstrings are still processed for introspection (``system.methodHelp``).

MODERNRPC_DEFAULT_ENTRYPOINT_NAME
*********************************

The ``RPCEntryPoint`` class is not used anymore. You can define multiple ``RpcServer`` instances to split your APIs.
No specific name is required, and no default one is needed anymore. This setting is now useless, you can simply delete
it from your settings.

MODERNRPC_JSON_DECODER / MODERNRPC_JSON_ENCODER
***********************************************

Backends are now configured individually. Configuring the encoder and decoder with default builtin ``json`` backend
is still possible using new settings.

Before
......

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DECODER = "path.to.valid.json.Decoder"
    MODERNRPC_JSON_ENCODER = "path.to.valid.json.Encoder"

After
.....

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DESERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.json.PythonJsonDeserializer",
        "kwargs": {
            "load_kwargs": {"cls": path.to.valid.json.Decoder},
        }
    }
    MODERNRPC_JSON_SERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.json.PythonJsonSerializer",
        "kwargs": {
            "dump_kwargs": {"cls": path.to.valid.json.Encoder},
        }
    }

MODERNRPC_XMLRPC_USE_BUILTIN_TYPES / MODERNRPC_XMLRPC_ALLOW_NONE
****************************************************************

Backends are now configured individually. Configuring the behavior of builtin ``xmlrpc`` backend is still possible
using new settings.

Before
......

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = False
    MODERNRPC_XMLRPC_ALLOW_NONE = False

After
.....

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_DESERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer",
        "kwargs": {
            "load_kwargs": {"use_builtin_types": False}
        }
    }
    MODERNRPC_XML_SERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
        "kwargs": {
            "dump_kwargs": {"allow_none": False}
        }
    }


MODERNRPC_XMLRPC_DEFAULT_ENCODING
*********************************

In the previous versions, this setting was used to initialize an ``xmlrpc.client.Marshaller``. In v2, this class is
not directly instantiated but used through the serialization process. Encoding can still be configured.


Before
......

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XMLRPC_DEFAULT_ENCODING = "ascii"

After
.....

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_SERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
        "kwargs": {
            "dump_kwargs": {"encoding": "ascii"}
        }
    }


Replace a single RPCEntryPoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before
******

Procedure registration was possible from anywhere in the code, as soon as the module
was declared in `settings.MODERNRPC_METHODS_MODULES`.

.. code-block:: python
   :caption: myapp/remote_procedures.py

   from modernrpc.core import rpc_method

   @rpc_method
   def add(a, b):
       return a + b


.. code-block:: python
   :caption: myproject/urls.py

   from django.urls import path
   from modernrpc.views import RPCEntryPoint

   urlpatterns = [
       # ... other url patterns
       path('rpc/', RPCEntryPoint.as_view()),
   ]

After
*****

With v2, an ``RpcServer`` instance must be created, and then used to register procedures.

.. code-block:: python
   :caption: myproject/myapp/rpc.py

   from modernrpc.server import RpcServer

   server = RpcServer()


   @server.register_procedure
   def add(a: int, b: int) -> int:
       """Add two numbers and return the result.

       :param a: First number
       :param b: Second number
       :return: Sum of a and b
       """
       return a + b

.. code-block:: python
   :caption: myproject/urls.py

   from django.urls import path
   from myapp.rpc import server

   urlpatterns = [
       # ... other url patterns
       path('rpc/', server.view),
   ]

Replace multiple RPCEntryPoints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before
******

In v1.x, multiple endpoints were declared by instantiating ``RPCEntryPoint`` several times, each one bound to a named
entry point. Procedures were then attached to a specific entry point using the ``entry_point`` argument of the
``@rpc_method`` decorator. A procedure with no explicit entry point was served by every endpoint.

.. code-block:: python
   :caption: myapp/remote_procedures.py

   from modernrpc.core import rpc_method

   @rpc_method(entry_point="apiV1")
   def add(a, b):
       return a + b

   @rpc_method(entry_point="apiV2")
   def add(a, b):
       return a + b

   @rpc_method
   def ping():
       # No entry_point: available on every endpoint
       return "pong"


.. code-block:: python
   :caption: myproject/urls.py

   from django.urls import path
   from modernrpc.views import RPCEntryPoint

   urlpatterns = [
       # ... other url patterns
       path('rpc/v1/', RPCEntryPoint.as_view(entry_point="apiV1")),
       path('rpc/v2/', RPCEntryPoint.as_view(entry_point="apiV2")),
   ]

After
*****

With v2, the ``entry_point`` concept disappears. Each endpoint becomes a distinct ``RpcServer`` instance, and you
register each procedure directly on the server(s) that must expose it. To make a procedure available on several
servers (the v1.x behavior of a procedure without an ``entry_point``), simply stack the registration decorators.

.. code-block:: python
   :caption: myproject/myapp/rpc.py

   from modernrpc.server import RpcServer

   api_v1 = RpcServer()
   api_v2 = RpcServer()


   @api_v1.register_procedure
   def add(a: int, b: int) -> int:
       """Add two numbers and return the result."""
       return a + b


   @api_v2.register_procedure
   def add(a: int, b: int) -> int:
       """Add two numbers and return the result (v2)."""
       return a + b


   @api_v1.register_procedure
   @api_v2.register_procedure
   def ping() -> str:
       # Registered on both servers
       return "pong"

.. code-block:: python
   :caption: myproject/urls.py

   from django.urls import path
   from myapp.rpc import api_v1, api_v2

   urlpatterns = [
       # ... other url patterns
       path('rpc/v1/', api_v1.view),
       path('rpc/v2/', api_v2.view),
   ]

This new process allows you to easily customize registration per procedure and per server.

Update your authentication configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before
******

.. code-block:: python
   :caption: myproject/myapp/auth.py

   # Custom predicate used to block some procedures to known bots
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

       if request.headers["User-Agent"].lower() in [ua.lower() for ua in forbidden_bots]:
           # ... forbid access
           return False

       # In all other cases, allow access
       return True


.. code-block:: python

   from modernrpc.core import rpc_method
   from modernrpc.auth import set_authentication_predicate
   from modernrpc.auth.basic import http_basic_auth_permissions_required
   from myproject.myapp.auth import forbid_bots_access


   @rpc_method
   @http_basic_auth_permissions_required(permissions='auth.view_user')
   def my_rpc_method_with_builtin_predicate(username):
       user = User.objects.get(username=username)
       return f"{user.first_name} {user.last_name}"

   @rpc_method
   @set_authentication_predicate(forbid_bots_access)
   def my_rpc_method_with_custom_authentication(a, b):
       return a + b


After
*****


.. code-block:: python
   :caption: myproject/myapp/auth.py

   from django.contrib.auth import authenticate
   from django.http.request import HttpRequest

   from modernrpc.auth import extract_http_basic_auth

   # Predicate used to block some procedures to known bots
   def forbid_bots_access(request: HttpRequest):
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

       if request.headers["User-Agent"].lower() in [ua.lower() for ua in forbidden_bots]:
           # ... forbid access
           return False

       # In all other cases, allow access
       return True


   # Predicate to check for specific Django permissions
   def check_view_permissions(perms: str):
       def inner(request: HttpRequest):
           # Use modernrpc helper to extract Basic Auth username & password
           username, password = extract_http_basic_auth(request)
           # Use Django auth system to authenticate the user
           user = authenticate(username=username, password=password)
           # Check for authentication (valid username & password) AND for permissions
           if not user or not user.has_perm(perms):
               return False
           # User is authenticated AND authorized
           return user

       return inner


.. code-block:: python

   from myproject.myapp.auth import check_view_permissions, forbid_bots_access


   @server.register_procedure(auth=check_view_permissions("auth.view_user"))
   def my_rpc_method_with_builtin_predicate(username: str):
       user = User.objects.get(username=username)
       return f"{user.first_name} {user.last_name}"

   @server.register_procedure(auth=forbid_bots_access)
   def my_rpc_method_with_custom_authentication(a, b):
       return a + b
