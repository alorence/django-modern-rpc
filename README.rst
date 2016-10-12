=================
django-modern-rpc
=================

.. image:: https://travis-ci.org/alorence/django-modern-rpc.svg?branch=master
   :target: https://travis-ci.org/alorence/django-modern-rpc

.. image:: https://coveralls.io/repos/github/alorence/django-modern-rpc/badge.svg?branch=master
   :target: https://coveralls.io/github/alorence/django-modern-rpc?branch=master


.. image:: https://readthedocs.org/projects/django-modern-rpc/badge/?version=latest
   :target: http://django-modern-rpc.readthedocs.io/en/latest/

.. note::
   This project is under development, and is not ready for production. You are free to install and
   test it, provide feedback (report issues or make pull requests) but there is no guarantee that the module is free
   of bugs. In addition, all planned features have not been implemented yet.

-----------
Information
-----------

django-modern-rpc is a free, lightweight RPC server for Django projects.
It supports JSON-RPC and XML-RPC requests under python 2.7, 3.3, 3.4,
3.5 and Django 1.8, 1.9 and 1.10.

--------
Features
--------

The project is under active development, so all the features are not yet
implemented. The list of available features is:

- XML-RPC & JSON-RPC support
- Usual errors are correctly reported to user according to the standard
- Multi-entry point, with specific methods and protocol attached
- Supported system methods:

  - system.listMethods()
  - system.methodSignature()

-----------------------------
Features planned to implement
-----------------------------

- System introspection methods (methodHelp(), etc.)
- Multi-call

------------
Installation
------------

To install django-modern-rpc, simply use pip::

    pip install django-modern-rpc

-----------
Quick start
-----------

Decorate the methods you want to make reachable from RPC call:

.. code:: python

    # In myproject/rpc_app/rpc_methods.py
    from modernrpc.core import rpc_method

    @rpc_method()
    def add(a, b):
        return a + b

and make sure these functions are imported at Django startup. A simple
way to do that is to import them in your app's module:

.. code:: python

    # In myproject/rpc_app/__init__.py
    from rpc_app.rpc_methods import add

Now, you have to declare an entry point. This is a standard Django view
which will automatically route the request to the right handler (for
JSON-RPC or XML-RPC call) and call the method on the server.

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        url(r'^rpc/', RPCEntryPoint.as_view(), name="rpc_entry_point"),
    ]

Now, you can call the function add from a client:

.. code:: python

    try:
        # Python 3
        import xmlrpc.client as xmlrpc_module
    except ImportError:
        # Python 2
        import xmlrpclib as xmlrpc_module

    client = xmlrpc_module.ServerProxy('http://127.0.0.1:8000/all-rpc/')
    print(client.add(2, 3))

    # Returns: 5
