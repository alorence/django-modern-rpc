=================
Django-modern-rpc
=================

Overview
--------

Django-modern-rpc provides a simple solution to implement a remote procedure call (RPC) server as part of your Django
project. It supports all major Django and Python versions.

Project's main features are:

- Simple and pythonic API
- Python 2.7, 3.3, 3.4, 3.5 and 3.6
- Django 1.8, 1.9, 1.10 and 1.11
- XML-RPC_ and `JSON-RPC 2.0`_ support (JSON-RPC 1.0 not supported)
- HTTP Basic Auth support
- Custom authentication support
- Automatic protocol detection based on request's ``Content-Type`` header
- High-level error management based on exceptions
- Multiple entry points, with specific methods and protocol attached
- RPC Methods documentation generated automatically, based on docstrings
- System introspection methods:

  - system.listMethods()
  - system.methodSignature()
  - system.methodHelp()
  - system.multicall() (XML-RPC only, using specification from https://mirrors.talideon.com/articles/multicall.html)

.. _XML-RPC: http://xmlrpc.scripting.com/
.. _JSON-RPC 2.0: http://www.jsonrpc.org/specification

.. toctree::
   :maxdepth: 3
   :caption: Table of Contents

   quickstart
   1_standard_config/index
   2_advanced_features/index
   contribute
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
