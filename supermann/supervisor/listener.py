"""A Supervisor event listener"""

from __future__ import absolute_import, unicode_literals

import sys

import supermann.supervisor.events


class EventListener(object):
    """A basic Supervisor event listener"""

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout):
        self.stdin = stdin
        self.stdout = stdout

    def parse(self, line):
        """Parses a Supervisor header or payload"""
        return dict([pair.split(':') for pair in line.split()])

    def ready(self):
        """Writes and flushes the READY symbol to stdout"""
        self.stdout.write('READY\n')
        self.stdout.flush()

    def result(self, result):
        """Writes and flushes a result message to stdout"""
        self.stdout.write('RESULT {0}\n{1}'.format(len(result), result))
        self.stdout.flush()

    def ok(self):
        self.result('OK')

    def fail(self):
        self.result('FAIL')

    def wait(self):
        """Waits for an event from Supervisor, then reads and returns it"""
        self.ready()
        headers = self.parse(self.stdin.readline())
        payload = self.parse(self.stdin.read(int(headers.pop('len'))))
        return supermann.supervisor.events.Event(headers, payload)
