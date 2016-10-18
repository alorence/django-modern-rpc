=======================
Define your RPC methods
=======================

Any python global function can be :doc:`turned to be an RPC method<methods_registration>`. In that document,
we will just see how does such methods should be declared

Supported types
---------------

JSON-RPC uses JSON to transport request and response. As a result, the supported types are limited by JSON type system,
described in http://www.ietf.org/rfc/rfc4627.txt.

XML-RPC supports more types, since requests and response contains type information. Supported types are documented at
http://xmlrpc.scripting.com/spec.html.

The most basic python types are encoded and decoded from/to automatically. That means you can use them directly
in your methods, and returns it as results. These types are:

=================    ================    ==================
XML-RPC type         JSON-RPC type       Python type
=================    ================    ==================
boolean              boolean             bool
int                  int                 int
double               double              float
string               string              bytearray, str or unicode
struct               struct              dict
dateTime.iso8601     string              datetime*
base64               *Not supported*     Binary
=================    ================    ==================

DateTime support
----------------

In XML-RPC
^^^^^^^^^^
XML-RPC format for requests and responses contains type information. Thus, XML decoder and encoder classes

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

Access the current request
--------------------------

If at some point, you need to access the curren request object from your RPC method, you just need to add ``**kwargs``
in the function arguments. The request, and some other variables will be passed through this dict to your function.

.. code:: python

    from modernrpc.settings import MODERNRPC_REQUEST_PARAM_NAME,
                                   MODERNRPC_PROTOCOL_PARAM_NAME,
                                   MODERNRPC_ENTRY_POINT_PARAM_NAME

    def content_type_printer(**kwargs):
        # The other available variables are:
        # protocol = kwargs.get(MODERNRPC_PROTOCOL_PARAM_NAME)
        # entry_point = kwargs.get(MODERNRPC_ENTRY_POINT_PARAM_NAME)

        # Get the current request
        request = kwargs.get(MODERNRPC_REQUEST_PARAM_NAME)
        # Return the content-type of the current request
        return request.META.get('Content-Type', '')
