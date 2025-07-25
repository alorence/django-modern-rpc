from django.urls import path
from project.rpc import math

from modernrpc import RpcServer

server = RpcServer()
server.register_namespace(math, "math")

urlpatterns = [
    path("rpc", server.view, name="rpc"),
    path("async_rpc", server.async_view, name="async_rpc"),
]
