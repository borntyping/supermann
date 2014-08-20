"""Utility functions used in other parts of Supermann"""

from __future__ import absolute_import, unicode_literals

import logging

#: The default log format
LOG_FORMAT = '%(asctime)s %(levelname)-8s [%(name)s] %(message)s'

#: A set of log levels availible for --log-level's choices
LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}


def configure_logging(level=logging.INFO, format=LOG_FORMAT, log=''):
    """This configures a logger to output to the console

    :param level: The log level to set
    :type level: int or str
    :param str format: The logging format to use
    :param str log: The log to configure, defaulting to the root logger
    """
    if isinstance(level, basestring):
        level = LOG_LEVELS.get(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format))
    log = logging.getLogger(log)
    log.setLevel(level)
    log.addHandler(handler)


def fullname(obj):
    """Returns the qualified name of an object's class

    :param obj: An object to inspect
    :returns: The name of the objects class
    """
    name = obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__
    return '.'.join([obj.__module__, name])


def getLogger(obj):
    """Returns a logger using the full name of the given object

    :param obj: An object to inspect
    :returns: A logger object using the :py:func:`.fullname` of the object
    """
    return logging.getLogger(fullname(obj))
