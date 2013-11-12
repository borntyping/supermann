"""A Supervisor event listener for Riemann"""

from __future__ import absolute_import, unicode_literals, print_function

import sys

import supermann.events

__version__ = '0.1.0'
__author__ = 'Sam Clements <sam.clements@datasift.com>'
__all__ = ['Supermann']


class EventListener(object):
    """A basic Supervisor event listener"""

    def parse(self, line):
        """Parses a Supervisor header or payload"""
        return dict([pair.split(':') for pair in line.split()])

    def ready(self):
        """Writes and flushes the READY symbol to stdout"""
        sys.stdout.write('READY\n')
        sys.stdout.flush()

    def result(self, result):
        """Writes and flushes a result message to stdout"""
        sys.stdout.write('RESULT {}\n{}'.format(len(result), result))
        sys.stdout.flush()

    def ok(self):
        self.result('OK')

    def fail(self):
        self.result('FAIL')

    def wait(self):
        """Waits for an event from Supervisor, then reads and returns it"""
        self.ready()
        headers = self.parse(sys.stdin.readline())
        payload = self.parse(sys.stdin.read(int(headers.pop('len'))))
        return supermann.events.Event(headers, payload)


class Supermann(object):
    """The Supermann event listener"""

    def __init__(self):
        self.supervisor = EventListener()

    def run(self):
        """Wait for events from Supervisor and pass them to recive()"""
        print("Starting Supermann...", file=sys.stderr)
        while True:
            event = self.supervisor.wait()
            self.recive(event)
            self.supervisor.ok()

    def recive(self, event):
        """Handle each event from supervisor"""
        if isinstance(event, supermann.events.Tick):
            print("Tick at {0} (every {1} seconds) {2!r}".format(
                event.when, event.frequency, event), file=sys.stderr)
        else:
            print("Recived {event!r}".format(event=event), file=sys.stderr)


def main():
    supermann = Supermann()
    supermann.run()
