Protocols specifications
========================

XML-RPC
-------

The most recent XML-RPC specification page used as reference for django-modern-rpc development
is http://xmlrpc.com/spec.md. It is part of `xmlrpc.com`_, a website created by `Dave Winer`_ in 2019 to
propose updated tools around XML-RPC standard.

The original website (xmlrpc.scripting.com) has also been archived with a new URL: `1998.xmlrpc.com`_

.. _Dave Winer: https://github.com/scripting
.. _xmlrpc.com: http://xmlrpc.com
.. _1998.xmlrpc.com: http://1998.xmlrpc.com

Multicall
^^^^^^^^^

Multicall was first proposed by Eric Kidd on 2001-01. Since the original article is now gone from the internet, it has
been archived at https://mirrors.talideon.com/articles/multicall.html

Other useful links
^^^^^^^^^^^^^^^^^^

- Eric Kidd's XML-RPC How To: https://tldp.org/HOWTO/XML-RPC-HOWTO/index.html

JSON-RPC
--------

Since JSON-RPC specification is more recent, available documentation is easier to find. The main specification is
available at https://www.jsonrpc.org/specification

The current official standard for JSON format is `RFC 8259`_.

.. _RFC 8259: https://datatracker.ietf.org/doc/html/rfc8259

Types support
-------------

Most of the time, django-modern-rpc will serialize and unserialize

.. table::
   :width: 100%

   ================ ========== ========== ===================
    RPC Data type    XML-RPC    JSON-RPC   Python conversion
   ================ ========== ========== ===================
    null             ✓ (1)      ✓          None
    string           ✓          ✓          str
    int              ✓          ✓          int
    float            ✓          ✓          float
    boolean          ✓          ✓          bool
    array            ✓          ✓          list
    struct           ✓          ✓          dict
    date             ✓          ✗ (2)      See (2)
    bas64            ✓ (3)      N/A        See (3)
   ================ ========== ========== ===================

**(1) null and NoneType**

By default, both JSON-RPC and XML-RPC handlers can serialize None and deserialize null value. The XML handler will
convert such values to `<nil/>` special argument, JSON one will convert to JSON null.

But some old XML-RPC clients may misunderstand the `<nil/>` value. If needed, you can disable its support by setting
:ref:`MODERNRPC_XMLRPC_ALLOW_NONE` to `False`. The XML-RPC marshaller will raise an exception on None serialization
or `<nil/>` deserialization.

**(2) Date types**

JSON transport has no specific support of dates, they are transmitted as string formatted with ISO 8601 standard.
The behavior of default encoder and decoder classes is:

- Input date (RPC method argument)

  * Dates are transmitted as standard string. Decoder will NOT try to recognize dates to apply specific treatment

- Output date (RPC method return type)

  * ``datetime.datetime`` objects will be automatically converted to string (format ISO 8601), so JSON-RPC clients
    will be able to handle it as usual. This behavior is due to the use of ``DjangoJSONEncoder`` as default encoder.

If you need to customize behavior of JSON encoder and/or decoder, you can specify another classes in ``settings.py``::

    MODERNRPC_JSON_DECODER = 'json.decoder.JSONDecoder'
    MODERNRPC_JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'

XML-RPC transport defines a type to handle dates and date/times: ``dateTime.iso8601``. Conversion is done as follow:

- Input date (RPC method argument)

  * If ``settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = True (default)``, the date will be converted to
    ``datetime.datetime``
  * If ``settings.MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = False``, the date will be converted to
    ``xmlrpc.client.DateTime`` (Python 3) or ``xmlrpclib.DateTime`` (Python 2)

- Output date (RPC method return type)

  * Any object of type ``datetime.datetime``, ``xmlrpclib.DateTime`` or ``xmlrpc.client.DateTime`` will
    be converted to ``dateTime.iso8601`` in XML response

To simplify dates handling in your procedures, you can use `get_builtin_date()` helper to convert any input into
a buildin `datetime.datetime`.

.. autofunction:: modernrpc.helpers.get_builtin_date

**base64**

base64 is not specifically supported, but you should be able to serialize and unserialize base64 encoded data as string.

Logging
-------

Internally, django-modern-rpc use Python logging system. While messages are usually hidden by default Django logging
configuration, you can easily show them if needed.

You only have to configure ``settings.LOGGING`` to handle log messages from ``modernrpc`` module.
Here is a basic example of such a configuration:

.. code-block:: python
   :caption: settings.py

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            # Your formatters configuration...
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            # your other loggers configuration
            'modernrpc': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }

All information about logging configuration can be found in `official Django docs`_.

.. _official Django docs: https://docs.djangoproject.com/en/dev/topics/logging/#configuring-logging

.. note::
   Logging configuration is optional. If not configured, the errors will still be visible in logs unless you set
   :ref:`MODERNRPC_LOG_EXCEPTIONS` to `False`. See :ref:`Logging errors`


.. _sys-procedures-ref:

Introspection procedures
------------------------

System introspection methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

System introspection methods (listMethods, methodHelp, methodSignature) were not part of the original standard but were
proposed in an unofficial addendum. Here is a list of references pages:

- http://xmlrpc-c.sourceforge.net/introspection.html
- http://scripts.incutio.com/xmlrpc/introspection.html (dead)
- http://xmlrpc.usefulinc.com/doc/reserved.html) (dead)

---

XML-RPC_ specification doesn't provide default methods to achieve introspection tasks, but some people proposed
a standard for such methods. The `original document`_ is now offline, but has been retrieved from Google
cache and is now hosted here_.

.. _XML-RPC: http://xmlrpc.scripting.com/spec.html
.. _original document: http://xmlrpc.usefulinc.com/doc/reserved.html
.. _here: http://scripts.incutio.com/xmlrpc/introspection.html

system.listMethods
^^^^^^^^^^^^^^^^^^
Return a list of all methods available.

system.methodSignature
^^^^^^^^^^^^^^^^^^^^^^
Return the signature of a specific method

system.methodHelp
^^^^^^^^^^^^^^^^^
Return the documentation for a specific method.

system.multicall
^^^^^^^^^^^^^^^^

Like 3 others, this system method is not part of the standard. But its behavior has been `well defined`_
by `Eric Kidd`_. It is now implemented most of the XML-RPC servers and supported by number of
clients (including `Python's ServerProxy`_).

This method can be used to make many RPC calls at once, by sending an array of RPC payload. The result is a list of
responses, with the result for each individual request, or a corresponding fault result.

It is available only to XML-RPC clients, since JSON-RPC protocol specify how to call multiple RPC methods
at once using batch request.

.. _well defined: https://mirrors.talideon.com/articles/multicall.html
.. _Python's ServerProxy: https://docs.python.org/3/library/xmlrpc.client.html#multicall-objects
.. _Eric Kidd: https://github.com/emk
