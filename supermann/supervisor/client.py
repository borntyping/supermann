"""Supervisor XML-RPC server wrapper"""

from __future__ import absolute_import, unicode_literals, print_function

import os

import supervisor.childutils


class XMLRPCClient(object):
    def __init__(self):
        self.server = supervisor.childutils.getRPCInterface(os.environ)

    def processes(self):
        return self.server.supervisor.getAllProcessInfo()

    def pid(self):
        return self.server.supervisor.getPID()
