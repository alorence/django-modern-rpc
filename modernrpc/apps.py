import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ModernRpcConfig(AppConfig):
    name = "modernrpc"
    verbose_name = "Django Modern RPC"

    def ready(self):
        self.defusedxml_monkey_patch()

    @staticmethod
    def defusedxml_monkey_patch():
        try:
            import defusedxml.xmlrpc  # noqa: PLC0415 (will be moved soon)
        except ImportError:
            msg = (
                '"defusedxml" package were not found. Your project may be vulnerable to malicious XML payloads. '
                "To secure the server against such attacks, please install 'defusedxml' or install "
                'django-modern-rpc with extra "defusedxml" (pip install django-modern-rpc[defusedxml])'
            )
            logger.debug(msg)
            return

        defusedxml.xmlrpc.monkey_patch()
