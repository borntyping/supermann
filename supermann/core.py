"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import collections
import os
import sys

import psutil
import riemann_client.client
import riemann_client.transport

import supermann.metrics
import supermann.signals
import supermann.supervisor


class Supermann(object):
    """The main Supermann process"""

    def __init__(self, host=None, port=None):
        self.log = supermann.utils.getLogger(self)
        self.log.info("This looks like a job for Supermann!")
        self.actions = collections.defaultdict(list)

        # The Supervisor listener and client take their configuration from
        # the environment variables provided by Supervisor
        self.supervisor = supermann.supervisor.Supervisor()

        self.riemann = riemann_client.client.QueuedClient(
            riemann_client.transport.TCPTransport(host, port))

        # This sets an exception handler to deal with uncaught exceptions -
        # this is used to ensure both a log message (and more importantly, a
        # timestamp) and a full traceback is output to stderr
        self.set_exception_handler()

    def connect(self, signal, reciver):
        """Connects a signal that will recive messages from this instance"""
        return signal.connect(reciver, sender=self)

    def run(self):
        """Runs forever, ensuring Riemann is disconnected properly"""
        with self.riemann:
            for event in self.supervisor.run_forever():
                # Emit a signal for each event
                supermann.signals.event.send(self, event=event)
                # Emit a signal for each Supervisor subprocess
                self.emit_processes(event=event)
                # Send the queued events at the end of the cycle
                self.riemann.flush()

    def set_exception_handler(self):
        """Sets Supermann.exception_handler as the global exception handler"""
        sys.excepthook = self.exception_handler

    def exception_handler(self, *exc_info):
        """Ensures exceptions are logged"""
        self.log.error("A fatal exception occurred:", exc_info=exc_info)

    def emit_processes(self, event):
        """Emit a signal for each Supervisor child process"""
        for data in self.supervisor.rpc.getAllProcessInfo():
            process = self._get_process(data.pop('pid'))
            supermann.signals.process.send(self, process=process, **data)

    def _get_process(self, pid):
        """Returns a psutil.Process object, or None if the PID is 0"""
        return psutil.Process(pid) if (pid != 0) else None

    def check_supervisor(self):
        """Checks that Supermann is correctly running under Supervisor"""
        process = psutil.Process(os.getpid())

        self.log.info("Supermann process PID is: {0}".format(process.pid))

        # Check that Supermann has a parent process
        if process.parent is None:
            self.log.critical("Supermann has no parent process!")
            return False

        self.log.info("Parent process PID is: {0}".format(process.parent.pid))

        # Check that the SUPERVISOR_SERVER_URL environment variable is set
        if 'SUPERVISOR_SERVER_URL' not in os.environ:
            self.log.critical("SUPERVISOR_SERVER_URL is not set!")
            return False

        # Check that the parent PID and the Supervisor PID match up
        if process.parent.pid != self.supervisor.rpc.getPID():
            self.log.critical("Supermann's parent process is not Supervisord!")
            return False

        return True

    def check_riemann(self):
        """Adds some basic information about the Riemann server to the log"""
        log = supermann.utils.getLogger(self.riemann)
        log.info("Using Riemann protobuf server at {0}:{1}".format(
            *self.riemann.transport.address))
