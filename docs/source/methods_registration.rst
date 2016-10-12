========================
RPC methods registration
========================

There is multiple ways to register your methods and make them accessible via RPC calls. It's up to you to choose the
best for your needs.

Method 1: Decorator
===================

Decorator usage is simple. You only need to add ``@rpc_method()`` before any method you want to provide via RPC calls.

.. code:: python

   # In myproject/rpc_app/rpc_methods.py
   from modernrpc.core import rpc_method

   @rpc_method()
   def add(a, b):
       return a + b

The python interpreter must run the decorator to correctly register your RPC methods. Thus, your methods have to be
imported when your Django project startup. In that example, if ``rpc_app`` is part of ``INSTALLED_APPS`` Django setting,
you can import your RPC methods in ``rpc_app``'s ``__init__.py``:

.. code:: python

   # In myproject/rpc_app/__init__.py
   from rpc_app.rpc_methods import *

.. note::
   You can also declare your RPC methods directly in your app's `__init__.py`.

Pros:

   - Increase code readability: you directly see which functions are RPC methods in your code

Cons:

   - Cozekek

Method 2: Explicit registration
===============================

.. code:: python

   # In myproject/rpc_app/apps.py
   from django.apps import AppConfig

   from modernrpc.core import register_method
   from rpc_app.rpc_methods import add

   class MyAppConfig(AppConfig):
       name = 'rpc_app'
       def ready(self):
           register_method(add)

Pros:

   - You control which methods are registered or not
   - Does not cause PEP8 validation warning (Unused imports, etc.)

Cons:

   - You have to register all methods one by one.