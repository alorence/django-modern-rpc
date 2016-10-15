=================
Django-modern-rpc
=================

Overview
--------

Django-modern-rpc provides a simple solution to implement a remote procedure call (RPC) server as part of your Django
project. It supports all major Django (from 1.8 to 1.10) and Python (2.7 to 3.5) versions.

Project's main features are:

- XML-RPC (as described on http://xmlrpc.scripting.com/) and JSON-RPC 2.0 (from http://www.jsonrpc.org/specification)
  support. Please note that JSON-RPC 1.0 is not supported.
- Automatic protocol detection based on the request's header ``Content-Type``
- Python 2.7, 3.3, 3.4 and 3.5
- Django 1.8, 1.9 and 1.10
- Usual error handled and reported to callers
- Multi entry points, with specific methods and protocol attached
- System introspection methods:

  - system.listMethods()
  - system.methodSignature()
  - system.methodHelp()

.. toctree::
   :maxdepth: 2
   :caption: Table of Contents

   quickstart
   rpc_view
   methods_registration
   configuration
   error_handling
   changelog
   contribute


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

