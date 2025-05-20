Procedures documentation
========================

Django-modern-rpc processes the docstring attached to your RPC methods to provide rich information about your API.
This article explains how documentation is generated and can be customized in version 2.0.

Documentation generation
------------------------

In version 2.0, the automatic HTML documentation generation through entry points has been removed. However, the library
still processes docstrings to provide rich information about your procedures, which can be accessed programmatically.

Each ``ProcedureWrapper`` instance has properties to access documentation:

- ``raw_docstring``: The raw docstring text
- ``html_doc``: The docstring converted to HTML
- ``args_doc``: Documentation for each argument
- ``return_doc``: Documentation for the return value

You can use these properties to build your own documentation views or integrate with other documentation systems.

.. code-block:: python

    from myapp.rpc import server

    # Get all registered procedures
    procedures = server.procedures

    # Access documentation for a specific procedure
    add_procedure = procedures.get('add')
    if add_procedure:
        html_documentation = add_procedure.html_doc
        args_documentation = add_procedure.args_doc
        return_documentation = add_procedure.return_doc

Write documentation
-------------------

The documentation is generated directly from RPC methods' docstrings. In version 2.0, you can use Python type hints and docstring formats like reStructuredText or Markdown:

.. code-block:: python

    from myapp.rpc import server

    @server.register_procedure(context_target='ctx')
    def content_type_printer(ctx) -> str:
        """
        Inspect request to extract the Content-Type header if present.
        This method demonstrates how a RPC method can access the request object.

        :param ctx: Request context with access to the current request
        :return: The Content-Type string for incoming request
        """
        # Access the request from the context
        request = ctx.request

        # Return the content-type of the current request
        return request.content_type

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
