==============
Error handling
==============

.. _exceptions:

Pre-defined error codes and exceptions
--------------------------------------

.. automodule:: modernrpc.exceptions
   :members:

Customize error handling
------------------------

If you want to define customized exceptions for your application, you can create ``RPCException`` sub-classes and set,
for each custome exception, a *faultCode* to ``RPC_CUSTOM_ERROR_BASE + N`` with ``N`` a unique number.

Here is an example:

.. code:: python

   class MyException1(RPCException):
       def __init__(self, message):
           super(RPCInternalError, self).__init__(RPC_CUSTOM_ERROR_BASE + 1, message)

   class MyException2(RPCException):
       def __init__(self, message):
           super(RPCInternalError, self).__init__(RPC_CUSTOM_ERROR_BASE + 2, message)

Anyway, any exception raised during the RPC method execution will generate a ``RPCInternalError`` with an error message
constructed from the underlying error. As a result, the RPC client will have a correct message describing what went
wrong.
