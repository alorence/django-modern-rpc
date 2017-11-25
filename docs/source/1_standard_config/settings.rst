========
Settings
========

Django-modern-rpc behavior can be customized by defining some values in project's ``settings.py``.

Basic configuration
===================

``MODERNRPC_METHODS_MODULES``
-----------------------------

Default: ``[]`` (Empty list)

Define the list of python modules containing RPC methods. You must set this list with at least one module.
At startup, the list is looked up to register all python functions decorated with `@rpc_method`.

JSON Serialization and deserialization
======================================
You can configure how JSON-RPC handler will serialize and unserialize data:

``MODERNRPC_JSON_DECODER``
--------------------------

Default: ``'json.decoder.JSONDecoder'``

Decoder class used to convert python data to JSON

``MODERNRPC_JSON_ENCODER``
--------------------------

Default: ``'django.core.serializers.json.DjangoJSONEncoder'``

Encoder class used to convert JSON to python values. Internally, modernrpc uses the default `Django JSON encoder`_,
which improves the builtin python encoder by adding support for additional types (DateTime, UUID, etc.).

.. _Django JSON encoder: https://docs.djangoproject.com/en/dev/topics/serialization/#djangojsonencoder

XML serialization and deserialization
=====================================

``MODERNRPC_XMLRPC_USE_BUILTIN_TYPES``
--------------------------------------

Default: ``True``

Control how builtin types are handled by XML-RPC serializer and deserializer. If set to True (default), dates will be
converted to ``datetime.datetime`` by XML-RPC deserializer. If set to False, dates will be converted to
`XML-RPC DateTime`_ instances (or `equivalent`_ for Python 2).

This setting will be passed directly to `ServerProxy`_ instantiation.

.. _XML-RPC DateTime: https://docs.python.org/3/library/xmlrpc.client.html#datetime-objects
.. _equivalent: https://docs.python.org/2/library/xmlrpclib.html#datetime-objects
.. _ServerProxy: https://docs.python.org/3/library/xmlrpc.client.html#xmlrpc.client.ServerProxy

``MODERNRPC_XMLRPC_ALLOW_NONE``
-------------------------------

Default: ``True``

Control how XML-RPC serializer will handle None values. If set to True (default), None values will be converted to
`<nil>`. If set to False, the serializer will raise a ``TypeError`` when encountering a `None` value.

``MODERNRPC_XMLRPC_DEFAULT_ENCODING``
-------------------------------------

Default: ``None``

Configure the default encoding used by XML-RPC serializer.

``MODERNRPC_XML_USE_BUILTIN_TYPES``
-----------------------------------

Default: ``True``

Deprecated. Define ``MODERNRPC_XMLRPC_USE_BUILTIN_TYPES`` instead.

Python 2 String standardization
===============================

``MODERNRPC_PY2_STR_TYPE``
--------------------------

Default: ``None``

Define target type for :ref:`GlobalStringStandardization`.

``MODERNRPC_PY2_STR_ENCODING``
------------------------------

Default: ``UTF-8``

Define global encoding used in :ref:`GlobalStringStandardization`.

RPC entry points configuration
==============================

``MODERNRPC_HANDLERS``
----------------------

Default: ``['modernrpc.handlers.JSONRPCHandler', 'modernrpc.handlers.XMLRPCHandler']``

List of handler classes used by default in any ``RPCEntryPoint`` instance. If you defined your custom handler for any
protocol, you can replace the default class used

``MODERNRPC_DEFAULT_ENTRYPOINT_NAME``
-------------------------------------

Default: ``'__default_entry_point__'``

Default name used for anonymous ``RPCEntryPoint``

Other available settings
========================

``MODERNRPC_DOC_FORMAT``
------------------------

Default: ``''`` (Empty String)

Configure the format of the docstring used to document your RPC methods.

Possible values are: ``(empty)``, ``rst`` or ``markdown``.

.. note::
    The corresponding package is not automatically installed. You have to ensure library `markdown` or `docutils` is
    installed in your environment if you set ``settings.MODERNRPC_DOC_FORMAT`` to a non-empty value


