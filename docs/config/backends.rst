Backends
========

.. versionadded:: 2.0

Django-modern-rpc can be configured to use different backends to deserialize incoming RPC request and serialize
response data to correct RPC response. Using a custom backend may help to implement non-standard behavior (allowing
serialization of new types) or improve performances.

To check performance of any backend, django-modern-rpc provide a test suite that is automatically ran
on `GitHub Actions`_ for each commit.

.. _GitHub Actions: https://github.com/alorence/django-modern-rpc/actions/workflows/benchmarks.yml

XML-RPC backends
----------------

xmlrpc (python builtin)
^^^^^^^^^^^^^^^^^^^^^^^

This is the most basic backend that depends on Python’s builtin xmlrpc module. It is used by default for both
deserialization and serialization of XML-RPC requests and responses.

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` No additional dependency required (stdlib)
| :octicon:`thumbsup;1em;sd-mr-1` Secure parsing via defusedxml protections enabled by default

| :octicon:`thumbsdown;1em;sd-mr-1` Can fail to parse some requests, particularly when spaces are added around some
  some specific values, like booleans, strings or dates
| :octicon:`thumbsdown;1em;sd-mr-1` May be slower than other backends

| :octicon:`thumbsup;1em;sd-mr-1`/:octicon:`thumbsdown;1em;sd-mr-1` Some important rules of the spec are not strictly
  followed. For instance, when the root tag of an XML-RPC request is NOT ``methodCall``, the Unmarshaller parse it
  without raising any exception.


Configuration
*************

Deserializer configuration must be set in ``load_kwargs`` key.

- **use_datetime** and **use_builtin_types** are used to configure Unmarshaller to parse incoming request. See
  `the Python documentation <https://docs.python.org/3/library/xmlrpc.client.html#xmlrpc.client.loads>`_ for complete
  documentation. Both values are set to ``True`` by default.


.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_DESERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcBackend",
        "kwargs": {
            "load_kwargs": {"use_datetime": False, "use_builtin_types": False}
        }
    }

Serializer configuration must be set in ``dump_kwargs`` key.

- **allow_none** can be used to enable or disable `nil` / `None` value in serialization. See
  `the Python documentation <https://docs.python.org/3/library/xmlrpc.client.html#xmlrpc.client.dumps>`_ for complete
  documentation. It is set to ``True`` by default

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_SERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcBackend",
        "kwargs": {
            "dump_kwargs": {"allow_none": False}
        }
    }


etree (xml.etree.ElementTree)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Uses Python’s standard library ``xml.etree.ElementTree`` (through defusedxml wrappers) to parse and build XML-RPC
messages. Can be used as both serializer and deserializer.

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` no additional dependency required (stdlib)
| :octicon:`thumbsup;1em;sd-mr-1` secure parsing via defusedxml protections enabled by default
| :octicon:`thumbsdown;1em;sd-mr-1` may be slower and less feature-rich than lxml for large or complex XML

Configuration
*************

- **todo** ...


xmltodict
^^^^^^^^^

Uses third-party `xmltodict <https://github.com/martinblech/xmltodict>`_ library. Can be used as both serializer and
deserializer.

To use this backend, ``xmltodict`` must be installed in the current environment. An extra dependency can be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[xmltodict]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[xmltodict]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[xmltodict]

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` Provides more control over XML parsing and serialization
| :octicon:`thumbsdown;1em;sd-mr-1` requires an additional dependency

Configuration
*************

- **todo** ...

lxml
^^^^

Uses third-party `lxml <https://lxml.de/>`_ library (``lxml.etree``). Can be used as both serializer and deserializer.

To use this backend, ``lxml`` must be installed in the current environment. An extra dependency can be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[lxml]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[lxml]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[lxml]

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` very fast and robust XML processing
| :octicon:`thumbsup;1em;sd-mr-1` richer XML feature set compared to stdlib etree
| :octicon:`thumbsdown;1em;sd-mr-1` requires an additional dependency

Configuration
*************

- **todo** ...

JSON-RPC backends
-----------------

json (python builtin)
^^^^^^^^^^^^^^^^^^^^^
This this the most basic backend that depends on Python builtin `json` module. It is used by default for both
deserialization and serialization of JSON-RPC requests and responses. It have decent performances

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` no dependency required
| :octicon:`thumbsdown;1em;sd-mr-1` may be slower

Configuration
*************

- **todo** ...

simplejson
^^^^^^^^^^

Uses third party `SimpleJSON <https://github.com/simplejson/simplejson>`_ library. Can be used for both serialization
and deserialization.

To use this backend, `simplejson` must be installed in the current environment. An extra dependency can
be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[simplejson]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[simplejson]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[simplejson]

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` Easier encoder customization
| :octicon:`thumbsdown;1em;sd-mr-1` requires an additional dependency
| :octicon:`thumbsdown;1em;sd-mr-1` slower than some other options (including builtin json)

Configuration
*************

- **todo** ...

orjson
^^^^^^

Uses third party `orjson <https://github.com/ijl/orjson>`_ library. Can be used as both serializer and deserializer.

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` Extremely fast
| :octicon:`thumbsdown;1em;sd-mr-1` requires an additional dependency

Configuration
*************

- **todo** ...


To use this backend, `orjson` must be installed in the current environment. An extra dependency can be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[orjson]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[orjson]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[orjson]

rapidjson
^^^^^^^^^

Uses third party `python-rapidjson <https://github.com/python-rapidjson/python-rapidjson>`_ library. Can be used as
both serializer and deserializer.

To use this backend, `python-rapidjson` must be installed in the current environment. An extra dependency can be
used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[rapidjson]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[rapidjson]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[rapidjson]

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` Very fast
| :octicon:`thumbsdown;1em;sd-mr-1` requires an additional dependency

Configuration
*************

- **todo** ...

Helper functions
----------------

.. autofunction:: modernrpc.helpers.get_builtin_date
