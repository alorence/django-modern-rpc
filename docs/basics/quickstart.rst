Quickstart
==========

Installation
------------

Install ``django-modern-rpc`` in your environment, using pip or equivalent tool

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc




Add ``modernrpc`` app to ``settings.INSTALLED_APPS``:

.. code-block:: python
   :caption: myproject/settings.py

    INSTALLED_APPS = [
        # ...
        'modernrpc',
    ]


Create an RPC Server
----------------

In version 2.0, you first create an RPC server instance that will manage your procedures:

.. code-block:: python
   :caption: myapp/rpc.py

    from modernrpc.server import RpcServer

    # Create a server instance
    server = RpcServer()

Declare procedures
-----------------

Remote procedures are Python functions decorated with the server's ``register_procedure`` decorator:

.. code-block:: python
   :caption: myapp/remote_procedures.py

    from myapp.rpc import server

    @server.register_procedure
    def add(a, b):
        """Add two numbers and return the result.

        :param a: First number
        :param b: Second number
        :return: Sum of a and b
        """
        return a + b

The ``register_procedure`` decorator can be customized to your needs. Read :doc:`register_procedure` for a full list of available options.

Create an entry point
---------------------

The entry point is a Django view that handles RPC calls. In version 2.0, you use the ``view`` property of your RPC server:

.. code-block:: python
   :caption: myproject/urls.py

    from django.urls import path
    from myapp.rpc import server

    urlpatterns = [
        # ... other url patterns
        path('rpc/', server.view),
    ]

The server's view is already configured with CSRF exemption and POST-only restrictions. You can customize the server behavior to your needs. Read :doc:`server` for full documentation.

Test the server
---------------

Start your project using ``python manage.py runserver`` and call your procedure using JSON-RPC or XML-RPC client, or
directly with your favourite HTTP client

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
