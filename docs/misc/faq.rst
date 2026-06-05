Frequently Asked Questions
==========================

Is it possible to return model instances?
-----------------------------------------
No. RPC protocols only support a limited set of types: scalars (strings, integers, floats, booleans, None), collections
(lists, dicts) and a few special types such as dates and binary data. See :ref:`Types support` for the full list. You
have to convert model instances to serializable types yourself, for example by returning a dictionary:

.. code-block:: python

   @server.register_procedure
   def get_user(user_id: int) -> dict:
       user = User.objects.get(pk=user_id)
       return {"id": user.id, "username": user.username, "email": user.email}

A third-party library like `Pydantic <https://pydantic.dev/>`_ may help to easily produce valid dict from high level data.

Can I register a procedure in multiple servers?
-----------------------------------------------
A procedure can be decorated multiple times, so it can be registered in more than one server.

See :ref:`multi-servers-registration`

Can I register a namespace into a namespace?
--------------------------------------------

No, this is currently not supported. If you need multiple levels of nesting, you can use the ``name`` parameter
on ``register_procedure`` to declare procedures with a dotted name (e.g., ``"math.advanced.fft"``).

Is there a way to serve documentation on server endpoint with GET request?
--------------------------------------------------------------------------

The automatic HTML documentation generation through entry points has been removed in v2. However, you can configure
``RpcServer`` with ``redirect_get_request_to`` to redirect GET requests to another view (e.g., a custom documentation
page). See :ref:`GET requests redirection` for details.
