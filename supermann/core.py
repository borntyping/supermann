"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import collections
import os
import sys

import psutil
import riemann_client.client
import riemann_client.transport

import supermann.metrics.process
import supermann.metrics.system
import supermann.signals
import supermann.supervisor


class Supermann(object):
    """Manages the components that make up a Supermann instance.

    Manages a the Supervisor and Riemann clients, and distributes events to the
    :py:data:`supermann.signals.event` and :py:data:`supermann.signals.process`
    signals.
    """

    def __init__(self, host=None, port=None):
        self.actions = collections.defaultdict(list)
        self.process_cache = dict()
        self.log = supermann.utils.getLogger(self)

        # Before connecting to Supervisor and Riemann, show when Supermann
        # started up and which supervisord instance it is running under
        process = psutil.Process(os.getpid())
        self.log.info("This looks like a job for Supermann!")
        self.log.info("Process PID is {0}, running under {1}".format(
            process.pid, process.ppid()))

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
        """Connects a signal that will recive messages from this instance

        :param blinker.Signal signal: Listen for events from this signal
        :param reciver: A function that will recive events
        """
        return signal.connect(reciver, sender=self)

    def connect_event(self, reciver):
        """Conects a reciver to ``event`` using :py:meth:`.connect`"""
        return self.connect(supermann.signals.event, reciver)

    def connect_process(self, reciver):
        """Conects a reciver to ``process`` using :py:meth:`.connect`"""
        return self.connect(supermann.signals.process, reciver)

    def with_all_recivers(self):
        """Adds all recivers to the Supermann instance

        :returns: the Supermann instance the method was called on
        """

        # Collect system metrics when an event is received
        self.connect_event(supermann.metrics.system.cpu)
        self.connect_event(supermann.metrics.system.mem)
        self.connect_event(supermann.metrics.system.swap)
        self.connect_event(supermann.metrics.system.load)
        self.connect_event(supermann.metrics.system.load_scaled)
        self.connect_event(supermann.metrics.system.uptime)

        # Collect metrics for each process when an event is recived
        self.connect_process(supermann.metrics.process.cpu)
        self.connect_process(supermann.metrics.process.mem)
        self.connect_process(supermann.metrics.process.fds)
        self.connect_process(supermann.metrics.process.io)
        self.connect_process(supermann.metrics.process.state)
        self.connect_process(supermann.metrics.process.uptime)

        return self

    def run(self):
        """Runs forever, ensuring Riemann is disconnected properly

        :returns: the Supermann instance the method was called on
        """
        with self.riemann:
            for event in self.supervisor.run_forever():
                # Emit a signal for each event
                supermann.signals.event.send(self, event=event)
                # Emit a signal for each Supervisor subprocess
                self.emit_processes(event=event)
                # Send the queued events at the end of the cycle
                self.riemann.flush()
        return self

    def exception_handler(self, *exc_info):
        """Used as a global exception handler to ensure errors are logged"""
        self.log.error("A fatal exception occurred:", exc_info=exc_info)

    def emit_processes(self, event):
        """Emit a signal for each Supervisor child process

        A new cache is created from the processes emitted in this cycle, which
        drops processes that no longer exist from the cache.

        :param event: An event received from Supervisor
        """
        cache = dict()

        for data in self.supervisor.rpc.getAllProcessInfo():
            pid = data.pop('pid')
            cache[pid] = self._get_process(pid)
            self.log.debug("Emitting signal for process {0}({1})".format(
                data['name'], pid))
            supermann.signals.process.send(self, process=cache[pid], data=data)

        # The cache is stored for use in _get_process and the next call
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

        :returns: A process from the cache or None
        :rtype: psutil.Process
        """
        if pid == 0:
            return None
        elif pid in self.process_cache:
            return self.process_cache[pid]
        else:
            return psutil.Process(pid)
