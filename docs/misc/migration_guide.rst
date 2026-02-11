Migration guide
===============

From 1.1 to 2.0
---------------

This section will guide you to update an existing setup of django-modern-rpc 1.0 or 1.1 to the latest v2 release.

Update settings
^^^^^^^^^^^^^^^

MODERNRPC_METHODS_MODULES
*************************

In v2, the new Server / Namespace system will automatically import your decorated procedures. This setting is now
useless, you can simply delete it from your settings.

MODERNRPC_LOG_EXCEPTIONS
************************

This setting has been removed. In v2, exception logging can be handled through the ``error_handler`` callback
on ``RpcServer``. See :ref:`Customize error handling` for details. You can simply delete this setting from your
configuration.

MODERNRPC_DOC_FORMAT
********************

This setting still exists in v2. Accepted values are ``""`` (empty string, default), ``"rst"`` or ``"md"``
(also accepts ``"markdown"``). No migration action is needed, but note that automatic HTML documentation through
entry points has been removed. Docstrings are still processed for introspection (``system.methodHelp``).

MODERNRPC_DEFAULT_ENTRYPOINT_NAME
*********************************

The ``RPCEntryPoint`` class is not used anymore. You can define multiple ``RpcServer`` instances to split your APIs.
No specific name is required, and no default one is needed anymore. This setting is now useless, you can simply delete
it from your settings.

MODERNRPC_JSON_DECODER / MODERNRPC_JSON_ENCODER
***********************************************

Backends are now configured individually. Configuring the encoder and decoder with default builtin ``json`` backend
is still possible using new settings.

Before
......

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DECODER = "path.to.valid.json.Decoder"
    MODERNRPC_JSON_ENCODER = "path.to.valid.json.Encoder"

After
.....

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_JSON_DESERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.json.PythonJsonDeserializer",
        "kwargs": {
            "load_kwargs": {"cls": path.to.valid.json.Decoder},
        }
    }
    MODERNRPC_JSON_SERIALIZER = {
        "class": "modernrpc.jsonrpc.backends.json.PythonJsonSerializer",
        "kwargs": {
            "dump_kwargs": {"cls": path.to.valid.json.Encoder},
        }
    }

MODERNRPC_XMLRPC_USE_BUILTIN_TYPES / MODERNRPC_XMLRPC_ALLOW_NONE
****************************************************************

Backends are now configured individually. Configuring the behavior of builtin ``xmlrpc`` backend is still possible
using new settings.

Before
......

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XMLRPC_USE_BUILTIN_TYPES = False
    MODERNRPC_XMLRPC_ALLOW_NONE = False

After
.....

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_DESERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcDeserializer",
        "kwargs": {
            "load_kwargs": {"use_builtin_types": False}
        }
    }
    MODERNRPC_XML_SERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
        "kwargs": {
            "dump_kwargs": {"allow_none": False}
        }
    }


MODERNRPC_XMLRPC_DEFAULT_ENCODING
*********************************

In the previous versions, this setting was used to initialize an ``xmlrpc.client.Marshaller``. In the v2, this class is
not directly instanciated but through the serialization process. Encoding can still be configured


Before
......

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XMLRPC_DEFAULT_ENCODING = "ascii"

After
.....

.. code-block:: python
   :caption: myproject/settings.py

    MODERNRPC_XML_SERIALIZER = {
        "class": "modernrpc.xmlrpc.backends.xmlrpc.PythonXmlRpcSerializer",
        "kwargs": {
            "dump_kwargs": {"encoding": "ascii"}
        }
    }


Replace a single RPCEntryPoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before
******

Procedure registration was possible from anywhere in the code, as soon as the module
was declared in `settings.MODERNRPC_METHODS_MODULES`.

.. code-block:: python
   :caption: myapp/remote_procedures.py

   from modernrpc.core import rpc_method

   @rpc_method
   def add(a, b):
       return a + b


.. code-block:: python
   :caption: myproject/urls.py

   from django.urls import path
   from modernrpc.views import RPCEntryPoint

   urlpatterns = [
       # ... other url patterns
       path('rpc/', RPCEntryPoint.as_view()),
   ]

After
*****

With v2, an ``RpcServer`` instance must be created, and then used to register procedures.

.. code-block:: python
   :caption: myproject/myapp/rpc.py

   from modernrpc.server import RpcServer

   server = RpcServer()


   @server.register_procedure
   def add(a: int, b: int) -> int:
       """Add two numbers and return the result.

       :param a: First number
       :param b: Second number
       :return: Sum of a and b
       """
       return a + b

.. code-block:: python
   :caption: myproject/urls.py

   from django.urls import path
   from myapp.rpc import server

   urlpatterns = [
       # ... other url patterns
       path('rpc/', server.view),
   ]

Note: if you declared multiple `RPCEntryPoint` in your urls config, simply declare multiple ``RpcServer`` instances
instead, then register each procedure directly to the right server. If a procedure must be registered in 2 different
servers, simply use the registration decorator multiple times.

.. code-block:: python
   :caption: myproject/myapp/rpc.py

   from modernrpc.server import RpcServer

   api_v1 = RpcServer()
   api_v2 = RpcServer()


   @api_v1.register_procedure()
   @api_v2.register_procedure()
   def add(a: int, b: int) -> int:
       """Add two numbers and return the result.

       :param a: First number
       :param b: Second number
       :return: Sum of a and b
       """
       return a + b

This new process allow to easily customize registration per procedure and per server.

Update your authentication configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before
******

.. code-block:: python
   :caption: myproject/myapp/auth.py

   # Custom predicate used to block some procedures to known bots
   def forbid_bots_access(request):
       """Return True when request has a User-Agent different from provided list"""
       if "User-Agent" not in request.headers:
           # No User-Agent provided, the request must be rejected
           return False

       forbidden_bots = [
           'Googlebot',  # Google
           'Bingbot',  # Microsoft
           'Slurp',  # Yahoo
           'DuckDuckBot',  # DuckDuckGo
           'Baiduspider',  # Baidu
           'YandexBot',  # Yandex
           'facebot',  # Facebook
       ]

       if request.headers["User-Agent"].lower() in [ua.lower() for ua in forbidden_bots]:
           # ... forbid access
           return False

       # In all other cases, allow access
       return True


.. code-block:: python

   from modernrpc.core import rpc_method
   from modernrpc.auth import set_authentication_predicate
   from modernrpc.auth.basic import http_basic_auth_permissions_required
   from myproject.myapp.auth import forbid_bots_access


   @rpc_method
   @http_basic_auth_permissions_required(permissions='auth.view_user')
   def my_rpc_method_with_builtin_predicate(username):
       user = User.objects.get(username=username)
       return f"{user.first_name} {user.last_name}"

   @rpc_method
   @set_authentication_predicate(forbid_bots_access)
   def my_rpc_method_with_custom_authentication(a, b):
       return a + b


After
*****


.. code-block:: python
   :caption: myproject/myapp/auth.py

   from django.contrib.auth import authenticate

   # Predicate used to block some procedures to known bots
   def forbid_bots_access(request: HttpRequest):
       """Return True when request has a User-Agent different from provided list"""
       if "User-Agent" not in request.headers:
           # No User-Agent provided, the request must be rejected
           return False

       forbidden_bots = [
           'Googlebot',  # Google
           'Bingbot',  # Microsoft
           'Slurp',  # Yahoo
           'DuckDuckBot',  # DuckDuckGo
           'Baiduspider',  # Baidu
           'YandexBot',  # Yandex
           'facebot',  # Facebook
       ]

       if request.headers["User-Agent"].lower() in [ua.lower() for ua in forbidden_bots]:
           # ... forbid access
           return False

       # In all other cases, allow access
       return True


   # Predicate to check for specific Django permissions
   def check_view_permissions(perms: str):
       def inner(request: HttpRequest):
           # Use modernrpc helper to extract Basic Auth username & password
           username, password = extract_http_basic_auth(request)
           # Use Django auth system to authenticate the user
           user = authenticate(username=username, password=password)
           # Check for authentication (valid username & password) AND for permissions
           if not user or not user.has_perm(perms):
               return False
           # User is authenticated AND authorized
           return user

       return inner


.. code-block:: python

   from myproject.myapp.auth import check_view_permissions, forbid_bots_access


   @server.register_procedure(auth=check_view_permissions("auth.view_user"))
   def my_rpc_method_with_builtin_predicate(username: str):
       user = User.objects.get(username=username)
       return f"{user.first_name} {user.last_name}"

   @server.register_procedure(auth=forbid_bots_access)
   def my_rpc_method_with_custom_authentication(a, b):
       return a + b
