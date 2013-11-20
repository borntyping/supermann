"""Supervisor XML-RPC server wrapper"""

from __future__ import absolute_import, unicode_literals, print_function

import os

import supervisor.childutils


def XMLRPCClient():
    """Returns an XML-RPC client built from Supervisor's environment"""
    return supervisor.childutils.getRPCInterface(os.environ)
