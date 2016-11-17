===============
Tips and tricks
===============

Access the current request
--------------------------

If at some point, if you need to access the current request object from your RPC method, simply add ``**kwargs``
in the function arguments. The request, and some other variables will be passed through this dict to your function.

.. code:: python

    from modernrpc.settings import MODERNRPC_REQUEST_PARAM_NAME,
                                   MODERNRPC_PROTOCOL_PARAM_NAME,
                                   MODERNRPC_ENTRY_POINT_PARAM_NAME

    def content_type_printer(**kwargs):
        # The other available variables are:
        # protocol = kwargs.get(MODERNRPC_PROTOCOL_PARAM_NAME)
        # entry_point = kwargs.get(MODERNRPC_ENTRY_POINT_PARAM_NAME)

        # Get the current request
        request = kwargs.get(MODERNRPC_REQUEST_PARAM_NAME)
        # Return the content-type of the current request
        return request.META.get('Content-Type', '')
