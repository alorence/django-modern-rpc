import logging

from modernrpc.conf import logger_has_handlers, get_modernrpc_logger


def test_configured_logger():
    # Logger has been configured in settings.py
    # In such case, logging.getLogger() and get_modernrpc_logger() return
    # the same object instance, without any modification
    logger = logging.getLogger('my_app')
    assert logger_has_handlers(logger) is True

    assert logger is get_modernrpc_logger('my_app')


def test_unconfigured_logger():
    # When trying to retrieve an unconfigured logger with logging.getLogger(), no handler is associated
    logger = logging.getLogger('xxx_unconfigured')
    assert logger_has_handlers(logger) is False

    # If we retrieve it with get_modernrpc_logger(), the returned object has a default NullHandler attached
    logger2 = get_modernrpc_logger('xxx_unconfigured')
    assert logger_has_handlers(logger2) is True
    assert len(logger2.handlers) == 1
    assert isinstance(logger2.handlers[0], logging.NullHandler)


def test_unconfigured_no_propagate():
    # If a parent of unconfigured logger have no handlers AND propagate flag set to False, the returned object
    # cannot handle any log message
    logger = logging.getLogger('my_app.a.b')
    assert logger_has_handlers(logger) is False

    # But as before, get_modernrpc_logger() returns a logger with a default NullHandler
    logger2 = get_modernrpc_logger('my_app.a.b')
    assert logger_has_handlers(logger2) is True
    assert len(logger2.handlers) == 1
    assert isinstance(logger2.handlers[0], logging.NullHandler)
