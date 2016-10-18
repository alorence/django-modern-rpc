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

   - The functions must be declared or imported in your top-level module

Method 2: Explicit registration
===============================

If for some reason you need to explicitly register your methods, you can do it using the function ``register_method()``
from the module ``modernrpc.core``. The best place to perform the registration is in your app's config ``ready()``
method. For more information about ``AppConfig`` classes and the ``ready()`` method, please check the
`Django documentation <https://docs.djangoproject.com/en/dev/ref/applications/>`_.

Here is an example of this registration method:

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

Configure the registration
==========================

No matter which registration method you chose, you have the same configuration options to change the behavior of your
RPC methods.

Both ``@rpc_method()`` decorator and ``register_method()`` have the same arguments:

``name = None``
  Can be used to override the external name of a RPC method. This is the only way to define dotted names for RPC
  methods, since python syntax does not allows such names in functions definitions. Example::

    register_method(add, name='math.additioner')

``protocol = ALL``
  Set the protocol argument to ``modernrpc.handlers.JSONRPC`` or ``modernrpc.handlers.XMLRPC`` to
  ensure a method will be available **only** via the corresponding protocol. Example::

   register_method(add, protocol=modernrpc.handlers.JSONRPC)

``entry_point = ALL``
  Set the entry_point argument to one or more str value to ensure the method will be available only via calls to
  corresponding entry point name. Fore more information, please check the documentation about :doc:`rpc_view`.
  Example::

   register_method(add, entry_point='apiV2')


Functions reference
===================

.. autofunction:: modernrpc.core.register_method

.. autofunction:: modernrpc.core.rpc_method
