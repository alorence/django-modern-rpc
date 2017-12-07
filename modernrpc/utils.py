import logging

from django.core.cache import cache
from django.utils import six


def ensure_sequence(element):
    """Ensure the given argument is a sequence object (tuple, list). If not, return a list containing its value."""
    return element if isinstance(element, (tuple, list)) else [element]


def clean_old_cache_content():
    """Clean CACHE data from old versions of django-modern-rpc"""
    cache.delete('__rpc_registry__', version=1)


def logger_has_handlers(logger):
    """
    Check if given logger has at least 1 handler associated, return a boolean value.

    Since Python 2 doesn't provide Logger.hasHandlers(), we have to perform the lookup by ourself.
    """
    if six.PY3:
        return logger.hasHandlers()
    else:
        c = logger
        rv = False
        while c:
            if c.handlers:
                rv = True
                break
            if not c.propagate:
                break
            else:
                c = c.parent
        return rv


def get_modernrpc_logger(name):
    """Get a logger from default logging manager. If no handler is associated, add a default NullHandler"""
    logger = logging.getLogger(name)
    if not logger_has_handlers(logger):
        # If logging is not configured in the current project, configure this logger to discard all logs messages.
        # This will prevent the 'No handlers could be found for logger XXX' error on Python 2,
        # and avoid redirecting errors to the default 'lastResort' StreamHandler on Python 3
        logger.addHandler(logging.NullHandler())
    return logger
