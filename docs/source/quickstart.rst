===========
Quick start
===========

Configuring django-modern-rpc is quick and simple. Follow that steps to be up and running in few minutes!

Installation and configuration
==============================

Use your preferred tool (pip, pipenv, pipsi, easy_install, requirements.txt file, etc.) to install package
``django-modern-rpc`` in your environment:

.. code:: bash

    pip install django-modern-rpc

Add ``modernrpc`` app to your Django applications, in ``settings.INSTALLED_APPS``:

.. code::

    # in project's settings.py
    INSTALLED_APPS = [
        ...
        'modernrpc',
    ]

Declare a RPC Entry Point in URLConf
====================================

The entry point is a standard Django view class which mainly handle RPC calls. Like other Django views, you have
to use ``django.conf.urls.url()`` to map URL pattern with this class. This can be done in your project's URLConf,
or in any app specific one.

.. code::

    # In myproject/my_app/urls.py
    from django.conf.urls import url

    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other url patterns
        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

Entry points behavior can be customized to your needs. Read :ref:`Entry point configuration` for full documentation.

Write and register your remote procedures
=========================================

Now, you have to write your remote procedures. These are global functions decorated with ``@rpc_method``.

.. code:: python

    # In myproject/rpc_app/rpc_methods.py
    from modernrpc.core import rpc_method

    @rpc_method
    def add(a, b):
        return a + b

``@rpc_method`` behavior can be customized to your needs. Read :ref:`Configure the registration <rpc_method_options>`
for full list of options.

Declare your RPC methods modules
================================

Django-modern-rpc will automatically register functions decorated with ``@rpc_method``, but needs a hint to locate them.
Declare ``settings.MODERNRPC_METHODS_MODULES`` to indicate all python modules where remote procedures are defined.

.. code:: python

    MODERNRPC_METHODS_MODULES = [
        'rpc_app.rpc_methods'
    ]

That's all !
============

Your application is ready to receive XML-RPC or JSON-RPC calls. The entry point URL is ``http://yourwebsite.com/rpc/``
but you can customize it to fit your needs.
