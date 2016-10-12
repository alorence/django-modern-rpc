=============
RPCEntryPoint
=============

Basic declaration
=================

The library provides a class to handle RPC calls. It is called ``RPCEntryPoint``. This is a standard Django View that
will return a valid response to any valid RPC call (POST requests).

``RPCEntryPoint`` is a standard Django view, you can declare it in your project or app's ``urls.py``:

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other views

        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

Advanced configuration
======================

You can modify the behavior of the view by passing some arguments to ``as_view()``.

Limit entry point to JSON-RPC or XML-RPC only
---------------------------------------------

Using ``protocol`` parameter, you can make sure a given entry point will only handle JSON-RPC or XML-RPC requests. This
is useful, for example if you need to have different addresses to handle protocols.

.. code:: python

   from django.conf.urls import url

   from modernrpc.handlers import JSONRPC, XMLRPC
   from modernrpc.views import RPCEntryPoint

   urlpatterns = [
       url(r'^json-rpc/$', RPCEntryPoint.as_view(protocol=JSONRPC)),
       url(r'^xml-rpc/$', RPCEntryPoint.as_view(protocol=XMLRPC)),
   ]

.. _multiple_entry_points:

Declare multiple entry points
-----------------------------

Using ``entry_point`` parameter, you can declare different entry points. Later, you will be able to configure your RPC
methods to be available to 1 or more specific entry points.

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
