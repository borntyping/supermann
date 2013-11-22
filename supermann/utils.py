"""Utility functions used in other parts of Supermann"""

from __future__ import absolute_import, unicode_literals

import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('supermann').addHandler(NullHandler())


def fullname(obj):
    """Returns the qualified name of an object's class"""
    name = obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__
    return '.'.join([obj.__module__, name])


def getLogger(obj):
    """Returns a logger using the full name of the given object"""
    return logging.getLogger(fullname(obj))
