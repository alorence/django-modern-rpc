===============
Tips and tricks
===============

Access to current request from RPC methods
------------------------------------------

If you need to access some environment from your RPC method, simply adds ``**kwargs`` in function parameters. When the
function will be executed, a dict will be passed as argument, providing the following information:

 - Current HTTP request, as proper Django HttpRequest instance
 - Current protocol (JSON-RPC or XML-RPC)
 - Current entry point name
 - Current handler instance

See the example to see how to access these values:

.. code:: python

    from modernrpc.core import REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY, HANDLER_KEY
    from modernrpc.core import rpc_method

    @rpc_method
    def content_type_printer(**kwargs):

        # Get the current request
        request = kwargs.get(REQUEST_KEY)

        # Other available objects are:
        # protocol = kwargs.get(PROTOCOL_KEY)
        # entry_point = kwargs.get(ENTRY_POINT_KEY)
        # handler = kwargs.get(HANDLER_KEY)

        # Return the content-type of the current request
        return request.META.get('Content-Type', '')


Enable logging
--------------

If you need to troubleshoot errors, you can enable logging capabilities. This will give you some information about
common issues (why incoming request is invalid, call to unregistered RPC method, etc.) or provide info about entry
point behavior.

To enable logging, set ``settings.MODERNRPC_ENABLE_LOGGING`` and configure ``settings.LOGGING`` to handle log messages
from ``modernrpc.core`` and ``modernrpc.views``. Here is a basic example of such a configuration:

.. code:: python

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

All information about logging configuration can be found in `official Django docs``.

.. _official Django docs: https://docs.djangoproject.com/en/dev/topics/logging/#configuring-logging