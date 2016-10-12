=============
Configuration
=============

In your project's settings, you can override some variable to customize behavior of django-modern-rpc.


JSON Serialization and deserialization
======================================

You can configure how JSON-RPC handler will serialize and unserialize data::

   JSONRPC_DEFAULT_DECODER = "json.decoder.JSONDecoder"
   JSONRPC_DEFAULT_ENCODER = "django.core.serializers.json.DjangoJSONEncoder"

Override if you want to use a different class to serialize your data into JSON. The default Django encoder is used by
default, it overrides the default python encoder to improve its behavior::

  JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.

