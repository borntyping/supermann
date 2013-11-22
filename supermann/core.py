"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import collections
import logging
import os
import traceback
import warnings

import psutil

import supermann.metrics
import supermann.riemann
import supermann.signals
import supermann.supervisor


class Supermann(object):
    """The main Supermann process"""

    def __init__(self, host='localhost', port=5555):
        self.log = supermann.utils.getLogger(self)
        self.log.info("This looks like a job for Supermann!")

        self.actions = collections.defaultdict(list)

        # The Supervisor interface reads configuration from the environment
        self.supervisor = supermann.supervisor.Supervisor()

        # But Riemann does need configuring
        self.riemann = supermann.riemann.Riemann(host, port)

    def connect(self, signal, reciver):
        """Connects a signal that will recive messages from this instance"""
        return signal.connect(reciver, sender=self)

    def run(self):
        try:
            self.riemann.client.connect()
            for event in self.supervisor.run_forever():
                # Emit a signal for each event
                supermann.signals.event.send(self, event=event)
                # Emit a signal for each Supervisor subprocess
                self.emit_processes(event=event)
                # Send the queued events at the end of the cycle
                self.riemann.send_queue()
        except Exception as exception:
            self.log.exception("A fatal exception has occurred:")
            traceback.print_exc()
        finally:
            # Ensure the Riemann client is closed if we crash
            self.riemann.client.disconnect()

    def emit_processes(self, event):
        """Emit a signal for each Supervisor child process"""
        for data in self.supervisor.rpc.getAllProcessInfo():
            process = psutil.Process(data['pid'])
            data.setdefault('name', process.name)
            supermann.signals.process.send(self, process=process, **data)

    def check_parent(self):
        """Checks that Supermann is running under Supervisor"""
        process = psutil.Process()

        if process.parent is None:
            self.log.warn("Supermann has no parent process!")
        self.log.info("Supermann process PID is: {0}".format(self.process.pid))
        self.log.info("Parent process PID is: {0}".format(self.parent.pid))
        if process.parent.pid != self.supervisor.rpc.getPID():
            self.log.warn("Supermann is not running under supervisord")

