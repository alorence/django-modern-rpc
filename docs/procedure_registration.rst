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

Without any arguments, the ``@server.register_procedure`` decorator will register the procedure with default parameters. It will be
available for any protocol (XML-RPC or JSON-RPC) and will use the function name as the procedure's "methodName".

You can customize this behavior by adding arguments to the decorator:

Procedure name
^^^^^^^^^^^^^^

Use ``name`` to override the exposed procedure's "methodName". This is useful to set up a dotted name, which is not
allowed in Python.

Default: ``name = None``

.. code-block:: python

   from myapp.rpc import server

   @server.register_procedure(name='math.add')
   def add(a, b):
       return a + b

Protocol availability
^^^^^^^^^^^^^^^^^^^^^

When a procedure should be exposed only to a specific protocol, set the ``protocol`` argument to ``Protocol.JSON_RPC`` or
``Protocol.XML_RPC``.

Default: ``protocol = Protocol.ALL``

.. code-block:: python

   from modernrpc import Protocol
   from myapp.rpc import server

   @server.register_procedure(protocol=Protocol.JSON_RPC)
   def add(a, b):
       return a + b

.. note::
  The ``Protocol`` enum is now imported directly from the ``modernrpc`` package.

Multiple servers
^^^^^^^^^^^^^^^

In version 2.0, the concept of entry points has been replaced with multiple server instances. You can create multiple RPC servers, each with its own set of procedures:

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


Access request context
---------------------

In version 2.0, you can access the request context by specifying a parameter name that will receive the context object:

.. code-block:: python

    from myapp.rpc import server

    @server.register_procedure(context_target='ctx')
    def content_type_printer(ctx):
        """Return the Content-Type of the current request.

        :param ctx: Request context (automatically injected)
        :return: Content-Type header value
        """
        # The context object contains:
        # - ctx.request: Current HTTP request (HttpRequest instance)
        # - ctx.protocol: Current protocol (JSON-RPC or XML-RPC)
        # - ctx.server: The RPC server instance
        # - ctx.handler: The handler instance processing the request
        # - ctx.auth_result: Result of authentication check, if any

        # Return the Content-Type of the current request
        return ctx.request.content_type
