from modernrpc.core import Protocol, RpcRequestContext
from modernrpc.server import RPCNamespace, RPCServer

__all__ = [
    "Protocol",
    "RPCNamespace",
    "RPCServer",
    "RpcRequestContext",
]

# Package version is now stored only in pyproject.toml. To retrieve it from code, use:
#   import pkg_resources; version = pkg_resources.get_distribution('django-modern-rpc').version
# or in recent Python version (> 3.11), use
#   import importlib.metadata; version = importlib.metadata.version("django-modern-rpc")
