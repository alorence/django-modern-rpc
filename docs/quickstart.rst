Quickstart
==========

Installation
------------

Install ``django-modern-rpc`` in your environment

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc

Basic setup
-----------

Create an ``RpcServer`` instance and register your first procedure

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

Remote procedures are Python functions decorated with the server's ``register_procedure`` decorator.
Both server and procedure registration can be customized. See ...

Serve the procedures
--------------------

To execute a remote procedure, clients will send a *POST* request to a single url in your project. Declare the route
to this view in your project's ``urls.py``

.. code-block:: python
   :caption: myproject/myproject/urls.py

    from django.urls import path
    from myapp.rpc import server

    urlpatterns = [
        # ... other url patterns
        path('rpc/', server.view),
    ]

The server's view is already configured with CSRF exemption and POST-only restrictions.

Test the server
---------------

Start your project using ``python manage.py runserver`` and call your procedure using JSON-RPC or XML-RPC client, or
directly with your favourite HTTP client

.. TODO
   Add more code example, with curl for XML-RPC and with jsonrpcclient for JSON-RPC

.. code-block:: bash
   :caption: JSON-RPC example

    ~  $ curl -X POST localhost:8000/rpc -H "Content-Type: application/json" -d '{"id": 1, "method": "system.listMethods", "jsonrpc": "2.0"}'
    {"id": 1, "jsonrpc": "2.0", "result": ["add", "system.listMethods", "system.methodHelp", "system.methodSignature"]}

    ~  $ curl -X POST localhost:8000/rpc -H "Content-Type: application/json" -d '{"id": 2, "method": "add", "params": [5, 9], "jsonrpc": "2.0"}'
    {"id": 2, "jsonrpc": "2.0", "result": 14}

.. code-block:: python
   :caption: XML-RPC example

   from xmlrpc.client import ServerProxy

   with ServerProxy("http://localhost:8000/rpc") as proxy:
       proxy.system.listMethods()
       proxy.add(5, 9)

    # ['add', 'system.listMethods', 'system.methodHelp', 'system.methodSignature', 'system.multicall']
    # 14
