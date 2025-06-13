Error handling
==============

.. note:: TODO

   This section needs to be reworked for v2


Introduction
------------

Error handling in RPC protocols is a challenging topic. Since errors must be returned as standard response,
it must always be caught and returned properly with the right format.

Status code
-----------

`XML-RPC spec <https://xmlrpc.com/spec.md#response-format>`_ about response status code

    Unless there's a lower-level error, always return 200 OK.

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

Customize Error Handling
------------------------

When an exception occurs during the execution of an RPC method, django-modern-rpc converts it to an appropriate RPC error response. By default, any exception that is not an instance of ``RPCException`` is wrapped in an ``RPCInternalError`` with the exception message.

Custom Error Handlers
^^^^^^^^^^^^^^^^^^^^^

You can customize how specific exceptions are handled by registering custom error handlers with the ``error_handler`` method. This allows you to:

- Convert specific exceptions to custom RPC errors
- Add additional information to error responses
- Handle exceptions in a way that makes sense for your application

Here's an example of how to register and use a custom error handler:

.. code-block:: python

   from modernrpc.exceptions import RPCException
   from modernrpc.server import RpcServer

   server = RpcServer()

   # Define a handler function for ValueError
   def handle_value_error(exc):
       # Convert ValueError to a custom RPC error
       return RPCException(code=12345, message=f"Invalid value: {exc}")

   # Register the handler for ValueError
   server.error_handler(ValueError, handle_value_error)

   # For a custom exception
   class MyCustomException(Exception):
       pass

   def handle_custom_exception(exc):
       # You can return any RPCException or subclass
       return RPCException(code=54321, message="A custom error occurred")

   server.error_handler(MyCustomException, handle_custom_exception)

When an exception occurs, the server will:

1. Check if the exception matches any registered error handler
2. If a match is found, call the handler with the exception
3. If the handler returns an RPCException, use it as the error response
4. If the handler returns None, fall back to the default error handling
5. If no handler matches, use the default error handling

The default error handling:

- Returns the exception as-is if it's an RPCException
- Wraps the exception in an RPCInternalError otherwise

This mechanism allows you to provide more meaningful error responses to your RPC clients while keeping your RPC methods focused on their core functionality.
