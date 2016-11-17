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

If a RPC method return one of these types or take it as argument, the behavior is the same in JSON-RPC and in XML-RPC,
no matter what version of Python you use in your project. You shouldn't face any issue when working with those types.

String types
------------

Both JSON-RPC and XML-RPC are able to transport strings.

In general,

Date types
----------

In XML-RPC
^^^^^^^^^^

TBD

In JSON-RPC
^^^^^^^^^^^

JSON transport has no specific support of dates, they are represented as string on format ISO 8601.
The behavior of default encoder and decoder classes is:

- Decoder will not try to guess each string to convert it as a date. Dates strings are transmitted as-it. Dates in RPC
  method arguments can be converted to datetime object using a helper. See below
- Encoder will convert any datetime object to a string using the format ISO 8601. This ensure all common dates will be
  represented with the same format

Please note you can use another classes. To do so, overrides the default values in settings::

    MODERNRPC_JSON_DECODER = 'json.decoder.JSONDecoder'
    MODERNRPC_JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'

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

TBD
