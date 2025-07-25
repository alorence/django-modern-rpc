Security concerns
=================

Since django-modern-rpc uses builtin xmlrpc.client internally, it is vulnerable to various security issues related to
XML payloads parsing. To protect you project against these attacks, you can install the package `defusedxml` in your
environment.

Alternatively, you can install django-modern-rpc with an extra to setup all at once :

.. code-block:: bash

    pip install django-modern-rpc[defusedxml]

Once `defusedxml` can be imported, various method are automatically patched against multiple attacks vectors.

For more information, check the `defusedxml project's`_ README.

.. _defusedxml project's: https://github.com/tiran/defusedxml
