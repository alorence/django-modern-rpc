from django.utils import six


def logger_has_handlers(logger):
    """Since Python 2 doesn't provide Logger.hasHandlers(), we have to
    perform the lookup by ourself."""
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


def ensure_sequence(element):
    """Ensure the given argument is a sequence object (tuple, list). If not, return a list with it."""
    if isinstance(element, (tuple, list)):
        return element

    return [element]
