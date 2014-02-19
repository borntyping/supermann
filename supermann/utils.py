"""Utility functions used in other parts of Supermann"""

from __future__ import absolute_import, unicode_literals

import logging

LOG_FORMAT = '%(asctime)s %(levelname)-8s [%(name)s] %(message)s'

LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}


def configure_logging(level=logging.INFO, format=LOG_FORMAT, log=''):
    """This configures a logger to output to the console"""
    if isinstance(level, basestring):
        level = LOG_LEVELS.get(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format))
    log = logging.getLogger(log)
    log.setLevel(level)
    log.addHandler(handler)


def fullname(obj):
    """Returns the qualified name of an object's class"""
    name = obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__
    return '.'.join([obj.__module__, name])


def getLogger(obj):
    """Returns a logger using the full name of the given object"""
    return logging.getLogger(fullname(obj))
