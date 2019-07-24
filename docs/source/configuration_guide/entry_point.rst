=========================
Entry point configuration
=========================

Django-modern-rpc provides a class to handle RPC calls called ``RPCEntryPoint``. This standard Django view
will return a valid response to any valid RPC call made via HTTP POST requests.

Basic declaration
=================

``RPCEntryPoint`` is a standard Django view, you can declare it in your project or app's ``urls.py``:

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other views

        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

As a result, all RPC requests made to ``http://yourwebsite/rpc/`` will be handled by the RPC entry point. Obviously,
you can decide to handle requests from a different URL by updating the ``regex`` argument of ``url()``. You can also
declare more entry points with different URLs.

Advanced entry point configuration
==================================

You can modify the behavior of the view by passing some arguments to ``as_view()``.

Limit entry point to JSON-RPC or XML-RPC only
---------------------------------------------

Using ``protocol`` parameter, you can make sure a given entry point will only handle JSON-RPC or XML-RPC requests. This
is useful, for example if you need to have different addresses to handle protocols.

.. code:: python

   from django.conf.urls import url

   from modernrpc.core import JSONRPC_PROTOCOL, XMLRPC_PROTOCOL
   from modernrpc.views import RPCEntryPoint

   urlpatterns = [
       url(r'^json-rpc/$', RPCEntryPoint.as_view(protocol=JSONRPC_PROTOCOL)),
       url(r'^xml-rpc/$', RPCEntryPoint.as_view(protocol=XMLRPC_PROTOCOL)),
   ]

.. _multiple_entry_points:

Declare multiple entry points
-----------------------------

Using ``entry_point`` parameter, you can declare different entry points. Later, you will be able to configure your RPC
methods to be available to one or more specific entry points.

.. code:: python

   from django.conf.urls import url

   from modernrpc.views import RPCEntryPoint

   urlpatterns = [
       url(r'^rpc/$', RPCEntryPoint.as_view(entry_point='apiV1')),
       url(r'^rpcV2/$', RPCEntryPoint.as_view(entry_point='apiV2')),
   ]

Class reference
===============

.. autoclass:: modernrpc.views.RPCEntryPoint
   :members:
