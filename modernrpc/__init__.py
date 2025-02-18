from modernrpc.constants import Protocol
from modernrpc.core import RpcRequestContext
from modernrpc.server import RpcNamespace, RpcServer

__all__ = [
    "Protocol",
    "RpcNamespace",
    "RpcRequestContext",
    "RpcServer",
]

# Package version is now stored only in pyproject.toml. To retrieve it from code, use:
#   import pkg_resources; version = pkg_resources.get_distribution('django-modern-rpc').version
# or in recent Python version (> 3.11), use
#   import importlib.metadata; version = importlib.metadata.version("django-modern-rpc")
