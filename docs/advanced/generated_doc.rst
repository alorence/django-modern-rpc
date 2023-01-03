Procedures documentation
========================

Django-modern-rpc can optionally process the docstring attached to your RPC methods and display it in a web page.
This article will explain how generated documentation can bu used and customized.

Enable documentation
--------------------
RPCEntryPoint class can be configured to provide HTML documentation of your RPC methods.
To enable the feature, simply set ``enable_doc = True`` in your view instance

.. code-block:: python

    urlpatterns = [

        # Configure the RPCEntryPoint directly by passing some arguments to as_view() method
        path('rpc/', RPCEntryPoint.as_view(enable_doc=True)),
    ]

If you prefer provide documentation on a different URL than the one used to handle RPC requests, you just need to
specify two different URLConf.

.. code-block:: python

    urlpatterns = [

        # By default, RPCEntryPoint does NOT provide documentation but handle RPC requests
        path('rpc/', RPCEntryPoint.as_view()),

        # And you can configure it to display doc without handling RPC requests.
        path('rpc-doc/', RPCEntryPoint.as_view(enable_doc=True, enable_rpc=False)),
    ]

Customize rendering
-------------------

You can customize the documentation page by setting your own template. ``RPCEntryPoint`` inherits
``django.views.generic.base.TemplateView``, so you have to set view's ``template_name`` attribute:

.. code-block:: python

    urlpatterns = [
        # RPCEntryPoint can be configured with arguments passed to as_view()
        path(
          'rpc/',
          RPCEntryPoint.as_view(
            enable_doc=True,
            template_name='my_app/my_custom_doc_template.html'
          )
        ),
    ]

In the template, you will get a list of ``modernrpc.core.RPCMethod`` instance (one per registered RPC method). Each
instance of this class has some methods and properties to retrieve documentation.

By default, documentation will be rendered using HTML5 vanilla tags with default classes and ids.

.. versionchanged:: 1.0.0
   In previous releases, the default template was based on Bootstrap 4 with collapse components and accordion widgets.
   To use this BS4 template, simply set  ```template_name='modernrpc/bootstrap4/doc_index.html'``` when instantiating
   the view.

Write documentation
-------------------

The documentation is generated directly from RPC methods docstring

.. code-block:: python

    @rpc_method(name="util.printContentType")
    def content_type_printer(**kwargs):
        """
        Inspect request to extract the Content-Type header if present.
        This method demonstrates how a RPC method can access the request object.
        :param kwargs: Dict with current request, protocol and entry_point information.
        :return: The Content-Type string for incoming request
        """
        # The other available variables are:
        # protocol = kwargs.get(MODERNRPC_PROTOCOL_PARAM_NAME)
        # entry_point = kwargs.get(MODERNRPC_ENTRY_POINT_PARAM_NAME)

        # Get the current request
        request = kwargs.get(REQUEST_KEY)
        # Return the content-type of the current request
        return request.META.get('Content-Type', '')

If you want to use `Markdown` or `reStructuredText` syntax in your RPC method documentation, you have to install the
corresponding package in you environment.

.. code-block:: bash

    pip install Markdown

or

.. code-block:: bash

    pip install docutils

Then, set ``settings.MODERNRPC_DOC_FORMAT`` to indicate which parser must be used to process your docstrings

.. code-block:: python

    # In settings.py
    MODERNRPC_DOC_FORMAT = 'markdown'

or

.. code-block:: python

    # In settings.py
    MODERNRPC_DOC_FORMAT = 'rst'


.. versionadded:: 1.0.0

   Typehints are now supported to generate arguments and return type in documentation
