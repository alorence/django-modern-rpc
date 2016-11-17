==================
Data types support
==================

JSON-RPC uses JSON to transport request and response. As a result, the supported types are limited by JSON type system,
described in http://www.ietf.org/rfc/rfc4627.txt.

XML-RPC transport contains explicit type information. As a consequence, more types are supported by this protocol.
Supported types are documented at http://xmlrpc.scripting.com/spec.html.

In addition, Python version used in your project may change how data types are handled. Since django-modern-rpc
let you declare methods that can handle both protocols, you should read this document to understand what you
should and shouldn't do with data in your methods.

Basic types
-----------

The basic types are handled the same way in all Python versions and with the 2 supported protocol.
Those types are:

- bool
- int
- float
- str

If a RPC method return one of these types or take it as argument, the behavior is the same in JSON-RPC and in XML-RPC,
no matter what version of Python you use in your project. You shouldn't face any issue when working with those types.

Date types
----------

In XML-RPC
^^^^^^^^^^

XML-RPC transport define a type to handle dates and date/times: ``dateTime.iso8601``. Conversion is done as follow:

 - Input date (RPC method argument)

   - If ``settings.MODERNRPC_XML_USE_BUILTIN_TYPES = True (default)``, the date will be converted to ``datetime.datetime``
   - If ``settings.MODERNRPC_XML_USE_BUILTIN_TYPES = False``, the date will be converted to ``xmlrpc.client.DateTime``
     (Python 3) or ``xmlrpclib.DateTime`` (Python 2)

 - Output date (RPC method return type)

   - Any object of type ``datetime.datetime`` or ``xmlrpclib.DateTime/xmlrpc.client.DateTime`` will be converted to
     ``dateTime.iso8601`` (in XML response)

In JSON-RPC
^^^^^^^^^^^

JSON transport has no specific support of dates, they are represented as string on format ISO 8601.
The behavior of default encoder and decoder classes is:

 - Input date (RPC method argument)

   - Dates are transmitted as standard string. Decoder will NOT try to recognize dates to apply specific treatments.

 - Output date (RPC method return type)

   - ``datetime.datetime`` objects will be automatically converted to string (format ISO 8601), so JSON-RPC clients
     will be able to handle it as usual. This behavior is due to the use of ``DjangoJSONEncoder`` as default encoder.

If you need to customize behavior of JSON encoder and/or decoder, you can specify another classes in ``settings.py``::

    MODERNRPC_JSON_DECODER = 'json.decoder.JSONDecoder'
    MODERNRPC_JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'

Using helper to handle all cases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As you probably noticed, when you receive a date value in your RPC method, the object can be of different types. To
make sure you can work with dates in a unified manner, django-modern-rpc defines a helper which help you to retrieve a
``datetime.datetime`` object from any date value:

.. autofunction:: modernrpc.helpers.get_builtin_date

Here is an usage example:

.. code:: python

   from modernrpc.helpers import get_builtin_date

   @rpc_method()
   def add_one_month(date):
       """Adds 31 days to the given date, and returns the result."""
       return get_builtin_date(date) + datetime.timedelta(days=31)

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