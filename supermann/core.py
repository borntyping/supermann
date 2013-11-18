"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import logging
import os
import warnings

import psutil

import supermann.actions
import supermann.riemann.client
import supermann.supervisor.events
import supermann.supervisor.listener


class Supermann(object):
    """The main Supermann proccess"""

    def __init__(self, reserve_stdin=True, reserve_stdout=True):
        self.log = logging.getLogger('supermann')
        self.supervisor = supermann.supervisor.listener.EventListener()
        self.riemann = supermann.riemann.client.UDPClient('localhost', 5555)
        self.actions = list()

        self.register_action(
            supermann.supervisor.events.TICK,
            supermann.actions.SystemMonitorAction)
        self.register_action(
            supermann.supervisor.events.TICK,
            supermann.actions.SupervisorMonitorAction)
        self.register_action(
            supermann.supervisor.events.TICK,
            supermann.actions.ProcessMonitorAction)
        self.register_action(
            supermann.supervisor.events.PROCESS_STATE,
            supermann.actions.ProcessStateAction)

    def register_action(self, event_class, action_class):
        self.actions.append((event_class, action_class(self)))

    def run(self):
        """Wait for events from Supervisor and pass them to recive()"""
        with self.riemann:
            while True:
                event = self.supervisor.wait()
                self.recive(event)
                self.supervisor.ok()

    def recive(self, event):
        """Handle each event from supervisor"""
        for event_class, action in self.actions:
            if isinstance(event, event_class):
                action(event)

    @property
    def process(self):
        return psutil.Process(os.getpid())

    @property
    def parent(self):
        return self.process.parent

    def check_parent(self):
        if self.parent is None:
            warnings.warn(
                "Supermann has no parent proccess!", RuntimeWarning)
        if self.parent.name != "supervisord":
            warnings.warn(
                "Supermann is not running under supervisord", RuntimeWarning)
        self.log.info("Supermann process PID is: {0}".format(self.process.pid))
        self.log.info("Parent process PID is: {0}".format(self.parent.pid))
