"""A Supervisor event listener for Riemann"""

from __future__ import unicode_literals, print_function

import sys

import supermann.events

__version__ = '0.1.0'
__author__ = 'Sam Clements <sam.clements@datasift.com>'


class EventListener(object):
    """A basic Supervisor event listener"""

    def headers(self, line):
        return dict([pair.split(':') for pair in line.split()])

    def ready(self):
        sys.stdout.write('READY\n')
        sys.stdout.flush()

    def result(self, result):
        sys.stdout.write('RESULT {}\n{}'.format(len(result), result))
        sys.stdout.flush()

    def ok(self):
        self.result('OK')

    def fail(self):
        self.result('FAIL')

    def wait(self):
        self.ready()
        headers = self.headers(sys.stdin.readline())
        payload = self.headers(sys.stdin.read(int(headers.pop('len'))))
        return header, payload

    def run(self):
        """Wait for events from Supervisor and pass them to event()"""
        while True:
            header, payload = self.wait()
            self.event(header, payload)

    def event(self):
        raise NotImplementedError


class Supermann(EventListener):
    """The Supermann event listener"""

    def run(self):
        print("Starting Supermann...", file=sys.stderr)
        super(self, Supermann).run()

    def event(self, headers, payload):
        event = supermann.events.Event.create(headers, payload)

        if isinstance(event, supermann.events.Tick):
            print("Tick at {tick.when} (every {tick.frequency} second) {tick!r}".format(tick=tick), file=sys.stderr)
        else:
            print("Recived {event!r}".format(event=event), file=sys.stderr)

        self.ok()


def main():
    Supermann().run()
