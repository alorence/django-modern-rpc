Procedures registration
=======================

Introduction
------------

In Django-modern-rpc v2, you first create an RPC server instance, then use its ``register_procedure`` decorator to expose functions:

.. code-block:: python
   :caption: myproject/myapp/rpc.py

   from modernrpc.server import RpcServer

   # Create a server instance
   server = RpcServer()

.. code-block:: python
   :caption: myproject/myapp/remote_procedures.py

   from myapp.rpc import server

   @server.register_procedure
   def add(a, b):
       return a + b

This new approach gives you more control over your RPC procedures and eliminates the need for global registration through settings.

Customize registration
----------------------

By default, the ``@server.register_procedure`` decorator will register the procedure to be available to both XML-RPC
and JSON-RPC calls. The "methodName" of the procedure will be the function name.

You can customize this behavior by adding arguments to the decorator:

Procedure name
^^^^^^^^^^^^^^

Use ``name`` to override the exposed procedure's "methodName". This is useful to set up a dotted
name and workaround the Python syntax restrictions.

Default: ``name = None``

.. code-block:: python

   from myapp.rpc import server

   @server.register_procedure(name='math.add')
   def add(a, b):
       return a + b

Protocol availability
^^^^^^^^^^^^^^^^^^^^^

When a procedure should be exposed only to a specific protocol, set the ``protocol`` argument
to ``Protocol.JSON_RPC`` or ``Protocol.XML_RPC``.

Default: ``protocol = Protocol.ALL``

.. code-block:: python

   from modernrpc import Protocol
   from myapp.rpc import server

   @server.register_procedure(protocol=Protocol.JSON_RPC)
   def add(a, b):
       return a + b


Accessing the context
^^^^^^^^^^^^^^^^^^^^^

If you need to access some context information in your procedure, simply add an argument with a name of your choice,
and declare it in decorator: ``register_procedure(context_target="<arg_name>")``

.. code-block:: python

    from modernrpc import RpcRequestContext
    from myapp.rpc import server


    @server.register_procedure(context_target="ctx")
    def content_type_printer(ctx: RpcRequestContext):
        """Return the Content-Type of the current request.

        :param ctx: Request context (automatically injected)
        :return: Content-Type header value
        """
        # Return the Content-Type of the current request
        return ctx.request.content_type


Multiple servers
----------------

In version 2.0, the concept of entry points has been replaced with multiple server
instances. You can create multiple RPC servers, each with its own set of procedures:

.. versionchanged:: 2.0.0

   In previous versions, each 'RPCEntryPoint' could be defined with a name. Then, in procedure registration, it was
   possible to specify one or more entry points to register with. Now, if multiple servers are defined, each procedure
   will have to register to all servers. See :ref:`Migration guide`

.. code-block:: python
   :caption: myapp/rpc.py

   from modernrpc.server import RpcServer

   # Create multiple server instances
   api_v1 = RpcServer()
   api_v2 = RpcServer()

Then register procedures with the appropriate server:

.. code-block:: python
   :caption: myapp/remote_procedures.py

   from myapp.rpc import api_v1, api_v2

   # This will expose the procedure only through api_v1
   @api_v1.register_procedure
   def add(a, b):
       return a + b

   # This will expose the procedure only through api_v2
   @api_v2.register_procedure
   def multiply(a, b):
       return a * b

   # If you want to expose a procedure through multiple servers,
   # you can register it with each server
   @api_v1.register_procedure
   @api_v2.register_procedure
   def subtract(a, b):
       return a - b
