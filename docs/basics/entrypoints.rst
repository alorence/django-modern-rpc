Entrypoints configuration
=========================

Django-modern-rpc provides a class-based view ``modernrpc.views.RPCEntryPoint`` to handle remote procedure calls.

Usage
-----

``RPCEntryPoint`` is a standard Django view, you can declare it in your project or app's ``urls.py``:

.. code-block:: python
   :caption: urls.py

    from django.urls import path
    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other views
        path('rpc/', RPCEntryPoint.as_view()),
    ]

Then, all requests to ``http://yourwebsite/rpc/`` will be routed to the view. They will be inspected and
parsed to be interpreted as RPC call. The result of procedure call will be encapsulated into a response according
to the request's protocol (JSON-RPC or XML-RPC).

Advanced configuration
----------------------

You can modify the behavior of the entry point by passing arguments to ``as_view()``.

Restrict supported protocol
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``protocol`` parameter, you can make sure a given entry point will handle only JSON-RPC or XML-RPC requests.
This can be used to setup protocol-specific paths.

Default: ``protocol = Protocol.ALL``

.. code-block:: python
   :caption: urls.py

    from django.urls import path

    from modernrpc.core import Protocol
    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        path('json-rpc/', RPCEntryPoint.as_view(protocol=Protocol.JSON_RPC)),
        path('xml-rpc/', RPCEntryPoint.as_view(protocol=Protocol.XML_RPC)),
    ]

.. _multiple_entry_points:

Declare multiple entry points
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``entry_point`` parameter, you can declare different entry points. Later, you will be able to configure your RPC
methods to be available to one or more specific entry points (see :ref:`Procedure registration - entry
point <entry_point_specific_procedure>`)

Default: ``entry_point = ALL``

.. code-block:: python
   :caption: urls.py

    from django.urls import path

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
       path('rpc/', RPCEntryPoint.as_view(entry_point='apiV1')),
       path('rpcV2/', RPCEntryPoint.as_view(entry_point='apiV2')),
    ]

HTML documentation
^^^^^^^^^^^^^^^^^^

``RPCEntryPoint`` view can be configured to display HTML documentation of your procedures when it receive a GET request.
To enable the feature, simply set ``enable_doc = True`` in your view instance.

Default: ``enable_doc = False``

.. code-block:: python
   :caption: urls.py

    from django.urls import path

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ...
        path('rpc/', RPCEntryPoint.as_view(enable_doc=True)),
    ]

The view will return HTML documentation on GET requests and process remote procedure calls on POST requests.

If you want a documentation-only entry point, set ``enable_rpc = False`` on documentation entry point.

Default: ``enable_rpc = True``

.. code-block:: python
   :caption: urls.py

    urlpatterns = [
        # By default, RPCEntryPoint does NOT provide documentation but handle RPC requests
        path('rpc/', RPCEntryPoint.as_view()),

        # And you can configure it to display doc without handling RPC requests.
        path('rpc-doc/', RPCEntryPoint.as_view(enable_doc=True, enable_rpc=False)),
    ]

The complete documentation is available here :ref:`Procedures documentation`

Reference
---------

.. autoclass:: modernrpc.views.RPCEntryPoint
   :members:
