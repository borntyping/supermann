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
        self.actions = collections.defaultdict(list)
        self.process_cache = dict()
        self.log = supermann.utils.getLogger(self)

        # Before connecting to Supervisor and Riemann, show when Supermann
        # started up and which supervisord instance it is running under
        process = psutil.Process(os.getpid())
        self.log.info("This looks like a job for Supermann!")
        self.log.debug("Supermann process PID is: {0}".format(process.pid))
        self.log.debug("Parent process PID is: {0}".format(process.parent.pid))

        # The Supervisor listener and client take their configuration from
        # the environment variables provided by Supervisor
        self.supervisor = supermann.supervisor.Supervisor()

        # The Riemann client uses the host and port passed on the command line
        self.riemann = riemann_client.client.QueuedClient(
            riemann_client.transport.TCPTransport(host, port))
        supermann.utils.getLogger(self.riemann).info(
            "Using Riemann protobuf server at {0}:{1}".format(host, port))

        # This sets an exception handler to deal with uncaught exceptions -
        # this is used to ensure both a log message (and more importantly, a
        # timestamp) and a full traceback is output to stderr
        sys.excepthook = self.exception_handler

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

    def exception_handler(self, *exc_info):
        """Ensures exceptions are logged"""
        self.log.error("A fatal exception occurred:", exc_info=exc_info)

    def emit_processes(self, event):
        """Emit a signal for each Supervisor child process

        A new cache is created from the processes emitted in this cycle, which
        drops processes that no longer exist from the cache.
        """
        cache = dict()

        for data in self.supervisor.rpc.getAllProcessInfo():
            pid = data.pop('pid')
            cache[pid] = self._get_process(pid)
            self.log.debug("Emitting signal for process {0}({1})".format(
                data['name'], pid))
            supermann.signals.process.send(self, process=cache[pid], data=data)

        self.process_cache = cache

    def _get_process(self, pid):
        """Returns a psutil.Process object or None for a PID

        Returns None is the PID is 0, which Supervisor uses for a dead process
        Returns a process from the cache if one exists with the same PID, or a
        new Process instance if the PID has not been cached.

        The cache is used because psutil.Process.get_cpu_percent(interval=0)
        stores state. When get_cpu_percent is next called, it returns the CPU
        utilisation since the last call - creating a new instance each cycle
        breaks this.
        """
        if pid == 0:
            return None
        elif pid in self.process_cache:
            return self.process_cache[pid]
        else:
            return psutil.Process(pid)
