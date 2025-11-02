Backends
========

.. versionadded:: 2.0

Django-modern-rpc can be configured to use different backends to deserialize incoming RPC requests and serialize
response data into the correct RPC response format. Using a custom backend can help implement non-standard behavior
(for example, allowing serialization of additional types) or improve performance.

To compare backend performance, django-modern-rpc provides a benchmark test suite that is automatically run
on `GitHub Actions`_ for each commit.

.. _GitHub Actions: https://github.com/alorence/django-modern-rpc/actions/workflows/benchmarks.yml

Terminology
-----------

Deserializer
^^^^^^^^^^^^

In each backend, the Deserializer class parses the incoming request body (XML or JSON) using its underlying library
and converts it into a valid Python representation. When the body is not syntactically correct, the deserialization
process will usually raise an ``RPCParseError``.

The result will be passed to the Unmarshaller (see below).

Unmarshaller
^^^^^^^^^^^^

The Unmarshaller class takes a Python dictionary built from the incoming request body and extracts important
information, such as the procedure name to call and the provided arguments.

When the format (XML-RPC or JSON-RPC) of the parsed request is invalid, the Unmarshaller will usually raise an
``RPCInvalidRequest``.

Marshaller
^^^^^^^^^^

The Marshaller class builds a high-level object representing the result of a procedure call (either success or error).
This object is then passed to the Serializer, which converts it to a string representation ready to be returned in an
``HttpResponse`` instance.

When the procedure response contains invalid data, the Marshaller will usually raise an ``RPCMarshallingError``

Serializer
^^^^^^^^^^

The Serializer uses its underlying library to serialize the response built by the Marshaller into a valid
string representation.

When the serialization process fails, an ``RPCMarshallingError`` may be raised.


Configuration
-------------

For each protocol (XML-RPC, JSON-RPC), a different class can be configured for deserialization and serialization.

The default values are:

.. code-block:: python
   :caption: myproject/settings.py

   MODERNRPC_XML_DESERIALIZER = {
     "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer",
     "kwargs": {}
   }
   MODERNRPC_XML_SERIALIZER = {
     "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
     "kwargs": {}
   }
   MODERNRPC_JSON_DESERIALIZER = {
     "class": "modernrpc.jsonrpc.backends.json.PythonJsonDeserializer",
     "kwargs": {}
   }
   MODERNRPC_JSON_SERIALIZER = {
     "class": "modernrpc.jsonrpc.backends.json.PythonJsonSerializer",
     "kwargs": {}
   }

Each class can be configured using the ``kwargs`` dictionary. The valid parameters depend on the selected backend.
Some arguments are common across many backends, while others apply only to specific ones. See below for a detailed
explanation of each backend’s configuration.


Some backends may be configured to use a different Unmarshaller and/or Marshaller class. When this is possible, use
``unmarshaller_klass`` / ``unmarshaller_kwargs`` and ``marshaller_klass`` / ``marshaller_kwargs`` in ``kwargs``.


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
| :octicon:`thumbsup;1em;sd-mr-1` Has better performance than other backends for both serialization and deserialization

| :octicon:`thumbsdown;1em;sd-mr-1` Can fail to parse some requests, particularly when there are extra spaces around
  certain values such as booleans, strings, or dates

| :octicon:`thumbsup;1em;sd-mr-1`/:octicon:`thumbsdown;1em;sd-mr-1` The underlying xmlrpc library can be permissive and
  accept some non-standard formatting. However, this backend will raise ``RPCInvalidRequest`` if the method name cannot
  be determined (for example, when the root tag is not ``methodCall``).

Configuration
*************

Unmarshaller / Deserializer
...........................

- ``load_kwargs``: passed to ``xmlrpc.client.loads``. See the
  `xmlrpc.client.loads() <https://docs.python.org/3/library/xmlrpc.client.html#xmlrpc.client.loads>`_ documentation
  for the list of valid keyword arguments

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_DESERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer",
        "kwargs": {
            "load_kwargs": {"use_datetime": False, "use_builtin_types": False}
        }
    }

The Unmarshaller class cannot be changed or configured at the moment.

Marshaller / Serializer
.......................

- ``dump_kwargs``: passed to ``xmlrpc.client.dumps``. See the
  `xmlrpc.client.dumps() <https://docs.python.org/3/library/xmlrpc.client.html#xmlrpc.client.dumps>`_ documentation
  for the list of valid keywords arguments.

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_SERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
        "kwargs": {
            "dump_kwargs": {"allow_none": False}
        }
    }

The Marshaller class cannot be changed or configured at the moment.


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

Unmarshaller / Deserializer
...........................

- ``unmarshaller_klass``: dotted path to the Unmarshaller class. Defaults to
  ``modernrpc.xmlrpc.backends.marshalling.EtreeElementUnmarshaller``.
- ``unmarshaller_kwargs``: keyword arguments passed to the Unmarshaller. Supported option:

  - ``allow_none`` (default: ``True``): whether to allow parsing of ``<nil/>``/``None`` values.
- ``element_type_klass``: dotted path to the XML Element class used to specialize the generic
  unmarshaller. Defaults to ``xml.etree.ElementTree.Element``.
- ``load_kwargs``: passed to ``defusedxml.ElementTree.XML``. By default, ``forbid_dtd`` is set to ``True`` for safety.

Example:

.. code-block:: python
   :caption: myproject/settings.py

   MODERNRPC_XML_DESERIALIZER = {
       "class": "modernrpc.xmlrpc.backends.etree.EtreeDeserializer",
       "kwargs": {
           "unmarshaller_kwargs": {"allow_none": False},
           "element_type_klass": "xml.etree.ElementTree.Element",
           "load_kwargs": {"forbid_dtd": True},
       }
   }

Marshaller / Serializer
.......................

- ``marshaller_klass``: dotted path to the Marshaller class. Defaults to
  ``modernrpc.xmlrpc.backends.marshalling.EtreeElementMarshaller``.
- ``marshaller_kwargs``: keyword arguments passed to the Marshaller. Supported options:

  - ``allow_none`` (default: ``True``): whether to allow serialization of ``None`` values.
  - ``element_factory`` (default: ``xml.etree.ElementTree.Element``): the function used to build a new Element
  - ``sub_element_factory`` (default: ``xml.etree.ElementTree.SubElement``): the function used to build a new SubElement
- ``element_type_klass``: dotted path to the XML Element class used to specialize the generic
  marshaller. Defaults to ``xml.etree.ElementTree.Element``.
- ``dump_kwargs``: passed to ``defusedxml.ElementTree.tostring``.

Example:

.. code-block:: python
   :caption: myproject/settings.py

   MODERNRPC_XML_SERIALIZER = {
       "class": "modernrpc.xmlrpc.backends.etree.EtreeSerializer",
       "kwargs": {
           "marshaller_kwargs": {"allow_none": True},
           "element_type_klass": "xml.etree.ElementTree.Element",
           "dump_kwargs": {"short_empty_elements": False},
       }
   }


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

Unmarshaller / Deserializer
...........................

- ``unmarshaller_klass``: dotted path to the Unmarshaller class. Defaults to
  ``modernrpc.xmlrpc.backends.marshalling.EtreeElementUnmarshaller``.
- ``unmarshaller_kwargs``: keyword arguments passed to the Unmarshaller. Supported option:

  - ``allow_none`` (default: ``True``)
- ``element_type_klass``: dotted path to the XML element class used to specialize the generic
  marshaller/unmarshaller. Defaults to ``lxml.etree._Element``.
- ``load_parser_kwargs``: keyword arguments passed to ``lxml.etree.XMLParser``. Secure defaults are applied:
  ``resolve_entities=False``, ``no_network=True``, ``dtd_validation=False``, ``load_dtd=False``, ``huge_tree=False``.
- ``load_kwargs``: additional arguments forwarded to ``lxml.etree.fromstring`` (the constructed parser is injected by
  the backend).

Example:

.. code-block:: python
   :caption: myproject/settings.py

   MODERNRPC_XML_DESERIALIZER = {
       "class": "modernrpc.xmlrpc.backends.lxml.LxmlDeserializer",
       "kwargs": {
           "unmarshaller_kwargs": {"allow_none": True},
           "load_parser_kwargs": {"huge_tree": False},
       }
   }

Marshaller / Serializer
.......................

- ``marshaller_klass``: dotted path to the Marshaller class. Defaults to
  ``modernrpc.xmlrpc.backends.marshalling.EtreeElementMarshaller``.
- ``marshaller_kwargs``: keyword arguments passed to the Marshaller. Supported options:

  - ``allow_none`` (default: ``True``): whether to allow parsing of ``<nil/>``/``None`` values.
  - ``element_factory`` (default: ``lxml.etree.Element``): the function used to build a new Element
  - ``sub_element_factory`` (default: ``lxml.etree.SubElement``): the function used to build a new SubElement
- ``element_type_klass``: dotted path to the XML Element class used to specialize the generic
  marshaller. Defaults to ``lxml.etree._Element``.
- ``dump_kwargs``: passed to ``lxml.etree.tostring``.

Example:

.. code-block:: python
   :caption: myproject/settings.py

   MODERNRPC_XML_SERIALIZER = {
       "class": "modernrpc.xmlrpc.backends.lxml.LxmlSerializer",
       "kwargs": {
           "marshaller_kwargs": {"allow_none": True},
           "dump_kwargs": {"pretty_print": True},
       }
   }


xmltodict
^^^^^^^^^

Uses third-party `xmltodict <https://github.com/martinblech/xmltodict>`_ library. Can be used as both serializer and
deserializer.

To use this backend, ``xmltodict`` must be installed in the current environment. It can be done with the included
extra dependency ``xmltodict``:

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

Unmarshaller / Deserializer
...........................

- ``unmarshaller_klass``: dotted path to the Unmarshaller class. Defaults to
  ``modernrpc.xmlrpc.backends.xmltodict.Unmarshaller``.
- ``unmarshaller_kwargs``: keyword arguments passed to the Unmarshaller. Currently, default one doesn't support
  any argument
- ``load_kwargs``: passed to ``xmltodict.parse``. See the
  `xmltodict docs <https://xmltodict.readthedocs.io/en/stable/README/>`_.

Example:

.. code-block:: python
   :caption: myproject/settings.py

   MODERNRPC_XML_DESERIALIZER = {
       "class": "modernrpc.xmlrpc.backends.xmltodict.XmlToDictDeserializer",
       "kwargs": {
           "load_kwargs": {"disable_entities": False},
       }
   }

Note: For security reasons, this backend first parses XML with ``defusedxml.ElementTree`` before converting it with
``xmltodict``. Any XML parsing errors or security violations will be reported accordingly.

Marshaller / Serializer
.......................

- ``marshaller_klass``: dotted path to the Marshaller class. Defaults to
  ``modernrpc.xmlrpc.backends.xmltodict.Marshaller``.
- ``marshaller_kwargs``: keyword arguments passed to the Marshaller. Supported options:

  - ``allow_none`` (default: ``True``): whether to allow serialization of ``None`` values.
- ``dump_kwargs``: passed to ``xmltodict.unparse``. See the
  `xmltodict docs <https://xmltodict.readthedocs.io/en/stable/README/>`_.

Note: In this backend, the Marshaller/Unmarshaller classes are fixed and cannot be changed via settings.

Example:

.. code-block:: python
   :caption: myproject/settings.py

   MODERNRPC_XML_SERIALIZER = {
       "class": "modernrpc.xmlrpc.backends.xmltodict.XmlToDictSerializer",
       "kwargs": {
           "dump_kwargs": {"pretty": True, "indent": "  ", "short_empty_elements": True},
           "marshaller_kwargs": {"allow_none": False},
       }
   }


JSON-RPC backends
-----------------

Common Unmarshaller / Marshaller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Unlike XML-RPC backends, JSON-RPC ones are simpler. Basically, a JSON deserializer will convert a string payload into
a structured python data (list, dict, etc.). Then, most of the work will be handled by the Unmarshaller class to build
a valid ``JsonRpcRequest`` instance.

On the other hand, the Unmarshaller will convert a ``JsonRpcResult`` (success or error) to a valid python dict and
pass the result to the serializer to build the corresponding JSON payload as a string.

Currently, the default JSON-RPC Unmarshaller / Marshaller classes are shared by all backends.


Unmarshaller configuration
**************************

Supported kwargs:

- ``validate_version`` (Default: ``True``): whether to enforce check for ``"jsonrpc": "2.0"`` in the incoming request.


Marshaller configuration
************************

Common Marshaller does not support any argument for now.


json (python builtin)
^^^^^^^^^^^^^^^^^^^^^
This is the most basic backend that depends on Python’s built-in ``json`` module. It is used by default for both
deserialization and serialization of JSON-RPC requests and responses.

By default, this backend use common `Unmarshaller` and `Marshaller` classes. In addition, it is configured to use
``DjangoJSONEncoder`` when serializing data, allowing ``date``, ``time`` and ``datetime`` instances to be serialized
transparently.

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` no dependency required

| :octicon:`thumbsdown;1em;sd-mr-1` not the most performant backend available

Configuration
*************

Unmarshaller / Deserializer
...........................

- ``unmarshaller_klass``: dotted path to the Unmarshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Unmarshaller``.
- ``unmarshaller_kwargs``: see :ref:`Unmarshaller configuration`
- ``load_kwargs``: passed to ``json.loads``. See the
  `json.loads() <https://docs.python.org/fr/3/library/json.html#json.loads>`_ documentation
  for the list of valid keyword arguments

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DESERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.json.PythonJsonDeserializer",
        "kwargs": {
            "load_kwargs": {},
            "unmarshaller_klass": "modernrpc.jsonrpc.backends.marshalling.Unmarshaller",
            "unmarshaller_kwargs": {"validate_version": False},
        }
    }

Marshaller / Serializer
.......................

- ``marshaller_klass``: dotted path to the Marshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Marshaller``.
- ``marshaller_kwargs``: see :ref:`Marshaller configuration`
- ``dump_kwargs``: passed to ``json.dumps``. See the
  `json.dumps() <https://docs.python.org/fr/3/library/json.html#json.dumps>`_ documentation
  for the list of valid keywords arguments.

Note: By default, ``json.dumps`` encoder is overridden to use
`DjangoJSONEncoder <https://docs.djangoproject.com/fr/5.2/topics/serialization/#djangojsonencoder>`_
through the `cls` argument, primarily to allow serializing ``date``, ``time`` and ``datetime`` objects.

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_SERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.json.PythonJsonSerializer",
        "kwargs": {
            "marshaller_klass": "myproject.core.marshaller.CustomMarshaller",
            "marshaller_kwargs": {"config1": "foo"},
            "dump_kwargs": {"indent": 2, "sort_keys": False},
        }
    }


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

Unmarshaller / Deserializer
...........................

- ``unmarshaller_klass``: dotted path to the Unmarshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Unmarshaller``.
- ``unmarshaller_kwargs``: see :ref:`Unmarshaller configuration`
- ``load_kwargs``: passed to ``simplejson.loads``. See the
  `simplejson.loads() <https://simplejson.readthedocs.io/en/latest/#simplejson.loads>`_ documentation
  for the list of valid keyword arguments

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DESERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.simplejson.SimpleJsonDeserializer",
        "kwargs": {
            "load_kwargs": {"use_decimal": False, "allow_nan": False},
            "unmarshaller_klass": "modernrpc.jsonrpc.backends.marshalling.Unmarshaller",
            "unmarshaller_kwargs": {"validate_version": False},
        }
    }

Marshaller / Serializer
.......................

- ``marshaller_klass``: dotted path to the Marshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Marshaller``.
- ``marshaller_kwargs``: see :ref:`Marshaller configuration`
- ``dump_kwargs``: passed to ``simplejson.dumps``. See the
  `simplejson.dumps() <https://simplejson.readthedocs.io/en/latest/#simplejson.dumps>`_ documentation
  for the list of valid keywords arguments.

Note: By default, a custom ``default`` function created from Django's
`DjangoJSONEncoder <https://docs.djangoproject.com/en/5.2/topics/serialization/#djangojsonencoder>`_ ``default``
method is passed to ``simplejson.dumps``, primarily to allow serializing ``date``, ``time`` and ``datetime`` objects.


.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_SERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.simplejson.SimpleJsonSerializer",
        "kwargs": {
            "marshaller_klass": "myproject.core.marshaller.CustomMarshaller",
            "marshaller_kwargs": {"config1": "foo"},
            "dump_kwargs": {"indent": 2, "sort_keys": False},
        }
    }


orjson
^^^^^^

Uses third party `orjson <https://github.com/ijl/orjson>`_ library. Can be used as both serializer and deserializer.

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

Pros / Cons
***********

| :octicon:`thumbsup;1em;sd-mr-1` Extremely fast

| :octicon:`thumbsdown;1em;sd-mr-1` requires an additional dependency

Configuration
*************

Unmarshaller / Deserializer
...........................

- ``unmarshaller_klass``: dotted path to the Unmarshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Unmarshaller``.
- ``unmarshaller_kwargs``: see :ref:`Unmarshaller configuration`
- ``load_kwargs``: ignored for now. ``orjson.loads`` does not accept any additional keyword arguments

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DESERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.orjson.OrjsonDeserializer",
        "kwargs": {
            "unmarshaller_klass": "modernrpc.jsonrpc.backends.marshalling.Unmarshaller",
            "unmarshaller_kwargs": {"validate_version": False},
        }
    }

Marshaller / Serializer
.......................

- ``marshaller_klass``: dotted path to the Marshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Marshaller``.
- ``marshaller_kwargs``: see :ref:`Marshaller configuration`
- ``dump_kwargs``: passed to ``orjson.dumps``. See the
  `orjson.dumps() <https://github.com/ijl/orjson?tab=readme-ov-file#serialize>`_ documentation
  for the list of valid keywords arguments.

Note: By default, since orjson is already able to serialize ``date`` and ``time`` objects, no particular encoder
customization is performed by django-modern-rpc.

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_SERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.orjson.OrjsonSerializer",
        "kwargs": {
            "dump_kwargs": {},
        }
    }


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

| :octicon:`thumbsup;1em;sd-mr-1` Pretty fast

| :octicon:`thumbsdown;1em;sd-mr-1` requires an additional dependency

Configuration
*************

Unmarshaller / Deserializer
...........................

- ``unmarshaller_klass``: dotted path to the Unmarshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Unmarshaller``.
- ``unmarshaller_kwargs``: see :ref:`Unmarshaller configuration`
- ``load_kwargs``: passed to ``rapidjson.loads``. See the
  `rapidjson.loads() <https://python-rapidjson.readthedocs.io/en/latest/loads.html>`_ documentation
  for the list of valid keyword arguments

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DESERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.rapidjson.RapidJsonDeserializer",
        "kwargs": {
            "load_kwargs": {},
            "unmarshaller_klass": "modernrpc.jsonrpc.backends.marshalling.Unmarshaller",
            "unmarshaller_kwargs": {"validate_version": False},
        }
    }

Marshaller / Serializer
.......................

- ``marshaller_klass``: dotted path to the Marshaller class. Defaults to
  ``modernrpc.jsonrpc.backends.marshalling.Marshaller``.
- ``marshaller_kwargs``: see :ref:`Marshaller configuration`
- ``dump_kwargs``: passed to ``rapidjson.dumps``. See the
  `rapidjson.dumps() <https://python-rapidjson.readthedocs.io/en/latest/dumps.html>`_ documentation
  for the list of valid keywords arguments.

Note: By default, date & time handling is set to `ISO-8601` via the ``datetime_mode`` argument
(``rapidjson.DM_ISO8601``) to help serializing ``date``, ``time`` and ``datetime`` objects.

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_SERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.rapidjson.RapidJsonSerializer",
        "kwargs": {
            "dump_kwargs": {"indent": 2, "sort_keys": True},
        }
    }


Helper functions
----------------

.. autofunction:: modernrpc.helpers.get_builtin_date
