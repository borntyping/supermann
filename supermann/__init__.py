"""A Supervisor event listener for Riemann"""

from __future__ import absolute_import, unicode_literals, print_function

import os
import sys
import warnings

import psutil

import supermann.riemann.client
import supermann.supervisor.events
import supermann.supervisor.listener

__version__ = '0.1.0'
__author__ = 'Sam Clements <sam.clements@datasift.com>'
__all__ = ['Supermann']


class Supermann(object):
    """The Supermann event listener"""

    def __init__(self, reserve_stdin=True, reserve_stdout=True):
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
                'service': 'supervisor/tick',
                'state': 'ok',
                'time': event.when,
                'metric_f': event.serial,
                'tags': ['supermann', 'supervisor', 'tick']
            },{
                'service': 'system/cpu/percent',
                'metric_f': psutil.cpu_percent(interval=0),
                'tags': ['supermann', 'system', 'cpu', 'percent']
            },{
                'service': 'system/mem/percent',
                'metric_f': psutil.virtual_memory().percent,
                'tags': ['supermann', 'system', 'mem', 'percent']
            })
        elif isinstance(event, supermann.supervisor.events.PROCESS_STATE):
            self.riemann.send_event({
                'service': 'process/{name}/state'.format(name=event.name),
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
            warnings.warn("Supermann has no parent proccess!", RuntimeWarning)
        if self.parent.name != "supervisord":
            warnings.warn("Supermann is not running under supervisord", RuntimeWarning)
        return self.parent


def main():
    supermann = Supermann()

    print("Parent proccess is:", supermann.check_parent(), file=sys.stderr)

    supermann.run()
