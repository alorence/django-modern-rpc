========
Settings
========

In your project's settings, you can override some variable to customize behavior of django-modern-rpc.

Basic configuration
===================
.. autodata:: modernrpc.config.MODERNRPC_METHODS_MODULES

JSON Serialization and deserialization
======================================
You can configure how JSON-RPC handler will serialize and unserialize data:

.. autodata:: modernrpc.config.MODERNRPC_JSON_DECODER
.. autodata:: modernrpc.config.MODERNRPC_JSON_ENCODER

Internally, the default `JSON encoder used is provided by Django <https://github.com/django/django/blob/master/django/core/serializers/json.py#L90>`_,
it improves the builtin python encoder behavior::

   JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs. [JSONEncoder]_

XML serialization and deserialization
=====================================
.. autodata:: modernrpc.config.MODERNRPC_XMLRPC_ALLOW_NONE
.. autodata:: modernrpc.config.MODERNRPC_XMLRPC_DEFAULT_ENCODING
.. autodata:: modernrpc.config.MODERNRPC_XML_USE_BUILTIN_TYPES

Update handler classes
======================
.. autodata:: modernrpc.config.MODERNRPC_HANDLERS

Other settings available
========================
.. autodata:: modernrpc.config.MODERNRPC_DEFAULT_ENTRYPOINT_NAME
.. autodata:: modernrpc.config.MODERNRPC_DOC_FORMAT
