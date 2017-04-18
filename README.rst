=================
django-modern-rpc
=================

.. image:: https://travis-ci.org/alorence/django-modern-rpc.svg?branch=master
    :target: https://travis-ci.org/alorence/django-modern-rpc

.. image:: https://coveralls.io/repos/github/alorence/django-modern-rpc/badge.svg?branch=master
    :target: https://coveralls.io/github/alorence/django-modern-rpc?branch=master

.. image:: https://codecov.io/gh/alorence/django-modern-rpc/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/alorence/django-modern-rpc
  
.. image:: https://readthedocs.org/projects/django-modern-rpc/badge/?version=latest
    :target: http://django-modern-rpc.readthedocs.io/

.. image:: https://badge.fury.io/py/django-modern-rpc.svg
    :target: https://badge.fury.io/py/django-modern-rpc

.. image:: https://img.shields.io/badge/demo-online-brightgreen.svg
    :target: http://modernrpc.herokuapp.com/

-----------
Description
-----------

Django-modern-rpc provides a simple solution to implement a remote procedure call (RPC) server as part of your Django
project. It supports all major Django and Python versions.

Project's main features are:

- Simple and pythonic API
- Python 2.7, 3.3, 3.4, 3.5 and 3.6
- Django 1.8, 1.9, 1.10 and 1.11
- XML-RPC_ and `JSON-RPC 2.0`_ support (JSON-RPC 1.0 not supported)
- HTTP Basic Auth support
- Custom authentication support
- Automatic protocol detection based on request's ``Content-Type`` header
- High-level error management based on exceptions
- Multiple entry points, with specific methods and protocol attached
- RPC Methods documentation generated automatically, based on docstrings
- System introspection methods:

  - system.listMethods()
  - system.methodSignature()
  - system.methodHelp()
  - system.multicall() (XML-RPC only, using specification from https://mirrors.talideon.com/articles/multicall.html)

.. _XML-RPC: http://xmlrpc.scripting.com/
.. _JSON-RPC 2.0: http://www.jsonrpc.org/specification

-----------
Quick start
-----------
1. Use pip to install the package in your environment:

.. code:: bash

    pip install django-modern-rpc

2. Add it to your Django applications, in ``settings.py``:

.. code:: python

    INSTALLED_APPS = [
        ...
        'modernrpc',
    ]

3. Declare an entry point, a view generating correct RPC responses to incoming requests:

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

4. Use ``@rpc_method`` to register a global function in django-moder-rpc registry:

.. code:: python

    # In myproject/rpc_app/rpc_methods.py
    from modernrpc.core import rpc_method

    @rpc_method
    def add(a, b):
        return a + b

5. Declare the list of python modules containing your RPC methods, in ``settings.py``:

.. code:: python

    MODERNRPC_METHODS_MODULES = [
        'rpc_app.rpc_methods'
    ]

Now, you can call the method ``add`` from a client:

.. code:: python

    >>> from xmlrpc.client import ServerProxy
    >>> client = ServerProxy('http://localhost:8000/rpc/')
    >>> print(client.add(2, 3))
    5

For more information, please read `the full documentation`_.

.. _`the full documentation`: http://django-modern-rpc.readthedocs.io
