========
Settings
========

Django-modern-rpc behavior can be customized by defining values in your project's ``settings.py``. This document describes all available settings and their default values.

Basic settings
=============

MODERNRPC_METHODS_MODULES
-------------------------

:Required:  Yes
:Default:   ``[]`` (Empty list)

Define the list of Python modules containing RPC methods. You must set this list with at least one module.
At startup, the list is looked up to register all Python functions decorated with ``@rpc_method``.

Example:

.. code-block:: python

    MODERNRPC_METHODS_MODULES = [
        'myapp.rpc_methods',
        'another_app.rpc_methods',
    ]

MODERNRPC_LOG_EXCEPTIONS
------------------------

:Required:  No
:Default:   ``True``

Set to ``False`` if you want to disable logging on exception catching. When enabled, exceptions raised during RPC method execution are logged using Python's logging system.

MODERNRPC_REGISTER_SYSTEM_PROCEDURES
-----------------------------------

:Required:  No
:Default:   ``True``

Set to ``False`` if you want to disable automatic registration of system procedures. By default, the RPC server
automatically registers system procedures (under the "system" namespace) that provide introspection capabilities.
If you don't need these procedures, you can disable them by setting this to ``False``.

MODERNRPC_DOC_FORMAT
--------------------

:Required:  No
:Default:   ``""`` (Empty string)

Configure the format of the docstring used to document your RPC methods.

Possible values are: ``""``, ``rst`` or ``markdown``.

.. note::
    The corresponding package is not automatically installed. You have to ensure library `markdown` or `docutils` is
    installed in your environment if set to a non-empty value.

MODERNRPC_HANDLERS
------------------

:Required:  No
:Default:   ``['modernrpc.handlers.JSONRPCHandler', 'modernrpc.handlers.XMLRPCHandler']``

List of handler classes used by default in any ``RPCEntryPoint`` instance. If you defined your custom handler for any
protocol, you can replace the default class used.

MODERNRPC_DEFAULT_ENTRYPOINT_NAME
---------------------------------

:Required:  No
:Default:   ``"__default_entry_point__"``

Default name used for anonymous ``RPCEntryPoint``.

Protocol specific settings
=========================

JSON-RPC Settings
----------------

MODERNRPC_JSON_DECODER
^^^^^^^^^^^^^^^^^^^^^^

:Required:  No
:Default:   ``"json.decoder.JSONDecoder"``

Decoder class used to convert JSON data to Python values.

MODERNRPC_JSON_ENCODER
^^^^^^^^^^^^^^^^^^^^^^

:Required:  No
:Default:   ``"django.core.serializers.json.DjangoJSONEncoder"``

Encoder class used to convert Python values to JSON data. Internally, modernrpc uses the default `Django JSON encoder`_,
which improves the builtin Python encoder by adding support for additional types (DateTime, UUID, etc.).

.. _Django JSON encoder: https://docs.djangoproject.com/en/dev/topics/serialization/#djangojsonencoder

XML-RPC Settings
--------------

MODERNRPC_XMLRPC_USE_BUILTIN_TYPES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Required:  No
:Default:   ``True``

Control how builtin types are handled by XML-RPC serializer and deserializer. If set to True (default), dates will be
converted to ``datetime.datetime`` by XML-RPC deserializer. If set to False, dates will be converted to
`XML-RPC DateTime`_ instances.

This setting will be passed directly to `ServerProxy`_ instantiation.

.. _XML-RPC DateTime: https://docs.python.org/3/library/xmlrpc.client.html#datetime-objects
.. _ServerProxy: https://docs.python.org/3/library/xmlrpc.client.html#xmlrpc.client.ServerProxy

MODERNRPC_XMLRPC_ALLOW_NONE
^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Required:  No
:Default:   ``True``

Control how XML-RPC serializer will handle None values. If set to True (default), None values will be converted to
`<nil>`. If set to False, the serializer will raise a ``TypeError`` when encountering a `None` value.

MODERNRPC_XMLRPC_DEFAULT_ENCODING
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Required:  No
:Default:   ``None``

Configure the default encoding used by XML-RPC serializer.

Deprecated Settings
==================

MODERNRPC_XML_USE_BUILTIN_TYPES
-------------------------------

Deprecated. Define ``MODERNRPC_XMLRPC_USE_BUILTIN_TYPES`` instead.

Advanced Configuration
=====================

Custom Handlers
--------------

If you need to customize how RPC requests are handled, you can create custom handler classes and configure django-modern-rpc to use them:

.. code-block:: python

    # settings.py
    MODERNRPC_HANDLERS = [
        'myapp.rpc.CustomJSONRPCHandler',
        'myapp.rpc.CustomXMLRPCHandler',
    ]

Your custom handler must inherit from one of the base handler classes and override the necessary methods.

Multiple Entry Points
-------------------

You can define multiple RPC entry points in your URLs configuration, each with different handlers and settings:

.. code-block:: python

    # urls.py
    from django.urls import path
    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # JSON-RPC only endpoint
        path('api/jsonrpc/', RPCEntryPoint.as_view(
            handlers=['modernrpc.handlers.JSONRPCHandler'],
        )),

        # XML-RPC only endpoint
        path('api/xmlrpc/', RPCEntryPoint.as_view(
            handlers=['modernrpc.handlers.XMLRPCHandler'],
        )),

        # Both protocols (default)
        path('api/rpc/', RPCEntryPoint.as_view()),
    ]

Environment-specific Settings
---------------------------

You might want to use different settings in development and production environments:

.. code-block:: python

    # settings.py
    if DEBUG:
        # Development settings
        MODERNRPC_LOG_EXCEPTIONS = True
        MODERNRPC_DOC_FORMAT = 'rst'
    else:
        # Production settings
        MODERNRPC_LOG_EXCEPTIONS = False
        MODERNRPC_DOC_FORMAT = ''
