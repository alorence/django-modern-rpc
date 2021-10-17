Data types support
==================
JSON transport supported types are limited by JSON type system described in http://www.ietf.org/rfc/rfc4627.txt.

XML-RPC specification contains explicit type information. As a result, more types are supported. They are described
in http://xmlrpc.scripting.com/spec.html.

In addition, Python version used in your project may change how data types are transmitted. Since django-modern-rpc
allows you to declare methods that can handle both protocols, this document describes how specific types are handled
in RPC methods in all cases (JSON or XML-RPC transport with Python 2 or Python 3).

Basic types
-----------
The basic types are handled the same way with the 2 supported protocols. Those types are:

- bool
- int
- float
- string

As long as a RPC method arguments or return value is of one of the above types, the behavior is consistent across all
Python version and protocols.

List and structures
-------------------
Both JSON-RPC and XML-RPC supports *lists* and *structures*. Conversion is done as follow:

 - Input data (RPC method argument)

   - *structure* is converted to Python ``dict``
   - *list* is converted to Python ``list``

 - Output data (RPC method return type)

   - Python ``dict`` is converted to *structure*
   - Python ``list`` and ``tuple`` is converted to *list*

In other words, you can use those types without any issue, it works as you expect it.

Both *lists* and *structures* can contains any combinations of elements of types defined in this documents. A *struct*
can contain another *struct* or a *list*, etc.

null and NoneType
-----------------
By default, both JSON-RPC and XML-RPC handlers will be able to return ``None`` or to take a None value as argument.
The XML handler will convert such values to ``<nil/>`` special argument. Since this type is not part of the original
specification, some XML-RPC clients may misunderstand this value. If you prefer respect the original standard, simply
define in your ``settings.py``::

   MODERNRPC_XMLRPC_ALLOW_NONE = False

As a result, the XML handler will raise a ``TypeError`` when trying to serialize a response containing a ``None`` value.

Dates
-----

In XML-RPC
^^^^^^^^^^
XML-RPC transport defines a type to handle dates and date/times: ``dateTime.iso8601``. Conversion is done as follow:

 - Input date (RPC method argument)

   - If ``settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = True (default)``, the date will be converted to
     ``datetime.datetime``
   - If ``settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = False``, the date will be converted to
     ``xmlrpc.client.DateTime`` (Python 3) or ``xmlrpclib.DateTime`` (Python 2)

 - Output date (RPC method return type)

   - Any object of type ``datetime.datetime``, ``xmlrpclib.DateTime`` or ``xmlrpc.client.DateTime`` will
     be converted to ``dateTime.iso8601`` in XML response

In JSON-RPC
^^^^^^^^^^^
JSON transport has no specific support of dates, they are transmitted as string formatted with ISO 8601 standard.
The behavior of default encoder and decoder classes is:

 - Input date (RPC method argument)

   - Dates are transmitted as standard string. Decoder will NOT try to recognize dates to apply specific treatments.
     Use

 - Output date (RPC method return type)

   - ``datetime.datetime`` objects will be automatically converted to string (format ISO 8601), so JSON-RPC clients
     will be able to handle it as usual. This behavior is due to the use of ``DjangoJSONEncoder`` as default encoder.

If you need to customize behavior of JSON encoder and/or decoder, you can specify another classes in ``settings.py``::

    MODERNRPC_JSON_DECODER = 'json.decoder.JSONDecoder'
    MODERNRPC_JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'

Using helper to handle all cases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To simplify date handling in your RPC methods, django-modern-rpc defines a helper to convert any object type into a
``datetime.datetime`` instance:

.. autofunction:: modernrpc.helpers.get_builtin_date

Here is an usage example:

.. code:: python

   from modernrpc.helpers import get_builtin_date

   @rpc_method()
   def add_one_month(date):
       """Adds 31 days to the given date, and returns the result."""
       return get_builtin_date(date) + datetime.timedelta(days=31)
