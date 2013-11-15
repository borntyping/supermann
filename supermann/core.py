"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import logging
import os
import warnings

import psutil

import supermann.riemann.client
import supermann.supervisor.events
import supermann.supervisor.listener


class Supermann(object):
    """The main Supermann proccess"""

    def __init__(self, reserve_stdin=True, reserve_stdout=True):
        self.log = logging.getLogger('supermann')
        self.supervisor = supermann.supervisor.listener.EventListener()
        self.riemann = supermann.riemann.client.UDPClient('localhost', 5555)

    def run(self):
        """Wait for events from Supervisor and pass them to recive()"""
        with self.riemann:
            while True:
                event = self.supervisor.wait()
                self.recive(event)
                self.supervisor.ok()

    def recive(self, event):
        """Handle each event from supervisor"""
        if isinstance(event, supermann.supervisor.events.TICK):
            self.riemann.send_event({
                'service': 'supervisor:tick',
                'state': 'ok',
                'time': event.when,
                'metric_f': event.serial,
                'tags': ['supermann', 'supervisor', 'tick']
            }, {
                'service': 'system:cpu:percent',
                'metric_f': psutil.cpu_percent(interval=0),
                'tags': ['supermann', 'system', 'cpu', 'percent']
            }, {
                'service': 'system:mem:percent',
                'metric_f': psutil.virtual_memory().percent,
                'tags': ['supermann', 'system', 'mem', 'percent']
            })
        elif isinstance(event, supermann.supervisor.events.PROCESS_STATE):
            self.log.info("Process {0} changed state from {1} to {2}".format(
                event.name, event.from_state, event.state))
            self.riemann.send_event({
                'service': 'process:{name}:state'.format(name=event.name),
                'state': event.state,
                'tags': ['supermann', 'supervisor', 'process', 'process_state']
            })

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
