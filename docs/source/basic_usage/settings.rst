========
Settings
========

Django-modern-rpc behavior can be customized by defining some values in global ``settings.py``.
This page show the list of variables and their default values.

Basic configuration
===================
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_METHODS_MODULES

JSON Serialization and deserialization
======================================
You can configure how JSON-RPC handler will serialize and unserialize data:

.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_JSON_DECODER
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_JSON_ENCODER

Internally, the default `JSON encoder used is provided by Django <https://github.com/django/django/blob/master/django/core/serializers/json.py#L90>`_,
it improves the builtin python encoder behavior::

   JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs. [JSONEncoder]_

XML serialization and deserialization
=====================================
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_XMLRPC_ALLOW_NONE
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_XMLRPC_DEFAULT_ENCODING
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_XML_USE_BUILTIN_TYPES

RPC entry point configuration
=============================
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_HANDLERS
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_DEFAULT_ENTRYPOINT_NAME

Other settings available
========================
.. autoattribute:: modernrpc.config.DefaultValues.MODERNRPC_DOC_FORMAT
