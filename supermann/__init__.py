"""A Supervisor event listener for Riemann"""

from __future__ import absolute_import, unicode_literals, print_function

import socket
import sys

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

        # As stdin/stdout are used to communicate with Supervisor,
        # reserve them by replacing the sys attributes with None
        if reserve_stdin:
            sys.stdin = None
        if reserve_stdout:
            sys.stdout = None

    def run(self):
        """Wait for events from Supervisor and pass them to recive()"""
        while True:
            event = self.supervisor.wait()
            self.recive(event)
            self.supervisor.ok()

    def recive(self, event):
        """Handle each event from supervisor"""
        with supermann.riemann.client.UDPClient('localhost', 5555) as client:
            if isinstance(event, supermann.supervisor.events.TICK):
                event = client.send_event(
                    host=socket.gethostname(),
                    service='supermann',
                    state='ok',
                    description="Supervisor tick",
                    tags=['supermann', 'supervisor', 'tick'])
            elif isinstance(event, supermann.supervisor.events.PROCESS_STATE):
                event = client.send_event(
                    host=socket.gethostname(),
                    service=event.name,
                    state=event.state,
                    description="Process state changed",
                    tags=['supermann', 'supervisor', 'process_state'])
            print(str(event.obj), file=sys.stderr)


def main():
    supermann = Supermann()
    supermann.run()
