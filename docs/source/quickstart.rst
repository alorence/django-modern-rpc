===========
Quick start
===========

Start using django-modern-rpc in a minute, following these simple steps.

Installation
============

Use pip::

   pip install django-modern-rpc

Create an entry point
=====================

An entry point is the URL used by clients to call your RPC methods. Declare as follow:

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other views

        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

For more information on entry point declaration and configuration, please read :doc:`the full
documentation <basic_usage/rpc_view>`.

Register your methods
=====================

Now, you must indicates to django-modern-rpc which methods in your code must be available via RPC calls.
There is various way to achieve this:

.. code:: python

   # In myproject/rpc_app/rpc_methods.py
   from modernrpc.core import rpc_method

   @rpc_method()
   def add(a, b):
       return a + b

This solution is quick, but you need to ensure the method is actually imported somewhere in your code. If it isn't,
the decorator rpc_method() is never called and your method will not be available to RPC calls.

You can import your function in many ways. For example, in the ``__init__.py`` of your app:

.. code:: python

   # In myproject/rpc_app/__init__.py
   from rpc_app.rpc_methods import add

.. note::
   There in another ways to register your RPC methods. For more information, please
   read :doc:`basic_usage/methods_registration`.
