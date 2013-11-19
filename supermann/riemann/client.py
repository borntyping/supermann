"""Riemann protocol buffer client"""

from __future__ import absolute_import, unicode_literals

import logging
import socket

import supermann.riemann.riemann_pb2
import supermann.utils


def create_pb_object(cls, data):
    """Creates a Protocol Buffer object from a dictionary"""
    obj = cls()
    for name, value in data.items():
        if isinstance(value, (list, tuple)):
            getattr(obj, name).extend(value)
        else:
            setattr(obj, name, value)
    return obj


class Client(object):
    def __init__(self, host, port, buffer_events=False):
        self.log = supermann.utils.getLogger(self)
        self.log.info("Sending messages to Riemann at %s:%s", host, port)
        self.host = host
        self.port = port

        self.buffer_events = buffer_events
        self.clear_events()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def send_events(self, *events):
        events = map(self.create_event, events)
        self.event_buffer.extend(events)
        if not self.buffer_events:
            self.flush_events()

    def write_events(self, *events):
        self.log.debug("Sending {n} events to Riemann at {host}:{port}".format(
            n=len(events), host=self.host, port=self.port))
        self.write(self.create_message({'events': events}))

    def flush_events(self):
        self.write_events(*self.event_buffer)
        self.clear_events()

    def clear_events(self):
        self.event_buffer = list()

    def create_event(self, data):
        data.setdefault('host', socket.gethostname())
        return create_pb_object(supermann.riemann.riemann_pb2.Event, data)

    def create_message(self, data):
        return create_pb_object(supermann.riemann.riemann_pb2.Msg, data)


class UDPClient(Client):
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def disconnect(self):
        self.socket.close()

    def write(self, message):
        self.socket.sendto(message.SerializeToString(), (self.host, self.port))
        return message
