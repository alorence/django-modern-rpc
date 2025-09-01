Customize backends
==================

.. versionadded:: 2.0

Django-modern-rpc can be configured to use different backends to unserialize incoming RPC request and serialize
response data to correct RPC response. Using a custom backend may help to implement non-standard behavior (allowing
serialization of new types) or improve performances.

To check performance of any backend, django-modern-rpc provide a test suite that is automatically ran
on `GitHub Actions`_ for each commit.

.. _GitHub Actions: https://github.com/alorence/django-modern-rpc/actions/workflows/benchmarks.yml

JSON-RPC backends
-----------------

json (python builtin)
^^^^^^^^^^^^^^^^^^^^^
This this the most basic backend that depends on Python builtin `json` module. It is used by default for both
deserialization and serialization of JSON-RPC requests and responses. It have decent performances

**PROS**

- no dependency required

**CONS**

- may be slower

simplejson
^^^^^^^^^^

Uses third party `SimpleJSON <https://github.com/simplejson/simplejson>`_ library. Can be used for both serialization
and deserialization.

**PROS**

- Easier encoder customization

**CONS**

- requires an additional dependency
- slower than some other options (including builtin json)

To use it, `simplejson` must be installed in the current environment. An extra dependency can be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[simplejson]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[simplejson]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[simplejson]

orjson
^^^^^^

Uses third party `orjson <https://github.com/ijl/orjson>`_ library. Can be used as both serializer and deserializer.

**PROS**

- Extremely fast

**CONS**

- requires an additional dependency

To use it, `orjson` must be installed in the current environment. An extra dependency can be used for that:

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

**PROS**

- Very fast

**CONS**

- requires an additional dependency

To use it, `python-rapidjson` must be installed in the current environment. An extra dependency can be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[rapidjson]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[rapidjson]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[rapidjson]


XML-RPC backends
----------------

xmlrpc (python builtin)
^^^^^^^^^^^^^^^^^^^^^^^

This is the most basic backend that depends on Python’s builtin xmlrpc module. It is used by default for both
deserialization and serialization of XML-RPC requests and responses.

**PROS**

- no dependency required

**CONS**

- may be slower

xmltodict
^^^^^^^^^

Uses third-party `xmltodict <https://github.com/martinblech/xmltodict>`_ library. Can be used as both serializer and
deserializer.

To use it, ``xmltodict`` must be installed in the current environment. An extra dependency can be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[xmltodict]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[xmltodict]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[xmltodict]

**PROS**

- Provides more control over XML parsing and serialization

**CONS**

- requires an additional dependency

etree (xml.etree.ElementTree)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Uses Python’s standard library ``xml.etree.ElementTree`` (through defusedxml wrappers) to parse and build XML-RPC
messages. Can be used as both serializer and deserializer.

**PROS**

- no additional dependency required (stdlib)
- secure parsing via defusedxml protections enabled by default

**CONS**

- may be slower and less feature-rich than lxml for large or complex XML

lxml
^^^^

Uses third-party `lxml <https://lxml.de/>`_ library (``lxml.etree``). Can be used as both serializer and deserializer.

To use it, ``lxml`` must be installed in the current environment. An extra dependency can be used for that:

.. tab:: pip

   .. code-block:: bash

       pip install django-modern-rpc[lxml]

.. tab:: poetry

   .. code-block:: bash

       poetry add django-modern-rpc[lxml]

.. tab:: uv

   .. code-block:: bash

       uv add django-modern-rpc[lxml]

**PROS**

- very fast and robust XML processing
- richer XML feature set compared to stdlib etree

**CONS**

- requires an additional dependency
