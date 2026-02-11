Error handling
==============

Introduction
------------

Error handling in RPC protocols is a challenging topic. Any error in remote procedure call processing must be returned
to the sender in a valid response with a code and a message. In addition, such a response must be returned with an HTTP
status 200.

To implement this behavior, django-modern-rpc uses Python exception mechanism to:

- Raise a pre-defined exception when processing request or serializing response to provide information about the actual
  error to the sender
- Catch any exception raised from procedures and convert it to a standardized error response.

Builtin exceptions
------------------

Here is a list of exceptions raised by django-modern-rpc

.. table::
   :widths: auto

   ======================  ========  ===============
    Exception                Code      Message
   ======================  ========  ===============
    RPCParseError           -32700    Parse error, unable to read the request: [...]
    RPCInsecureRequest      -32700    Security error: [...]
    RPCInvalidRequest       -32600    Invalid request: [...]
    RPCMethodNotFound       -32601    Method not found: [...]
    RPCInvalidParams        -32602    Invalid parameters: [...]
    RPCInternalError        -32603    Internal error: [...]
    RPCMarshallingError     -32603    Unable to serialize result data: [...]. Original exception: [...]
   ======================  ========  ===============

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

Customize error handling
------------------------

Overview
^^^^^^^^

In addition to the built‑in exceptions described above, django‑modern‑rpc lets you plug an error handler at the
server level. The handler is invoked as soon as any exception is raised from the library or your procedure and before
the error response is built and returned to the sender.

The handler receives the original Python exception and a ``RpcRequestContext`` object. It must have the following
signature:

.. code-block:: python

   from modernrpc import RpcRequestContext

   def my_error_handler(exc: BaseException, ctx: RpcRequestContext) -> None:
       ...

See :ref:`Accessing the context` for detailed documentation about ``RpcRequestContext`` object.

To register the handler in your server, uses the ``error_handler`` argument:

.. code-block:: python
   :caption: urls.py

   from django.urls import path
   from modernrpc.server import RpcServer

   server = RpcServer(error_handler=my_error_handler)

Use cases
^^^^^^^^^

Below are a few practical examples.

.. code-block:: python
   :caption: Send any caught exception to Sentry

   import sentry_sdk

   def logging_handler(exc: BaseException, ctx: RpcRequestContext) -> None:
       sentry_sdk.capture_exception(exc)


.. code-block:: python
   :caption: Log any exception as warning using python logging module

   import logging

   err_logger = logging.getLogger("myproject.errors")

   def logging_handler(exc: BaseException, ctx: RpcRequestContext) -> None:
       err_logger.warning("RPC error on %s: %s", ctx.request.path, exc, exc_info=True)


.. code-block:: python
   :caption: Transform a specific exception into another one

   def logging_handler(exc: BaseException, ctx: RpcRequestContext) -> None:
       if isinstance(exc, ZeroDivisionError):
           raise RPCInvalidParams("You cannot divide by Zero") from exc
