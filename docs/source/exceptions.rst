Error handling
==============

Error handling is fully described in both XML & JSON-RPC standards. Each common error have an associated *faultCode*
and the response format is described, so errors can be handled correctly on the client side.

In django-modern-rpc, all errors are reported using a set of pre-defined exceptions. Thus, in JSON and XML-RPC handlers,
when an exception is catched, the correct error response is returned to the view to be transmitted to the client.

This simplify error management, and allow developpers to simply return errors to clients from inside a RPC Method.

.. _exceptions:

The pre-defined exception
-------------------------

RPCException(Exception)
^^^^^^^^^^^^^^^^^^^^^^^

This is the base class of all RPC exception. Custom exceptions raised by your RPC method
should inherits from RPCException.

RPCParseError(RPCException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raised by handlers if the request can't be read as valid JSOn or XML data.

RPCInvalidRequest(RPCException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raised by handlers if incoming JSON or XML data is not a valid JSON-RPC or XML-RPC data.

RPCUnknownMethod(RPCException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raised by handlers if in RPC request, the method called is not defined for the current entry point and protocol.

RPCInvalidParams(RPCException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raised by handlers if the RPC method's params does not match the parameters in RPC request

RPCInternalError(RPCException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raised by handlers if any standard exception is raised during the execution of the RPC method.
