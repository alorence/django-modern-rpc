Configuration
=============

In your project's settings, you can override some variable to customize behavior of django-modern-rpc.


JSONRPC_DEFAULT_ENCODER
^^^^^^^^^^^^^^^^^^^^^^^

default::

  JSONRPC_DEFAULT_ENCODER = "django.core.serializers.json.DjangoJSONEncoder"

Override if you want to use a different class to serialize your data into JSON.
