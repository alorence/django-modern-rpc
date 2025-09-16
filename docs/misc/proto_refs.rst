Protocols references
====================

XML-RPC
-------

XML-RPC protocol were first elaborated by `Dave Winer`_ (`ref <https://en.wikipedia.org/wiki/XML-RPC>`_ in 1998. The
most recent XML-RPC specification page used as reference by django-modern-rpc is http://xmlrpc.com/spec.md.

The original website describing and specifying the protocol (xmlrpc.scripting.com) now redirects to https://xmlrpc.com.
An archive of this website is available at http://1998.xmlrpc.com.

All these websites were created and maintained by Dave Winer, the creator of the protocol.

.. _Dave Winer: https://github.com/scripting

Introspection procedures
^^^^^^^^^^^^^^^^^^^^^^^^

XML-RPC initial specification does not provide anything to achieve introspection (list procedures, their signatures
and related documentation), but this was proposed in an `unofficial addendum <http://xmlrpc-c.sourceforge.net/introspection.html>`_.

System introspection procedures (`system.listMethods`, `system.methodHelp` and `system.methodSignature`) are now
widely implemented in various XML-RPC servers libraries.

Multicall
^^^^^^^^^

Multicall was first proposed by `Eric Kidd`_ on Jan. 2001. Since the original article is now gone from the internet, only
archived versions are currently available.

References

- https://web.archive.org/web/20060624230303/http://www.xmlrpc.com:80/discuss/msgReader$1208?mode=topic

.. _Eric Kidd: https://github.com/emk

Like 3 others, this system method is not part of the standard. But its behavior has been `well defined`_
by `Eric Kidd`_. It is now implemented most of the XML-RPC servers and supported by number of
clients (including `Python's ServerProxy`_).

This method can be used to make many RPC calls at once, by sending an array of RPC payload. The result is a list of
responses, with the result for each individual request, or a corresponding fault result.

It is available only to XML-RPC clients, since JSON-RPC protocol specify how to call multiple RPC methods
at once using batch request.

.. _well defined: https://mirrors.talideon.com/articles/multicall.html
.. _Python's ServerProxy: https://docs.python.org/3/library/xmlrpc.client.html#multicall-objects

Fault codes
^^^^^^^^^^^

XML-RPC initial specification does not define a list of common errors and related `faultCode`. In 2001, Dan Libby
tried to specify such fault codes as an extension of the standard. The original document is now only available from
Wayback Machine :
https://web.archive.org/web/20240416231938/https://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php

Here is a list of defined codes and corresponding error description

.. table:: Dan Libby's proposal for standardized error codes
   :widths: auto

   ======== ==============================
    -32700   parse error. not well formed
    -32701   parse error. unsupported encoding
    -32702   parse error. invalid character for encoding
    -32600   server error. invalid xml-rpc. not conforming to spec.
    -32601   server error. requested method not found
    -32602   server error. invalid method parameters
    -32603   server error. internal xml-rpc error
    -32500   application error
    -32400   system error
    -32300   transport error
   ======== ==============================


Other useful links
^^^^^^^^^^^^^^^^^^

- Eric Kidd's XML-RPC How To: https://tldp.org/HOWTO/XML-RPC-HOWTO/index.html

JSON-RPC
--------

JSON-RPC specification is more recent. The main documentation is available at https://www.jsonrpc.org/specification

The current official standard for JSON format is `RFC 8259`_.

.. _RFC 8259: https://datatracker.ietf.org/doc/html/rfc8259

Introspection procedures & multicall
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

XML-RPC introspection procedures (`system.listMethods`, `system.methodHelp` and `system.methodSignature`) are not
included in official JSON-RPC specification. But since they are perfectly compatible with JSON-RPC protocol, builtin
procedures defined in django-modern-rpc are automatically available through JSON-RPC calls.

However, since JSON-RPC spec explicitly define `Batch requests` as a method to call multiple procedures from a single
request, the builtin `system.multicall` is disabled when a server is called through JSON-RPC.

Batch requests
^^^^^^^^^^^^^^

django-modern-rpc fully support batch requests as defined in the spec. When a server exposes its async view, a batch
request will execute procedures concurently using ``asyncio.gather()``. When a server expose the sync view,
procedures are executed sequentially.

Error codes
^^^^^^^^^^^

JSON-RPC original specification define a list of officiel error codes based on the list created by Dan Libby as an
XMML-RPC extension. See https://www.jsonrpc.org/specification#error_object

.. table:: JSON-RPC standardized error codes
   :widths: 18 20 62

   =================  ===================  ==================================================================
    code               message              meaning
   =================  ===================  ==================================================================
    -32700             Parse error          Invalid JSON was received by the server. An error occurred on the
                                            server while parsing the JSON text.
    -32600             Invalid Request      The JSON sent is not a valid Request object.
    -32601             Method not found     The method does not exist / is not available.
    -32602             Invalid params       Invalid method parameter(s).
    -32603             Internal error       Internal JSON-RPC error.
    -32000 to -32099   Server error         Reserved for implementation-defined server-errors.
   =================  ===================  ==================================================================


Types support
-------------

Default types support
^^^^^^^^^^^^^^^^^^^^^

Most of the time, django-modern-rpc will serialize and deserialize all common scalar and non-scalar types.

.. table::
   :width: 100%

   ========================= ========= ========== ===================
    Data type                 XML-RPC   JSON-RPC   Python conversion
   ========================= ========= ========== ===================
    null / nil                ✓ (1)     ✓          None
    boolean                   ✓         ✓          bool
    integer                   ✓         ✓          int
    string                    ✓         ✓          str
    double                    ✓         ✓          float
    array                     ✓         ✓          list
    struct                    ✓         ✓          dict
    date / dateTime.iso8601   ✓ (2)     ✗ (2)      datetime.datetime
    base64                    ✓ (3)     ✗          bytes
   ========================= ========= ========== ===================

Specific cases
^^^^^^^^^^^^^^

null and NoneType (1)
*********************

In the original XML-RPC specification, there is no support for `null` values.
An `extension <https://web.archive.org/web/20050911054235/http://ontosys.com/xml-rpc/extensions.php>`_ has been
proposed in 2001 to add this type. It is currently fully supported by all backends.

See :ref:`XML-RPC backends` for detailed documentation of `null` support in each backend.

JSON-RPC backends will transparently convert `null` value to Python `None` and vice versa.

Date / Datetime (2)
*******************

XML-RPC spec defines the type `dateTime.iso8601` to handle dates and datetimes. The default behavior depends on
the configured backend.

See :ref:`XML-RPC backends` for detailed documentation of `dateTime.iso8601` support in each backend.

JSON-RPC backends have no specific support of dates. The default behavior of builtin backends is:

- **Deserialization (RPC method argument)**

  Dates are received as standard string. Unmarshaller will NOT try to recognize dates for high level conversion. You
  can use :any:`modernrpc.helpers.get_builtin_date` to easily retrieve a proper `datetime` instance in such case.

- **Serialization (RPC method return type)**

  `datetime.datetime`, `datetime.date` and `datetime.time` objects will be automatically converted to string (format
  ISO 8601). This is configured per backend, either using a custom JSONEncoder based on Django's
  `DjangoJSONEncoder <https://docs.djangoproject.com/en/5.2/topics/serialization/#djangojsonencoder>`_ or by defining
  a ``default`` callback used in serialization process.

See :ref:`JSON-RPC backends` for detailed documentation of `date` / `time` / `datetime` support in each backend.

base64 (3)
**********

.. todo:: Explain how base64 type is used to serialize and deserialize bytes data

Logging
-------

Internally, django-modern-rpc use Python logging system. While messages are usually hidden by default Django logging
configuration, you can easily show them if needed.

You only have to configure ``settings.LOGGING`` to handle log messages from ``modernrpc`` module.
Here is a basic example of such a configuration:

.. code-block:: python
   :caption: settings.py

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           # Your formatters configuration...
       },
       'handlers': {
           'console': {
               'level': 'DEBUG',
               'class': 'logging.StreamHandler',
           },
       },
       'loggers': {
           # your other loggers configuration
           'modernrpc': {
               'handlers': ['console'],
               'level': 'DEBUG',
               'propagate': True,
           },
       }
   }

All information about logging configuration can be found in `official Django docs`_.

.. _official Django docs: https://docs.djangoproject.com/en/dev/topics/logging/#configuring-logging
