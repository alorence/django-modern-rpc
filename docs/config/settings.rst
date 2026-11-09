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

MODERNRPC_EXPOSE_INTERNAL_ERRORS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Control whether the message of unexpected exceptions is returned to the client. When ``False`` (default), any
exception which is not a subclass of ``RPCException`` (as well as serialization errors) is returned as a generic
``Internal error`` (code ``-32603``), and its details are logged on the server side. When ``True``, the original
exception message is returned to the client.

This setting can be overridden for a specific server with the ``expose_internal_errors`` argument of ``RpcServer``.
See :ref:`Internal errors` for details.

:Default:   ``False``

.. warning::
   Exception messages may contain implementation details (SQL errors, file paths, third-party API responses, etc.).
   Do not enable this setting in production.

MODERNRPC_MAX_BATCH_SIZE
^^^^^^^^^^^^^^^^^^^^^^^^

Maximum number of calls allowed in a single request: number of items in a JSON-RPC batch request, or number of calls
in an XML-RPC ``system.multicall``. A request exceeding this limit is rejected with an Invalid Request error
(``-32600``) and none of its calls is executed. Set to ``None`` to disable the limit.

This setting can be overridden for a specific server with the ``max_batch_size`` argument of ``RpcServer``.
See :ref:`Batch requests` and :ref:`Multicall`.

:Default:   ``100``

.. warning::
   Without limit, a small payload can trigger thousands of procedure executions. Only disable this limit if your
   server is not exposed to untrusted clients.

MODERNRPC_DOC_FORMAT
^^^^^^^^^^^^^^^^^^^^

Configure the format of the docstring used to document your RPC methods.

Possible values are:

- ``""`` (empty string): no processing, the docstring is returned as-is (with newlines converted to HTML paragraphs)
- ``"rst"`` (also ``"restructured"`` / ``"restructuredtext"``): parse docstrings as reStructuredText (requires ``docutils``)
- ``"md"`` (also ``"markdown"``): parse docstrings as Markdown (requires ``markdown``)

The value is case-insensitive.

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

List of handler classes used by default in ``RpcServer`` instances. If you have overridden a handler class, you may need
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
