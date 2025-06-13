Customize backends
==================

.. versionadded:: 2.0

Django-modern-rpc can use various backends to unserialize (parse an incoming RPC request) and serialize (transform
response data to correct RPC response) data.

It is planned to have multiple backends provided in future versions.
See `django-modern-rpc#78 <https://github.com/alorence/django-modern-rpc/issues/78>`_ for updates.

JSON-RPC
--------

builtin json module
^^^^^^^^^^^^^^^^^^^
Uses Python builtin library. Can be used as both serializer and deserializer.

**PROS**
- no dependency required

**CONS**
- may be slower

simplejson
^^^^^^^^^^

Uses third party SimpleJSON library. Can be used as both serializer and deserializer.

**PROS**

- TBD

**CONS**

- requires an additional dependency

XML-RPC
-------

builtin xmlrpc module
^^^^^^^^^^^^^^^^^^^^^

Uses Python builtin library. Can be used as both serializer and deserializer.

**PROS**

- no dependency required

**CONS**

- may be slower

xmltodict
^^^^^^^^^

Uses third party xML2DICT library. Can be used as both serializer and deserializer.

**PROS**

- TBD

**CONS**

- requires an additional dependency

Benchmarks
----------

In the future, benchmarks will be included in pytest to check and compare performances of each backend.

See `django-modern-rpc#77 <https://github.com/alorence/django-modern-rpc/issues/77>`_
