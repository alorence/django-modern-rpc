Quickstart
==========

Installation
------------

Install ``django-modern-rpc`` in your environment, using pip or equivalent tool

.. code-block:: bash

    pip install django-modern-rpc

Add ``modernrpc`` app to ``settings.INSTALLED_APPS``:

.. code-block:: python
   :caption: myproject/settings.py

    INSTALLED_APPS = [
        # ...
        'modernrpc',
    ]

Declare a procedure
-------------------

Remote procedures are global Python functions decorated with ``@rpc_method``.

.. code-block:: python
   :caption: myapp/remote_procedures.py

    from modernrpc.core import rpc_method

    @rpc_method
    def add(a, b):
        return a + b

``@rpc_method`` behavior can be customized to your needs. Read :doc:`register_procedure` for a full list of available
options.

Locate procedures modules
-------------------------

Django-modern-rpc will automatically register functions decorated with ``@rpc_method``, but needs a hint to locate them.
Set ``settings.MODERNRPC_METHODS_MODULES`` variable to indicate project's modules where remote procedures are declared.

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_METHODS_MODULES = [
        'myapp.remote_procedures'
    ]

Create an entry point
---------------------

The entrypoint is a special Django view handling RPC calls. Like any other view, it must
be declared in URLConf or any app specific ``urls.py``:

.. code-block:: python
   :caption: myproject/urls.py

    from django.urls import path
    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other url patterns
        path('rpc/', RPCEntryPoint.as_view()),
    ]

Entry points behavior can be customized to your needs. Read :doc:`entrypoints` for
full documentation.

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
