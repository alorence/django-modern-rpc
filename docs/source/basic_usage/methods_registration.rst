========================
RPC methods registration
========================

Django-modern-rpc will automatically register RPC methods at startup. To ensure this automatic registration is performed
quickly, you must provide the list of python modules where your remote methods are declared.

In ``settings.py``, add the variable ``MODERNRPC_METHODS_MODULES`` to define this list. In our example, the only defined
RPC method is ``add()``, declared in ``myproject/rpc_app/rpc_methods.py``.

.. code:: python

   MODERNRPC_METHODS_MODULES = [
       'rpc_app.rpc_methods'
   ]

When django-modern-rpc application will be loaded, it's `AppConfig.ready() method`_ is executed. The automatic
registration is performed at this step.

.. _`AppConfig.ready() method`: https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready

Decorate your RPC methods
=========================

Decorator usage is simple. You only need to add ``@rpc_method`` decorator before any method you want to provide
via RPC calls.

.. code:: python

   # In myproject/rpc_app/rpc_methods.py
   from modernrpc.core import rpc_method

   @rpc_method()
   def add(a, b):
       return a + b

.. _rpc_method_options:

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
  corresponding entry point name. Fore more information, please check the documentation about
  :ref:`multiple entry points declaration <multiple_entry_points>`.
  Example::

   @rpc_method(entry_point='apiV2')
   def add(a, b):
       return a + b

Access request, protocol and other info from a RPC method
=========================================================

See :doc:`../advanced/tips_and_tricks`.
