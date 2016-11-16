=================
Django-modern-rpc
=================

Overview
--------

Django-modern-rpc provides a simple solution to implement a remote procedure call (RPC) server as part of your Django
project. It supports all major Django and Python versions.

Project's main features are:

- Simple and pythonic API
- Python 2.7, 3.3, 3.4 and 3.5
- Django 1.8, 1.9 and 1.10
- XML-RPC (as described on http://xmlrpc.scripting.com/) support
- JSON-RPC 2.0 (from http://www.jsonrpc.org/specification) support (JSON-RPC 1.0 is NOT supported)
- Automatic protocol detection based on the request's header ``Content-Type``
- Usual error handled and reported to callers
- Multiple entry points, with specific methods and protocol attached
- System introspection methods:

  - system.listMethods()
  - system.methodSignature()
  - system.methodHelp()

.. toctree::
   :maxdepth: 3
   :caption: Table of Contents

   quickstart
   basic_usage/index
   advanced/index
   contribute
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
