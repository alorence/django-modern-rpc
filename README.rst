=================
django-modern-rpc
=================

.. image:: https://travis-ci.org/alorence/django-modern-rpc.svg?branch=master
   :target: https://travis-ci.org/alorence/django-modern-rpc

.. image:: https://coveralls.io/repos/github/alorence/django-modern-rpc/badge.svg?branch=master
   :target: https://coveralls.io/github/alorence/django-modern-rpc?branch=master

.. image:: https://readthedocs.org/projects/django-modern-rpc/badge/?version=latest
   :target: http://django-modern-rpc.readthedocs.io/en/latest/

-----------
Description
-----------

django-modern-rpc is a free, lightweight RPC server for Django projects. The project is still under development,
and its API is subject to modifications. Currently supported features are:

- XML-RPC (as described on http://xmlrpc.scripting.com/) and JSON-RPC 2.0 (from http://www.jsonrpc.org/specification)
  support. Please note that JSON-RPC 1.0 is not supported.
- Automatic protocol detection based on the request's header ``Content-Type``
- Python 2.7, 3.3, 3.4 and 3.5
- Django 1.8, 1.9 and 1.10
- Usual error handled and reported to callers
- Multi entry points, with specific methods and protocol attached
- System introspection methods:

  - system.listMethods()
  - system.methodSignature()
  - system.methodHelp()
  - system.multicall() (XML-RPC only, using specification from https://mirrors.talideon.com/articles/multicall.html)

----------------------------
Features not yet implemented
----------------------------

- Multi-call for JSON-RPC
- Methods documentation generated as HTML page
- Built-in support for request authentications

-----------
Quick start
-----------
1. Install the library using pip::

    pip install django-modern-rpc

2. Decorate the methods you want to make available via RPC calls:

.. code:: python

    # In myproject/rpc_app/rpc_methods.py
    from modernrpc.core import rpc_method

    @rpc_method()
    def add(a, b):
        return a + b

and make sure these functions are imported at Django startup. A simple
way to do this is to import them in your app's module:

.. code:: python

    # In myproject/rpc_app/__init__.py
    from rpc_app.rpc_methods import add

3. Declare an entry point, a view which will generate a correct RPC response depending on the incoming request:

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        url(r'^rpc/', RPCEntryPoint.as_view(), name="rpc_entry_point"),
    ]

Now, you can call the RPC method ``add`` from a client:

.. code:: python

    >>> from xmlrpc.client import ServerProxy
    >>> client = ServerProxy('http://127.0.0.1:8000/rpc/')
    >>> print(client.add(2, 3))
    5

To get more information, please read `the full documentation <http://django-modern-rpc.readthedocs.io>`_.
