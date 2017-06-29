# coding: utf-8
import logging

from django.conf import settings as user_settings

from modernrpc.conf import default_settings
from modernrpc.utils import logger_has_handlers


class ModernRpcSettings:

    def __getattr__(self, item):
        if hasattr(user_settings, item):
            # We can't put 'getattr(default_settings, item)' as 3rd default argument here,
            # because it will be evaluated always and raise AttributeError if missing, even
            # when the attribute can  be found in user_settings
            return getattr(user_settings, item)
        else:
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
