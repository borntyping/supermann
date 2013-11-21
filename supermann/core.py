"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import collections
import logging
import os
import warnings

import psutil

import supermann.metrics
import supermann.riemann.client
import supermann.supervisor.client
import supermann.supervisor.events
import supermann.supervisor.listener


class Supermann(object):
    """The main Supermann process"""

    def __init__(self, host='localhost', port=5555):
        self.log = supermann.utils.getLogger(self)
        self.log.info("This looks like a job for Supermann!")

        self.metrics = collections.defaultdict(list)
        self.queue = list()

        self.event_listener = supermann.supervisor.listener.EventListener()
        self.supervisor_client = supermann.supervisor.client.XMLRPCClient()
        self.riemann = supermann.riemann.client.UDPClient(host, port)

    @property
    def supervisor(self):
        """Returns the supervisor namespace of the XML-RPC client"""
        return self.supervisor_client.supervisor

    # Event handling

    def register_metric_function(self, event_class, *functions):
        self.metric_functions[event_class].extend(functions)

    def run(self):
        """Wait for events from Supervisor and pass them to recive()"""
        with self.riemann:
            while True:
                event = self.event_listener.wait()
                self.recive(event)
                self.event_listener.ok()

    def recive(self, supervisor_event):
        """Handle each event from supervisor"""
        for event_class in self.metrics:
            if isinstance(supervisor_event, event_class):
                for metric in self.metrics[event_class]:
                    self.log.debug("Collecting metric {0}.{1}".format(
                        metric.__module__, metric.__name__))
                    self.queue_events(*metric(self, supervisor_event))
        self.flush_queue()

    # Event queue

    def queue_events(self, *events):
        self.queue.extend(events)

    def flush_queue(self):
        """Sends all events in the queue to Riemann and resets the queue"""
        self.riemann.send_events(*self.queue)
        self.queue = list()

    # Process management

    @property
    def process(self):
        return psutil.Process(os.getpid())

    @property
    def parent(self):
        return self.process.parent

    def check_parent(self):
        """Checks that Supermann is running under Supervisor"""
        if self.parent is None:
            self.log.warn("Supermann has no parent process!")
        self.log.info("Supermann process PID is: {0}".format(self.process.pid))
        self.log.info("Parent process PID is: {0}".format(self.parent.pid))
        if self.process.parent.pid != self.supervisor.getPID():
            self.log.warn("Supermann is not running under supervisord")

