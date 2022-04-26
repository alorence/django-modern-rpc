What is RPC
-----------
RPC is an acronym for "Remote Procedure Call". It is a client-server protocol allowing a program (a desktop
software, a webserver, etc.) to execute a function on another machine, using HTTP messages
as transport for requests and responses.

What is django-modern-rpc
-------------------------
This library can be used to implement a XML-RPC / JSON-RPC server as part of your Django project. It provide a simple
and pythonic API to expose a set of global functions to the outside world.

Requirements
------------

- Python 2.7, 3.3+
- Django 1.8+
- Optionally, you may need to install ``markdown`` or ``docutils`` to support rich-text in your methods documentation.

Main features
-------------

**Multi-protocols support**

Both XML-RPC_ and `JSON-RPC 2.0`_ protocols are supported. Please note that JSON-RPC 1.0 is not supported.
The request's ``Content-Type`` is used to determine how incoming RPC call will be handled.

.. _XML-RPC: http://xmlrpc.scripting.com/
.. _JSON-RPC 2.0: http://www.jsonrpc.org/specification

**Authentication**

Restrict access to your RPC methods by configuring one or more predicates. They are executed before
remote procedure to determine if client is allowed to run it. In addition, a set of pre-defined
decorators can be used to control access based on `HTTP Basic auth`_.

.. _HTTP Basic auth: https://en.wikipedia.org/wiki/Basic_access_authentication

**Error management**

Internally, django-modern-rpc use exceptions to track errors. This help to return a correct error response to clients
as well as tracking error on server side.

**Other features**

Multiple entry-points
  You can configure your project to have as many RPC entry point as you want. This allows to
  provide different RPC methods depending on the URL used to expose them.

Auto-generated documentation
  Provide a view and a default template to display a list of all available RPC methods
  on the server and the corresponding documentation, based on methods docstring.

System introspection methods
  Common system methods such as ``system.listMethods()``, ``system.methodSignature()`` and
  ``system.methodHelp()`` are provided to both JSON-RPC and XML-RPC clients. In adition, ``system.multicall()`` is
  provided to XML-RPC client only to allow launching multiple methods in a single RPC call. JSON-RPC client doesn't need
  such a method since the protocol itself define how client can use batch requests to call multiple RPC methods at once.


Quick-start
-----------
Learn how to install and configure django-modern-rpc in one minute: read the :ref:`Quick-start guide`.
