Configuration
=============

Write your first RPC method
---------------------------

Remotes procedures are simple Python functions decorated with ``@rpc_method``.

.. code:: python

    # In myproject/rpc_app/rpc_methods.py
    from modernrpc.core import rpc_method

    @rpc_method
    def add(a, b):
        return a + b

``@rpc_method`` behavior can be customized to your needs. Read :ref:`Configure the registration <rpc_method_options>`
for full list of options.

Declare your RPC methods modules
--------------------------------

Django-modern-rpc will automatically register functions decorated with ``@rpc_method``, but needs a hint to locate them.
Declare ``settings.MODERNRPC_METHODS_MODULES`` to indicate all python modules where remote procedures are defined.

.. code:: python

    MODERNRPC_METHODS_MODULES = [
        'rpc_app.rpc_methods'
    ]

Create an entry point
---------------------

The entrypoint is a special Django view which handle RPC calls. Like any other view, it has to
be declared in URLConf or any app specific ``urls.py``:

.. code::

    from django.conf.urls import url
    from modernrpc.views import RPCEntryPoint

    urlpatterns = [
        # ... other url patterns
        url(r'^rpc/', RPCEntryPoint.as_view()),
    ]

Entry points behavior can be customized to your needs. Read `Entrypoint configuration` (ref needed) for full documentation.
