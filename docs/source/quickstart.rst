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
        ...
        'modernrpc',
    ]

Create an entry point
=====================

An entry point is the URL used by clients to call your RPC methods. Declare it as follow:

.. code:: python

    # In myproject/rpc_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other views

        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

Entry points behavior can be customized with some arguments. Read the page :ref:`Entry point configuration`
for more information.

Write and register your methods
===============================

In the next step, you will declare which global functions should be available for remote calls. Use ``@rpc_method``
decorator to simply indicates those methods.

.. code:: python

    # In myproject/rpc_app/rpc_methods.py
    from modernrpc.core import rpc_method

    @rpc_method
    def add(a, b):
        return a + b

``@rpc_method`` behavior can be customized with some arguments. Read the page :ref:`Configure the registration
<rpc_method_options>` for more information.

Declare your RPC methods modules
================================

Django-modern-rpc will automatically register functions decorated with ``@rpc_method``, but needs a hint to locate them.
Declare ``MODERNRPC_METHODS_MODULES`` in your settings to indicate one or more python module where your RPC methods
are defined.

.. code:: python

    MODERNRPC_METHODS_MODULES = [
        'rpc_app.rpc_methods'
    ]

That's all !
============

Your application is ready to receive XML-RPC or JSON-RPC calls. The entry point URL is ``http://yourwebsite.com/rpc/``
but you can customize it to fit your needs.
