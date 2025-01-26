from django.urls import path
from project.rpc import math

from modernrpc import RPCServer

server = RPCServer()
server.register_namespace(math, "math")


urlpatterns = [
    path("rpc", server.view, name="rpc"),
]
