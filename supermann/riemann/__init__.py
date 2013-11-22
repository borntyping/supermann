"""Supermann interface for Riemann"""

from __future__ import absolute_import, unicode_literals

import socket

import supermann.riemann.client

class Riemann(object):
    def __init__(self, host='localhost', port=5555):
        self.log = supermann.utils.getLogger(self)
        self.client = supermann.riemann.client.UDPClient(host, port)
        self.create_queue()

    def create_queue(self):
        self.queue = supermann.riemann.riemann_pb2.Msg()

    def queue_events(self, *events):
        self.queue.events.extend(map(self.create_event, events))

    def send_queue(self):
        self.log.debug("Sending {n} events to Riemann".format(
            n=len(self.queue.events)))
        self.client.send(self.queue)
        self.create_queue()

    def create_event(self, data):
        if isinstance(data, supermann.riemann.riemann_pb2.Event):
            return data
        data.setdefault('host', socket.gethostname())
        return supermann.riemann.client.create_pb_object(
            supermann.riemann.riemann_pb2.Event, data)

    def event(self, service, **data):
        event = supermann.riemann.riemann_pb2.Event()
        event.service = service
        event.tags.append('supermann')
        event.tags.extend(data.pop('tags', list()))
        data.setdefault('host', socket.gethostname())
        for name, value in data.items():
            setattr(event, name, value)
        self.queue_events(event)
