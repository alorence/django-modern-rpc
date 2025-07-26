Data types support
==================

When working with RPC protocols, it's important to understand how different data types are handled during serialization and deserialization. This document describes how specific types are handled in django-modern-rpc across different protocols and Python versions.

Protocol Type Systems
-------------------

JSON-RPC supported types are limited by the JSON type system described in `RFC 4627 <http://www.ietf.org/rfc/rfc4627.txt>`_.

XML-RPC specification contains explicit type information. As a result, more types are supported. They are described in the `XML-RPC specification <http://xmlrpc.scripting.com/spec.html>`_.

Since django-modern-rpc allows you to declare methods that can handle both protocols, this document describes how specific types are handled in RPC methods in all cases (JSON or XML-RPC transport with Python 3).

Basic types
-----------
The basic types are handled the same way with the 2 supported protocols. Those types are:

- bool
- int
- float
- string

As long as a RPC method arguments or return value is of one of the above types, the behavior is consistent across all protocols.

Lists and structures
-------------------
Both JSON-RPC and XML-RPC support *lists* and *structures*. Conversion is done as follows:

- Input data (RPC method argument)
   - *structure* is converted to Python ``dict``
   - *list* is converted to Python ``list``

- Output data (RPC method return type)
   - Python ``dict`` is converted to *structure*
   - Python ``list`` and ``tuple`` are converted to *list*

In other words, you can use these types without any issue; they work as you would expect.

Both *lists* and *structures* can contain any combinations of elements of types defined in this document. A *struct* can contain another *struct* or a *list*, etc.

null and NoneType
-----------------
By default, both JSON-RPC and XML-RPC handlers will be able to return ``None`` or to take a None value as argument.

The XML handler will convert such values to ``<nil/>`` special argument. Since this type is not part of the original specification, some XML-RPC clients may misunderstand this value. If you prefer to respect the original standard, simply define in your ``settings.py``:

.. code-block:: python

   MODERNRPC_XMLRPC_ALLOW_NONE = False

As a result, the XML handler will raise a ``TypeError`` when trying to serialize a response containing a ``None`` value.

Dates
-----

In XML-RPC
^^^^^^^^^^
XML-RPC transport defines a type to handle dates and date/times: ``dateTime.iso8601``. Conversion is done as follows:

- Input date (RPC method argument)
   - If ``settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = True`` (default), the date will be converted to ``datetime.datetime``
   - If ``settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = False``, the date will be converted to ``xmlrpc.client.DateTime``

- Output date (RPC method return type)
   - Any object of type ``datetime.datetime`` or ``xmlrpc.client.DateTime`` will be converted to ``dateTime.iso8601`` in XML response

In JSON-RPC
^^^^^^^^^^^
JSON transport has no specific support for dates; they are transmitted as strings formatted with ISO 8601 standard. The behavior of default encoder and decoder classes is:

- Input date (RPC method argument)
   - Dates are transmitted as standard strings. The decoder will NOT try to recognize dates to apply specific treatments.

- Output date (RPC method return type)
   - ``datetime.datetime`` objects will be automatically converted to string (format ISO 8601), so JSON-RPC clients will be able to handle it as usual. This behavior is due to the use of ``DjangoJSONEncoder`` as the default encoder.

If you need to customize the behavior of JSON encoder and/or decoder, you can specify another class in ``settings.py``:

.. code-block:: python

    MODERNRPC_JSON_DECODER = 'json.decoder.JSONDecoder'
    MODERNRPC_JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'

For more information about these and other settings, see the :doc:`settings` documentation.

Using helper to handle all cases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To simplify date handling in your RPC methods, django-modern-rpc defines a helper to convert any object type into a ``datetime.datetime`` instance:

.. code-block:: python

   from modernrpc.helpers import get_builtin_date

   @rpc_method
   def add_one_month(date):
       """Adds 31 days to the given date, and returns the result."""
       return get_builtin_date(date) + datetime.timedelta(days=31)

The ``get_builtin_date`` function handles various date formats and types, ensuring consistent behavior across protocols.

Binary data
----------

In XML-RPC
^^^^^^^^^^
XML-RPC supports binary data through the ``<base64>`` type. Python's ``bytes`` and ``bytearray`` objects are automatically encoded as base64 when returned from an RPC method.

When receiving binary data, it will be decoded from base64 and provided to your method as a ``bytes`` object.

In JSON-RPC
^^^^^^^^^^^
JSON does not have native support for binary data. By default, binary data is encoded as base64 and transmitted as a string. The ``DjangoJSONEncoder`` handles this conversion automatically for ``bytes`` and ``bytearray`` objects.

When receiving binary data, you'll need to decode it manually if it was encoded as base64:

.. code-block:: python

   import base64

   @rpc_method
   def process_binary_data(data_str):
       # Decode base64 string to binary
       binary_data = base64.b64decode(data_str)
       # Process binary data
       return result

Custom types
-----------

For custom Python types, you have several options:

1. Implement ``__str__`` or ``__repr__`` methods for simple string conversion
2. Convert objects to dictionaries before returning them
3. Use custom JSON encoders/decoders for JSON-RPC

Example with dictionary conversion:

.. code-block:: python

   class User:
       def __init__(self, name, email):
           self.name = name
           self.email = email

       def to_dict(self):
           return {
               'name': self.name,
               'email': self.email
           }

   @rpc_method
   def get_user(user_id):
       user = User.objects.get(id=user_id)
       return user.to_dict()  # Return as dictionary for RPC compatibility
