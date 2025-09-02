Frequently Asked Questions
==========================

Is it possible to return model instances?
-----------------------------------------
No. You have to develop your own logic.
TODO: develop this answer...

Can I register a procedure in multiple servers?
-----------------------------------------------
A procedure can be decorated multiple times, so it can be registered in more than one server.

See :ref:`multi-servers-registration`

Can I register a namespace into a namespace?
--------------------------------------------

No, this is currently not supported.

If you need multiple levels, ...

Is there a way to serve documentation on server endpoint with GET request?
--------------------------------------------------------------------------

No, this has been removed in v2. Maybe an option to return a redirection on another view can do the job?
