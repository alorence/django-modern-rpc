Frequently Asked Questions
==========================

Is it possible to return model instances?
-----------------------------------------
No. RPC protocols only support primitive types (strings, integers, floats, booleans, None) and collections (lists,
dicts). You have to convert model instances to serializable types yourself, for example by returning a dictionary:

.. code-block:: python

   @server.register_procedure
   def get_user(user_id: int) -> dict:
       user = User.objects.get(pk=user_id)
       return {"id": user.id, "username": user.username, "email": user.email}

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
