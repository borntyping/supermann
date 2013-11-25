"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import collections
import os
import traceback

import psutil

import supermann.metrics
import supermann.riemann.client
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
        self.riemann = supermann.riemann.client.UDPClient(host, port)

    def connect(self, signal, reciver):
        """Connects a signal that will recive messages from this instance"""
        return signal.connect(reciver, sender=self)

    def run(self):
        """Runs forever, ensuring Riemann is disconnected properly"""
        try:
            self.riemann.connect()
            for event in self.supervisor.run_forever():
                # Emit a signal for each event
                supermann.signals.event.send(self, event=event)
                # Emit a signal for each Supervisor subprocess
                self.emit_processes(event=event)
                # Send the queued events at the end of the cycle
                self.riemann.send_next_message()
        except Exception:
            self.log.exception("A fatal exception has occurred:")
            traceback.print_exc()
        finally:
            # Ensure the Riemann client is closed if we crash
            self.riemann.disconnect()

    def emit_processes(self, event):
        """Emit a signal for each Supervisor child process"""
        for data in self.supervisor.rpc.getAllProcessInfo():
            try:
                process = psutil.Process(data['pid'])
            except psutil.NoSuchProcess:
                process = None
            supermann.signals.process.send(self, process=process, **data)

    def check_supervisor(self):
        """Checks that Supermann is correctly running under Supervisor"""
        process = psutil.Process()

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
