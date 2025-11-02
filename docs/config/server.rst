Server / Namespaces
===================

Server
------

The ``RpcServer`` class is the central component that handles remote procedure calls.

At least one instance must be created.

.. code-block:: python
   :caption: myproject/myapp/rpc.py

    from modernrpc.server import RpcServer

    server = RpcServer()

A server instance expose a view that must be added to the Django routing system

.. code-block:: python
   :caption: myproject/myproject/urls.py

    from django.urls import path
    from myapp.rpc import server

    urlpatterns = [
        # ... other url patterns
        path('rpc/', server.view),  # Synchronous view
    ]

Then, all requests to ``http://yourwebsite/rpc/`` will be routed to the server's view. They will be inspected and
parsed to be interpreted as RPC calls.

If a `POST` request have a correct `Content-Type` header and a well formed body, it will be handled by the right
XML-RPC or JSON-RPC backend. The result of procedure calls will be encapsulated into a well-formed response, according
to the request protocol (XML or JSON-RPC)

.. note:: You are free to choose the path that will be used to handle your remote procedure calls, but ``/rpc`` or
   ``/RPC2`` are the moste commonly used paths (example in `xmlrpc.server docs`_)

.. _xmlrpc.server docs: https://docs.python.org/fr/3/library/xmlrpc.server.html#simplexmlrpcserver-example

Protocol restriction
^^^^^^^^^^^^^^^^^^^^

Using the ``supported_protocol`` argument, you can configure a given server to handle only JSON-RPC or XML-RPC
requests. This can be used to set up protocol-specific servers.

Default: ``supported_protocol = Protocol.ALL``

.. code-block:: python
   :caption: myapp/rpc.py

    from modernrpc import Protocol, RpcServer

    # Create protocol-specific servers
    json_server = RpcServer(supported_protocol=Protocol.JSON_RPC)
    xml_server = RpcServer(supported_protocol=Protocol.XML_RPC)

.. code-block:: python
   :caption: urls.py

    from django.urls import path
    from myapp.rpc import json_server, xml_server

    urlpatterns = [
        path('json-rpc/', json_server.view),
        path('xml-rpc/', xml_server.view),
    ]

System procedures
^^^^^^^^^^^^^^^^^

By default, 3 introspection procedures (+ 1 multicall procedure, only for XML-RPC requests) are registered by a server,
under the namespace ``system``. See :ref:`Introspection procedures` for history and  protocol specific details, as
well as :ref:`Introspection procedures & multicall` for JSON-RPC specific implementation.


.. automodule:: modernrpc.system_procedures
   :private-members: __system_list_methods, __system_method_signature, __system_method_help, __system_multicall

.. note:: `system.multicall` builtin method is registered as synchronous version by default. In this version, each
   procedure is executed sequentially. If you want to opt-in for the asynchronous version (procedures executed
   concurently using ``asyncio.gather()``, set ``settings.MODERNRPC_XMLRPC_ASYNC_MULTICALL = True``.


Using the ``register_system_procedures`` argument, you can completely disable their automatic registration.

Default: ``register_system_procedures = True``

.. code-block:: python
   :caption: myproject/myapp/rpc.py

    from modernrpc.server import RpcServer

    server = RpcServer(register_system_procedures=False)

    # server won't register the system.* procedures

.. warning::

  Disabling the system procedure registration may prevent some clients (in particular, XML-RPC ones) to
  send request to your server, use at your own risk.

Authentication
^^^^^^^^^^^^^^

.. code-block:: python
   :caption: myapp/rpc.py

    from myapp.auth import my_auth_callback
    from modernrpc.server import RpcServer

    # Create a server with authentication
    server = RpcServer(auth=my_auth_callback)

    @server.register_procedure
    def multiply(a, b):
        return a * b

All procedures registered in the server will use the auth callback configured in the server.

.. note::
  Configured authentication callback can be overridden at namespace or procedure level.

For more information about authentication, see :ref:`Authentication`.

GET requests redirection
^^^^^^^^^^^^^^^^^^^^^^^^

By default, when the server receive a request on a non-POST method, a "Method Not Allowed (405)" response is returned.
Sometimes, you may need to allow GET requests to really return a page, for example to display some documentation
about the RPC server.

For that use case, server can be configured with ``redirect_get_request_to`` argument. It allows any value accepted
by ``django.shortcuts.redirect`` function (see `official redirect() docs`_). When configured, a permanent redirection
to the corresponding location will be returned on GET requests.

.. _official redirect() docs: https://docs.djangoproject.com/en/5.2/topics/http/shortcuts/#redirect

Namespace
---------

Namespaces allow you to organize related RPC procedures under a common prefix. This is useful for:

- Grouping related procedures together
- Avoiding name conflicts between procedures
- Providing a clearer API structure

Creating a namespace
^^^^^^^^^^^^^^^^^^^^

To create a namespace, instantiate the ``RpcNamespace`` class:

.. code-block:: python
   :caption: myapp/math.py

    from modernrpc import RpcNamespace

    # Create a namespace for math procedures
    math = RpcNamespace()

Registering procedures
^^^^^^^^^^^^^^^^^^^^^^

You can register procedures to a namespace using the ``register_procedure`` method, similar to how you
would with an ``RpcServer``:

.. code-block:: python
   :caption: myapp/math.py

    @math.register_procedure
    def add(a, b):
        return a + b

    @math.register_procedure
    def subtract(a, b):
        return a - b

See :ref:`Customize registration` for a list of available customization options.

Registering a namespace to a server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To make the procedures in a namespace available through your RPC server, register the namespace to the server:

.. code-block:: python
   :caption: myapp/rpc.py

    from modernrpc.server import RpcServer
    from myapp.math import math

    server = RpcServer()
    server.register_namespace(math, "math")

This will make the procedures available under the prefix "math.", so clients can call
them as `math.add` and `math.subtract`.

If you don't provide a name when registering a namespace, the procedures will be registered without a prefix:

.. code-block:: python
   :caption: myapp/rpc.py

    # Register without a prefix
    server.register_namespace(math)

    # Procedures are available as "add" and "subtract"

Authentication
^^^^^^^^^^^^^^

Namespaces can have their own authentication settings that override the server's settings:

.. code-block:: python
   :caption: myapp/math.py

    # Create a namespace with authentication
    secure_math = RpcNamespace(auth=my_auth_callback)

    @secure_math.register_procedure
    def multiply(a, b):
        return a * b

All procedures registered in the namespace will use the auth callback configured in the namespace.

.. note::
  Configured authentication callback can be overridden at procedure level.

For more information about authentication, see :ref:`Authentication <auth-ref>`.


Multiple servers definition
---------------------------

You can create multiple server.

.. code-block:: python
   :caption: myapp/rpc.py

    from modernrpc.server import RpcServer

    # Create multiple server instances
    api_v1 = RpcServer()
    api_v2 = RpcServer()

.. code-block:: python
   :caption: urls.py

    from django.urls import path
    from myapp.rpc import api_v1, api_v2

    urlpatterns = [
       path('api/v1/', api_v1.view),
       path('api/v2/', api_v2.view),
    ]

When multiple servers are defined, each server can register its own procedures. This is useful to have different
functions performing the same task under the same name, but from a different path (a.k.a multiple API versions).

If needed, a procedure can be registered into multiple servers. This can be used to avoid code duplication when a
specific procedure should run the same code for different paths.

Sync and async views
--------------------

RpcServer exposes two HTTP entry points:

- view: a regular (synchronous) Django view callable
- async_view: an asynchronous Django view (a coroutine function)

They are feature-equivalent. Routing, serializers/deserializers selection, authentication/authorization, error handling,
introspection methods and namespaces all behave exactly the same in both cases. The only difference is the execution
model of the view itself.

When should you use async_view?

- If your deployment stack is ASGI-based (e.g., Daphne, Uvicorn, Hypercorn) and your RPC procedures contain async code
  async_view lets Django run the request handler as a coroutine. Multiple in-flight RPC calls can then await
  I/O concurrently, which can improve throughput and tail latency under I/O-bound workloads.
- If your procedures are all synchronous or you run under a purely WSGI stack, using view is perfectly fine;
  async_view will not provide benefits in that scenario.

Behavior details

- **Async procedures**: Procedures declared with async def will run concurrently within the same event loop when invoked
  through async_view, allowing overlapping awaits on I/O operations. Each individual request still executes one
  procedure at a time, but the server can progress multiple requests concurrently.
- **Sync procedures**: Synchronous procedures are still supported by async_view. Django will execute them in a threadpool
  (just like calling a sync view from an async context), so they work transparently, though without the concurrency
  advantages of native async code.
- API parity: Configuration and registration are identical; there is nothing special to do when registering procedures
  or namespaces for async_view.


.. code-block:: python
   :caption: urls.py

    from django.urls import path
    from modernrpc.server import RpcServer

    rpc = RpcServer()
    # register procedures, namespaces, auth, etc. on rpc as usual

    urlpatterns = [
        # Sync endpoint
        path("/rpc", rpc.view),
        # Async endpoint (same API, coroutine-based view)
        path("/async_rpc", rpc.async_view),
    ]

Notes

- Django has supported asynchronous views since 3.1; modernrpc supports Django 3.2 to 5.2. async_view will work on all
  supported Django versions when running under an ASGI server.
- You can expose both endpoints simultaneously (as shown above). Clients can choose either; functionality is identical.
