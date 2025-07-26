Customize backends
==================

.. versionadded:: 2.0

Django-modern-rpc can use various backends to unserialize (parse an incoming RPC request) and serialize (transform
response data to correct RPC response) data.

The library provides multiple backends for both JSON-RPC and XML-RPC protocols, allowing you to choose the one that best fits your needs in terms of performance, dependencies, and features.

JSON-RPC Backends
----------------

builtin json module
^^^^^^^^^^^^^^^^^^
Uses Python's builtin json library. Can be used as both serializer and deserializer.

**PROS**
- No additional dependencies required
- Available in all Python installations
- Compatible with all Django versions

**CONS**
- May be slower than other JSON backends
- Limited customization options

simplejson
^^^^^^^^^^
Uses the third-party simplejson library. Can be used as both serializer and deserializer.

**PROS**
- Better performance than the builtin json module
- More customization options
- Better error messages
- Supports older Python versions

**CONS**
- Requires an additional dependency

orjson
^^^^^^
Uses the third-party orjson library. Can be used as both serializer and deserializer.

**PROS**
- Significantly faster than other JSON backends
- Written in Rust for high performance
- Better handling of Python data types
- Smaller output size

**CONS**
- Requires an additional dependency
- Rust compiler needed for installation from source

rapidjson
^^^^^^^^^
Uses the third-party python-rapidjson library. Can be used as both serializer and deserializer.

**PROS**
- Very fast JSON parsing and serialization
- Compliant with the JSON specification
- Supports custom encoders and decoders

**CONS**
- Requires an additional dependency
- May have compatibility issues with some Python objects

XML-RPC Backends
---------------

builtin xmlrpc module
^^^^^^^^^^^^^^^^^^^^
Uses Python's builtin xmlrpc library. Can be used as both serializer and deserializer.

**PROS**
- No additional dependencies required
- Available in all Python installations
- Compatible with all Django versions

**CONS**
- May be slower than other XML backends
- Limited customization options
- Potential security vulnerabilities (use with defusedxml)

xmltodict
^^^^^^^^^
Uses the third-party xmltodict library. Can be used as both serializer and deserializer.

**PROS**
- Converts XML to Python dictionaries and back
- More intuitive data structure for Python developers
- Better handling of complex XML structures
- Can be more efficient for certain operations

**CONS**
- Requires an additional dependency
- May have different behavior than the standard xmlrpc module

etree
^^^^^
Uses Python's ElementTree library (with defusedxml for security). Can be used as both serializer and deserializer.

**PROS**
- Efficient XML parsing
- Good balance of performance and memory usage
- Better security when used with defusedxml

**CONS**
- More complex API than other backends
- May require more code for custom handling

lxml
^^^^
Uses the third-party lxml library. Can be used as both serializer and deserializer.

**PROS**
- Very fast XML parsing and serialization
- Supports XPath for querying XML
- Extensive feature set for XML manipulation
- Compliant with XML standards

**CONS**
- Requires an additional dependency with C extensions
- More complex API than other backends

Configuring Backends
------------------

You can configure which backends to use in your Django settings:

.. code-block:: python

    # settings.py

    # For JSON-RPC
    MODERNRPC_JSON_DECODER = "json.decoder.JSONDecoder"  # Default
    MODERNRPC_JSON_ENCODER = "django.core.serializers.json.DjangoJSONEncoder"  # Default

    # For XML-RPC
    MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = True  # Default
    MODERNRPC_XMLRPC_ALLOW_NONE = True  # Default
    MODERNRPC_XMLRPC_DEFAULT_ENCODING = None  # Default

For more detailed configuration options, see the :doc:`settings` documentation.

Benchmarks
---------

Performance can vary significantly between backends. In general:

For JSON-RPC:
- orjson is typically the fastest
- rapidjson is also very fast
- simplejson is moderately fast
- builtin json is the slowest but most widely available

For XML-RPC:
- lxml is typically the fastest
- etree is moderately fast
- xmltodict can be faster for certain operations
- builtin xmlrpc is the slowest but most widely available

Future benchmarks will be included in pytest to check and compare performances of each backend.
See `django-modern-rpc#77 <https://github.com/alorence/django-modern-rpc/issues/77>`_ for updates.

Additional Backends
-----------------

It is planned to have additional backends provided in future versions.
See `django-modern-rpc#78 <https://github.com/alorence/django-modern-rpc/issues/78>`_ for updates.
