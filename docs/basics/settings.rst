========
Settings
========

Django-modern-rpc behavior can be customized by defining some values in project's ``settings.py``.

Basic settings
==============

MODERNRPC_METHODS_MODULES
-------------------------

:Required:  Yes
:Default:   ``[]`` (Empty list)

Define the list of python modules containing RPC methods. You must set this list with at least one module.
At startup, the list is looked up to register all python functions decorated with ``@rpc_method``.

MODERNRPC_LOG_EXCEPTIONS
------------------------

:Required:  No
:Default:   ``True``

Set to ``False`` if you want to disable logging on exception catching

MODERNRPC_DOC_FORMAT
--------------------

:Required:  No
:Default:   ``""`` (Empty string)

Configure the format of the docstring used to document your RPC methods.

Possible values are: ``""``, ``rst`` or ``markdown``.

.. note::
    The corresponding package is not automatically installed. You have to ensure library `markdown` or `docutils` is
    installed in your environment if set to a non-empty value

MODERNRPC_HANDLERS
------------------

:Required:  No
:Default:   ``['modernrpc.handlers.JSONRPCHandler', 'modernrpc.handlers.XMLRPCHandler']``

List of handler classes used by default in any ``RPCEntryPoint`` instance. If you defined your custom handler for any
protocol, you can replace the default class used

MODERNRPC_DEFAULT_ENTRYPOINT_NAME
---------------------------------

:Required:  No
:Default:   ``"__default_entry_point__"``

Default name used for anonymous ``RPCEntryPoint``

Protocol specific
=================
You can configure how JSON-RPC handler will serialize and deserialize data:

MODERNRPC_JSON_DECODER
----------------------

:Required:  No
:Default:   ``"json.decoder.JSONDecoder"``

Decoder class used to convert JSON data to python values.

MODERNRPC_JSON_ENCODER
----------------------

:Required:  No
:Default:   ``"django.core.serializers.json.DjangoJSONEncoder"``

Encoder class used to convert python values to JSON data. Internally, modernrpc uses the default `Django JSON encoder`_,
which improves the builtin python encoder by adding support for additional types (DateTime, UUID, etc.).

.. _Django JSON encoder: https://docs.djangoproject.com/en/dev/topics/serialization/#djangojsonencoder

MODERNRPC_XMLRPC_USE_BUILTIN_TYPES
----------------------------------

:Required:  No
:Default:   ``True``

Control how builtin types are handled by XML-RPC serializer and deserializer. If set to True (default), dates will be
converted to ``datetime.datetime`` by XML-RPC deserializer. If set to False, dates will be converted to
`XML-RPC DateTime`_ instances (or `equivalent`_ for Python 2).

This setting will be passed directly to `ServerProxy`_ instantiation.

.. _XML-RPC DateTime: https://docs.python.org/3/library/xmlrpc.client.html#datetime-objects
.. _equivalent: https://docs.python.org/2/library/xmlrpclib.html#datetime-objects
.. _ServerProxy: https://docs.python.org/3/library/xmlrpc.client.html#xmlrpc.client.ServerProxy

MODERNRPC_XMLRPC_ALLOW_NONE
---------------------------

:Required:  No
:Default:   ``True``

Control how XML-RPC serializer will handle None values. If set to True (default), None values will be converted to
`<nil>`. If set to False, the serializer will raise a ``TypeError`` when encountering a `None` value.

MODERNRPC_XMLRPC_DEFAULT_ENCODING
---------------------------------

:Required:  No
:Default:   ``None``

Configure the default encoding used by XML-RPC serializer.

MODERNRPC_XML_USE_BUILTIN_TYPES
-------------------------------

Deprecated. Define ``MODERNRPC_XMLRPC_USE_BUILTIN_TYPES`` instead.
