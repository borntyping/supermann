"""A Supervisor event listener"""

from __future__ import absolute_import, unicode_literals

import logging
import sys

import supermann.supervisor.events
import supermann.utils


class EventListener(object):
    """A basic Supervisor event listener"""

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout,
                 reserve_stdin=True, reserve_stdout=True):
        self.log = supermann.utils.getLogger(self)

        # STDIN and STDOUT are referenced by the object, so that they are easy
        # to test, and so the references in sys can be removed (see below)
        self.stdin = stdin
        self.stdout = stdout

        # As stdin/stdout are used to communicate with Supervisor,
        # reserve them by replacing the sys attributes with None
        if reserve_stdin:
            sys.stdin = None
            self.log.warn("Supervisor listener has reserved STDIN")
        if reserve_stdout:
            sys.stdout = None
            self.log.warn("Supervisor listener has reserved STDOUT")

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
        self.log.debug("Received %s from supervisor", headers['eventname'])
        return supermann.supervisor.events.Event(headers, payload)
