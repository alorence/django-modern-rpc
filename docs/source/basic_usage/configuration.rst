=============
Configuration
=============

In your project's settings, you can override some variable to customize behavior of django-modern-rpc.

JSON Serialization and deserialization
======================================
You can configure how JSON-RPC handler will serialize and unserialize data:

.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_JSON_DECODER
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_JSON_ENCODER

The default Django encoder is used by default, it improves the default python encoder behavior:

   JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.

RPC Method additional argument
==============================
If you need to access context in your RPC method, simply declare it with a param ``**kwargs``. The dict instance
passed to the function will contains information about current request, entry point, protocol, etc.

You can configure under which keys these information will be available:

.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_REQUEST_PARAM_NAME
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_PROTOCOL_PARAM_NAME
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_ENTRY_POINT_PARAM_NAME

Update handler classes
======================
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_HANDLERS

Other settings available
========================
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_XML_USE_BUILTIN_TYPES
