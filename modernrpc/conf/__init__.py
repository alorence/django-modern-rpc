# coding: utf-8
import logging

from django.conf import settings as user_settings

from modernrpc.conf import default_settings
from modernrpc.utils import logger_has_handlers


class ModernRpcSettings(object):

    def __getattr__(self, item):

        try:
            # First, try to retrieve setting from project level settings module
            return getattr(user_settings, item)
        except AttributeError:
            # Fallback: return the default value, provided by django-modern-rpc
            return getattr(default_settings, item)


settings = ModernRpcSettings()


def get_modernrpc_logger(name):
    """Get a logger from default logging manager. If no handler is associated, add a default NullHandler"""
    logger = logging.getLogger(name)
    if not logger_has_handlers(logger):
        # If logging is not configured in the current project, configure this logger to discard all logs messages.
        # This will prevent the 'No handlers could be found for logger XXX' error on Python 2,
        # and avoid redirecting errors to the default 'lastResort' StreamHandler on Python 3
        logger.addHandler(logging.NullHandler())
    return logger
