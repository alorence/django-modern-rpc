# django-modern-rpc

> **Important note**: This project is under development, and is not ready for production environment.
> You are free to install and test it and provide feedback or make pull
> request if you want to add a feature, report a bug or try to resolve
> one of them.

## Information

django-modern-rpc is a free, lightweight RPC server for Django projects.
It supports JSON-RPC and XML-RPC requests under python 2.7, 3.3, 3.4,
3.5 and Django 1.8, 1.9 and 1.10.

## Features

The project is in active development, so all the features are not yet
implemented. The list of available features is:
- XML-RPC & JSON-RPC support
- Usual errors are correctly reported to user according to the standard
- Multi-entry point, with specific methods and protocol attached

## Features planned to implement

- System introspection methods (listMethods(), methodHelp(),
methodSignature(), etc.)
- Multi-call

## Installation

There is no pypi package for now. This will be availble in the future.
To use django-modern-rpc, you have to clone it and import its path to
your PYTHONPATH when starting Django

## Quick start

Decorate the methods you want to make reachable from RPC call:
```python
# In myproject/rpc_app/rpc_methods.py
from modernrpc.core import rpc_method

@rpc_method()
def add(a, b):
    return a + b
```

and make sure these functions are imported at Django startup. A simple
way to do that is to import them in your app's modeul:

```python
# In myproject/rpc_app/__init__.py
from rpc_app.rpc_methods import add
```

Now, you have to declare an entry point. This is a standard Django view
which will automatically route the request to the right handler (for
JSON-RPC or XML-RPC call) and call the method on the server.

```python
# In myproject/rpc_app/urls.py
from django.conf.urls import url

from modernrpc.views import RPCEntryPoint

urlpatterns = [
    url(r'^rpc/', RPCEntryPoint.as_view(), name="rpc_entry_point"),
]
```

Now, you can call the function add from a client:

```python
try:
    # Python 3
    import xmlrpc.client as xmlrpc_module
except ImportError:
    # Python 2
    import xmlrpclib as xmlrpc_module

client = xmlrpc_module.ServerProxy('http://127.0.0.1:8000/all-rpc/')
print(client.add(2, 3))

# Returns: 5
```

[![Travis Build status](https://travis-ci.org/alorence/django-modern-rpc.svg?branch=master)](https://travis-ci.org/alorence/django-modern-rpc)