Server configuration
====================

Starting with v2, the ``RpcServer`` class is the central component that handles remote procedure calls.

Basic usage
-----------

First, create an RPC server instance:

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

All requests to ``http://yourwebsite/rpc/`` will be routed to the server's view. They will be inspected and
parsed to be interpreted as RPC calls. The result of procedure calls will be encapsulated into a response according
to the request's protocol (JSON-RPC or XML-RPC).

Advanced configuration
----------------------

You can modify the behavior of the server by passing arguments to its constructor.

Restrict supported protocol
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the ``supported_protocol`` parameter, you can make sure a given server will handle only JSON-RPC or XML-RPC requests.
This can be used to set up protocol-specific servers.

Default: ``supported_protocol = Protocol.ALL``

.. code-block:: python
   :caption: myapp/rpc.py

    from modernrpc import Protocol
    from modernrpc.server import RpcServer

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

Multiple servers
^^^^^^^^^^^^^^^

In version 2.0, you can create multiple server instances, each with its own set of procedures and configuration:

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

System procedures
^^^^^^^^^^^^^^^^

By default, the server automatically registers system procedures like `system.listMethods`. You can disable this behavior by setting:

.. code-block:: python
   :caption: settings.py

    MODERNRPC_REGISTER_SYSTEM_PROCEDURES = False

For more information about documentation generation, authentication, and other advanced features, please refer to the Advanced section of this documentation.
