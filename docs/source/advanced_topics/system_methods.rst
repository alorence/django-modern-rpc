==============
System methods
==============

XML-RPC_ specification doesn't provide default methods to achieve introspection tasks, but some people proposed
a standard for such methods. The `original document`_ is now offline, but has been retrieved from Google
cache and is now hosted here_.

.. _XML-RPC: http://xmlrpc.scripting.com/spec.html
.. _original document: http://xmlrpc.usefulinc.com/doc/reserved.html
.. _here: http://scripts.incutio.com/xmlrpc/introspection.html

system.listMethods
------------------
Return a list of all methods available.

system.methodSignature
----------------------
Return the signature of a specific method

system.methodHelp
-----------------
Return the documentation for a specific method.

system.multicall
----------------

Like 3 others, this system method is not part of the standard. But its behavior has been `well defined`_
by `Eric Kidd`_. It is now implemented most of the XML-RPC servers and supported by number of
clients (including `Python's ServerProxy`_).

This method can be used to make many RPC calls at once, by sending an array of RPC payload. The result is a list of
responses, with the result for each individual request, or a corresponding fault result.

It is available only to XML-RPC clients, since JSON-RPC protocol specify how to call multiple RPC methods
at once using batch request.

.. _well defined: https://mirrors.talideon.com/articles/multicall.html
.. _Python's ServerProxy: https://docs.python.org/3/library/xmlrpc.client.html#multicall-objects
.. _Eric Kidd: https://github.com/emk
