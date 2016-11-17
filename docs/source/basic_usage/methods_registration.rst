========================
RPC methods registration
========================

.. note::
   Until version 0.3, it was possible to choose between 2 different registration methods. This has been simplified
   in 0.4, there is now only one registration procedure

Decorate your methods
=====================

Decorator usage is simple. You only need to add ``@rpc_method`` decorator before any method you want to provide
via RPC calls.

.. code:: python

   # In myproject/rpc_app/rpc_methods.py
   from modernrpc.core import rpc_method

   @rpc_method()
   def add(a, b):
       return a + b

Declare the modules containing RPC methods
==========================================

In your ``settings.py``, add the variable ``MODERNRPC_METHODS_MODULES`` to define the list of modules containing
decorated RPC methods. In our example, the only RPC method is ``add()``, declared in ``myproject/rpc_app/rpc_methods.py``.

.. code:: python

   MODERNRPC_METHODS_MODULES = [
       'rpc_app.rpc_methods'
   ]

At startup, django-modern-rpc will lookup all modules listed in ``MODERNRPC_METHODS_MODULES``, and will register
all functions in those modules that have been decorated with ``@rpc_method``.

Configure the registration
==========================

If you decorate your methods with ``@rpc_method`` without specifying argument, the registered method will be available
for all entry points, for any XML-RPC or JSON-RPC call and will have the name of the corresponding function.

You can also change this behavior by setting arguments to the decorator:

``name = None``
  Can be used to override the external name of a RPC method. This is the only way to define dotted names for RPC
  methods, since python syntax does not allows such names in functions definitions. Example::

   @rpc_method(name='math.additioner')
   def add(a, b):
       return a + b

``protocol = ALL``
  Set the protocol argument to ``modernrpc.handlers.JSONRPC`` or ``modernrpc.handlers.XMLRPC`` to
  ensure a method will be available **only** via the corresponding protocol. Example::

   @rpc_method(protocol=modernrpc.handlers.JSONRPC)
   def add(a, b):
       return a + b

``entry_point = ALL``
  Set the entry_point argument to one or more str value to ensure the method will be available only via calls to
  corresponding entry point name. Fore more information, please check the documentation about :doc:`rpc_view`.
  Example::

   @rpc_method(entry_point='apiV2')
   def add(a, b):
       return a + b
