===========
Quick start
===========

Start using django-modern-rpc in a minute, following these simple steps.

Installation
============

Use pip to install the package in your environment::

   pip install django-modern-rpc


Configuration
=============

Add the library to your Django applications, in your ``settings.py``:

.. code:: python

    INSTALLED_APPS = [
        #...
        'modernrpc',
        #...
    ]


Create an entry point
=====================

An entry point is the URL used by clients to call your RPC methods. Declare as follow:

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other views

        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

For more information on entry point declaration and configuration, please read :doc:`the full
documentation <basic_usage/entry_point_configuration>`.

Write and register your methods
===============================

Now, you must indicates to django-modern-rpc which methods in your code must be available via RPC calls. Use the
decorator ``@rpc_method`` to mark any python function as RPC method

.. code:: python

    # In myproject/rpc_app/rpc_methods.py
    from modernrpc.core import rpc_method

    @rpc_method
    def add(a, b):
        return a + b


Declare your RPC methods modules
================================

Django-modern-rpc will automatically register functions marked as RPC method. The only hint you have to provide is a
list of modules containg such methods. In your ``settings.py``:


.. code:: python

    MODERNRPC_METHODS_MODULES = [
        'rpc_app.rpc_methods'
    ]

That's all !
============

Your application is ready to receive XML-RPC or JSON-RPC call. The entry point URL is ``http://yourwebsite.com/rpc/``
but you can customize it to fit your needs.
