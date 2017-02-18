===============
Tips and tricks
===============

Access the current request
--------------------------

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

    @pc_method
    def content_type_printer(**kwargs):

        # Get the current request
        request = kwargs.get(REQUEST_KEY)

        # Other available objects are:
        # protocol = kwargs.get(PROTOCOL_KEY)
        # entry_point = kwargs.get(ENTRY_POINT_KEY)
        # handler = kwargs.get(HANDLER_KEY)

        # Return the content-type of the current request
        return request.META.get('Content-Type', '')
