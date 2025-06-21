import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ModernRpcConfig(AppConfig):
    name = "modernrpc"
    verbose_name = "Django Modern RPC"

    def ready(self): ...
