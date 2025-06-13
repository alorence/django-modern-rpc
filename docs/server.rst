Server / Namespaces
===================

Server
------

The ``RpcServer`` class is the central component that handles remote procedure calls.

Default configuration
^^^^^^^^^^^^^^^^^^^^^

A default ``RpcServer`` instance will handle any RPC request it receives

.. code-block:: python
   :caption: myproject/myapp/rpc.py

    from modernrpc.server import RpcServer

    server = RpcServer()

All requests to ``http://yourwebsite/rpc/`` will be routed to the server's view. They will be inspected and
parsed to be interpreted as RPC calls. The result of procedure calls will be encapsulated into a response according
to the request's protocol (JSON-RPC or XML-RPC).

Protocol restriction
^^^^^^^^^^^^^^^^^^^^

Using the ``supported_protocol`` argument, you can make sure a given server will handle only JSON-RPC or XML-RPC requests.
This can be used to set up protocol-specific servers.

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

Using the ``register_system_procedures`` argument, you can disable the automatic registration of :ref:`system procedures<sys-procedures-ref>`.

Default: ``register_system_procedures = True``

.. code-block:: python
   :caption: myproject/myapp/rpc.py

    from modernrpc.server import RpcServer

    server = RpcServer(register_system_procedures=False)

    # server won't register the system.* procedures

.. warning::
  Disabling the system procedure registration may prevent some clients (in particular, XML-RPC ones) to send request to your server, use at your own risks.

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

Registering procedures to a namespace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can register procedures to a namespace using the ``register_procedure`` method, similar to how you would with an ``RpcServer``:

.. code-block:: python
   :caption: myapp/math.py

    @math.register_procedure
    def add(a, b):
        return a + b

    @math.register_procedure
    def subtract(a, b):
        return a - b

Registering a namespace to a server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To make the procedures in a namespace available through your RPC server, register the namespace to the server:

.. code-block:: python
   :caption: myapp/rpc.py

    from modernrpc.server import RpcServer
    from myapp.math import math

    server = RpcServer()
    server.register_namespace(math, "math")

This will make the procedures available with the prefix "math.", so clients can call them as "math.add" and "math.subtract".

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

.. warning::
  This section needs more detailed explanation & examples
