Error handling
==============

Introduction
------------

When remote procedures are executed, errors can be caused by almost anything: invalid request payload, arguments
deserialization or result serialization error, exception in method execution, etc. All errors must be
handled properly for 2 reasons :

1. An error response must be returned to RPC client (with an error code and a textual message)
2. Developers should be able to detect such errors (using logs, error reporting tool like Sentry, etc.)

For that reasons, django-modern-rpc handle all errors with Python builtin exception system. This allows for very
flexible error handling and allows to define custom exceptions with fixed error code and message.

Builtin exceptions
------------------

Hopefully, error codes for both JSON-RPC_ and XML-RPC_ are pretty similar. The following errors are fully supported
in django-modern-rpc.

.. _JSON-RPC: https://www.jsonrpc.org/specification#error_object
.. _XML-RPC: http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php

.. list-table::
   :widths: 40 60
   :header-rows: 1

   * - Code
     - Message
   * - -32700
     - parse error. not well formed
   * - -32600
     - Invalid request
   * - -32601
     - Method not found
   * - -32602
     - Invalid params
   * - -32603
     - Internal error

Additional errors from XML-RPC specs are less relevant in modern web application, and have not been implemented.

Custom exceptions
-----------------

When any exception is raised from a remote procedure, the client will get a default Internal Error as response. If you
want to return a custom error code and message instead, simply define a custom exception. Create an ``RPCException``
sub-classes and set a *faultCode* to ``RPC_CUSTOM_ERROR_BASE + N`` with ``N`` a unique number.

Here is an example:

.. code-block:: python

   class MyException1(RPCException):
       def __init__(self, message):
           super().__init__(RPC_CUSTOM_ERROR_BASE + 1, message)

   class MyException2(RPCException):
       def __init__(self, message):
           super().__init__(RPC_CUSTOM_ERROR_BASE + 2, message)

Such exceptions raised from your remote procedure will be properly returned to client.

Log errors
----------

.. versionadded:: 1.0

By default, when an exception is caught from modernrpc code, a stacktrace of the error will be printed in the
default log output. This allows developer to detect such case and fix the issue if needed.

To disable this behavior, set :ref:`MODERNRPC_LOG_EXCEPTIONS` to `False`.

---

Error handling
^^^^^^^^^^^^^

In version 2.0, you can register custom error handlers to handle specific exceptions:

.. code-block:: python
   :caption: myapp/rpc.py

    from modernrpc.server import RpcServer
    from modernrpc.exceptions import RPCInternalError

    # Create a server instance
    server = RpcServer()

    # Register a custom error handler
    @server.error_handler(ValueError)
    def handle_value_error(exception):
        # Convert ValueError to a custom RPC error
        return RPCInternalError(f"Invalid value: {exception}")

This allows you to customize how specific exceptions are handled and reported to clients.
