Procedures registration
=======================

Introduction
------------

Any global python function can be exposed. Simply decorate it with ``modernrpc.core.rpc_method``:

.. code-block:: python
   :caption: myproject/myapp/remote_procedures.py

   from modernrpc.core import rpc_method

   @rpc_method
   def add(a, b):
       return a + b

Django-modern-rpc will automatically register procedures at startup, as long as the containing module is listed
in ``settings.MODERNRPC_METHODS_MODULES``:

.. code-block:: python
   :caption: settings.py
   :name: settings

   MODERNRPC_METHODS_MODULES = [
       "myapp.remote_procedures",
   ]

.. note::
  Automatic registration is performed in ``modernrpc.apps.ModernRpcConfig.ready()``. See `Django docs <https://docs
  .djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready>`_ for additional information.

Customize registration
----------------------

Without any argument, ``@rpc_method`` decorator will register the procedure with default parameters. It will be
available for all entry points, any protocol (XML-RPC or JSON-RPC) and will have the function name as
procedure's "methodName".

You can also change this behavior by adding arguments:

Procedure name
^^^^^^^^^^^^^^

Use ``name`` to override the exposed procedure's "methodName". This is useful to setup a dotted name, which is not
allowed in python.

Default: ``name = None``

.. code-block:: python

   @rpc_method(name='math.add')
   def add(a, b):
       return a + b

Protocol availability
^^^^^^^^^^^^^^^^^^^^^

When a procedure must be exposed only to a specific protocol, set ``protocol`` argument to ``Protocol.JSON_RPC`` or
``Protocol.XML_RPC``.

Default: ``protocol = Protocol.ALL``

.. code-block:: python

   from modernrpc.core import rpc_method, Protocol

   @rpc_method(protocol=Protocol.JSON_RPC)
   def add(a, b):
       return a + b

.. note::
  Don't forget to import ``modernrpc.core.Protocol`` enum.

.. _entry_point_specific_procedure:

Entry point
^^^^^^^^^^^

If you declared multiple entry points (see :ref:`multiple_entry_points`) and want
a procedure to be exposed only from one of them, provide its name using ``entry_point`` argument.
You can also expose a procedure to 2 or more entry points by setting a list of strings.

Default: ``entry_point = modernrpc.core.ALL``

.. code-block:: python

   # This will expose the procedure to "apiV2" entry point only"
   @rpc_method(entry_point="apiV2")
   def add(a, b):
       return a + b

   # This will expose the procedure to 2 different entry points
   @rpc_method(entry_point=["apiV2", "legacy"])
   def multiply(a, b):
       return a * b


Access internal information
---------------------------

If you need to access some environment from your RPC method, simply adds ``**kwargs`` in function parameters. When the
function will be executed, a dict will be passed as argument, providing the following information:

 - Current HTTP request (``HttpRequest`` instance)
 - Current protocol (JSON-RPC or XML-RPC)
 - Current entry point name
 - Current handler instance

See the example to see how to access these values:

.. code:: python

    from modernrpc.core import rpc_method, REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY, HANDLER_KEY

    @rpc_method
    def content_type_printer(**kwargs):

        # Get the current request
        request = kwargs.get(REQUEST_KEY)

        # Other available objects are:
        # protocol = kwargs.get(PROTOCOL_KEY)
        # entry_point = kwargs.get(ENTRY_POINT_KEY)
        # handler = kwargs.get(HANDLER_KEY)

        # Return the Content-Type of the current request
        return request.content_type
