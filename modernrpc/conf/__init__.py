# coding: utf-8
import logging

from django.conf import settings as user_settings

from modernrpc.conf import default_settings


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
    logger = logging.getLogger(name)
    if not settings.MODERNRPC_ENABLE_LOGGING:
        # If settings.MODERNRPC_ENABLE_LOGGING set to False, attach a NullHandlers to the default logger.
        # This will prevent the 'No handlers could be found for logger XXX' error on Python 2,
        # and avoid redirecting errors to the default 'lastResort' StreamHandler on Python 3
        logger.addHandler(logging.NullHandler())
    return logger
