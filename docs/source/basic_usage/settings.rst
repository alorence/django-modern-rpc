========
Settings
========

In your project's settings, you can override some variable to customize behavior of django-modern-rpc.

Basic configuration
===================
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_METHODS_MODULES

JSON Serialization and deserialization
======================================
You can configure how JSON-RPC handler will serialize and unserialize data:

.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_JSON_DECODER
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_JSON_ENCODER

Internally, the default `JSON encoder used is provided by Django <https://github.com/django/django/blob/master/django/core/serializers/json.py#L90>`_,
it improves the builtin python encoder behavior::

   JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs. [JSONEncoder]_

XML serialization and deserialization
=====================================
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_XMLRPC_ALLOW_NONE
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_XMLRPC_DEFAULT_ENCODING
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_XML_USE_BUILTIN_TYPES

Update handler classes
======================
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_HANDLERS

Other settings available
========================
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
.. autodata:: modernrpc.modernrpc_settings.MODERNRPC_DOC_FORMAT
