Settings
========

This page lists all settings that can be used to customize django-modern-rpc's behavior. Set them inside your
project's ``settings.py``.

Global settings
---------------

MODERNRPC_DEFAULT_ENCODING
^^^^^^^^^^^^^^^^^^^^^^^^^^

Default encoding used to parse incoming requests when no charset is set in request headers.

:Default:   ``utf-8``

MODERNRPC_DOC_FORMAT
^^^^^^^^^^^^^^^^^^^^

Configure the format of the docstring used to document your RPC methods.
Possible values are: ``""`` (empty string), ``rst`` or ``markdown``.

:Default:   ``""`` (Empty string)

.. note::
   The corresponding package is not automatically installed. You have to ensure library `markdown` or `docutils` is
   installed in your environment if set to a non-empty value.

MODERNRPC_XMLRPC_ASYNC_MULTICALL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When set to ``True``, the ``system.multicall`` XML-RPC method will use an asynchronous implementation that
executes procedures concurrently using ``asyncio.gather()``. When ``False`` (default), procedures in a multicall
are executed sequentially.

:Default:   ``False``

MODERNRPC_HANDLERS
^^^^^^^^^^^^^^^^^^

List of handler classes used by default in ``RpcServer`` instances. If you overridden a handler class, you may need
to specify its dotted path here to use it automatically.

:Default:   ``["modernrpc.jsonrpc.handler.JsonRpcHandler", "modernrpc.xmlrpc.handler.XmlRpcHandler"]``


Backends customization
----------------------

Each protocol (XML-RPC & JSON-RPC) can be configured with a specific backend for both deserialization (parsing of
incoming request) and serialization (dumping outgoing response).

For each setting, a dict is defined with ``class`` and ``kwargs`` keys to set the dotted path of the class to
instantiate and a dictionary passed to the class when instantiating. Valid `kwargs` depend on the selected `class`.
Refer to :ref:`Backends` to get a list of all valid arguments for each backend.

MODERNRPC_XML_DESERIALIZER
^^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   ``{"class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer", "kwargs": {}}``

MODERNRPC_XML_SERIALIZER
^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   ``{"class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer", "kwargs": {}}``

MODERNRPC_JSON_DESERIALIZER
^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   ``{"class": "modernrpc.jsonrpc.backends.json.PythonJsonDeserializer", "kwargs": {}}``

MODERNRPC_JSON_SERIALIZER
^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   ``{"class": "modernrpc.jsonrpc.backends.json.PythonJsonSerializer", "kwargs": {}}``
