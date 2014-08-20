"""Supervisor interface for Supermann"""

from __future__ import absolute_import, unicode_literals

import os
import sys

import supervisor.childutils

import supermann.utils
import supermann.signals


class Event(object):
    """An event recived from Supervisor"""

    __slots__ = ['headers', 'payload']

    def __init__(self, headers, payload):
        self.headers = headers
        self.payload = payload


class EventListener(object):
    """A simple Supervisor event listener"""

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout,
                 reserve_stdin=True, reserve_stdout=True):
        """Listens for events from Supervisor and yields Event objects

        STDIN and STDOUT are referenced by the object, so that they are easy
        to test, and so the references in sys can be disabled.

        :param file stdin: A file-like object that can be used as STDIN
        :param file stdout: A file-like object that can be used as STDOUT
        :param bool reserve_stdin: Set ``sys.stdin`` to ``None``
        :param bool reserve_stdout: Set ``sys.stdout`` to ``None``
        """
        self.log = supermann.utils.getLogger(self)

        self.stdin = stdin
        self.stdout = stdout

        # As stdin/stdout are used to communicate with Supervisor,
        # reserve them by replacing the sys attributes with None
        if reserve_stdin:
            sys.stdin = None
            self.log.debug("Supervisor listener has reserved STDIN")
        if reserve_stdout:
            sys.stdout = None
            self.log.debug("Supervisor listener has reserved STDOUT")

    @staticmethod
    def parse(line):
        """Parses a Supervisor header or payload

        :param str line: A line from a Supervisor message
        :returns: A dictionary containing the header or payload
        """
        return dict([pair.split(':') for pair in line.split()])

    def ready(self):
        """Writes and flushes the READY symbol to stdout"""
        self.stdout.write('READY\n')
        self.stdout.flush()

    def result(self, result):
        """Writes and flushes a result message to stdout

        :param str result: ``OK`` or ``FAIL``
        """
        self.stdout.write('RESULT {0}\n{1}'.format(len(result), result))
        self.stdout.flush()

    def ok(self):
        self.result('OK')

    def fail(self):
        self.result('FAIL')

    def wait(self):
        """Waits for an event from Supervisor, then reads and returns it

        :returns: An :py:class:`.Event` containing the headers and payload
        """
        headers = self.parse(self.stdin.readline())
        payload = self.parse(self.stdin.read(int(headers.pop('len'))))
        self.log.debug("Received %s from supervisor", headers['eventname'])
        return Event(headers, payload)


class Supervisor(object):
    """Contains the Supervisor event listener and XML-RPC interface"""

    def __init__(self):
        self.log = supermann.utils.getLogger(self)

        try:
            self.log.info("Using Supervisor XML-RPC interface at {0}".format(
                os.environ['SUPERVISOR_SERVER_URL']))
        except KeyError:
            raise RuntimeError("SUPERVISOR_SERVER_URL is not set!")

        self.listener = EventListener()
        self.interface = supervisor.childutils.getRPCInterface(os.environ)

    @property
    def rpc(self):
        """Returns the 'supervisor' namespace of the XML-RPC interface"""
        return self.interface.supervisor

    def run_forever(self):
        """Yields events from Supervisor, managing the OK and READY signals

        :returns: A stream of :py:class:`.Event`s
        """
        while True:
            self.listener.ready()
            yield self.listener.wait()
            self.listener.ok()
