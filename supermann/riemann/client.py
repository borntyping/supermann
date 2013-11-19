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
        self.event_buffer = list()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def send_events(self, *events):
        events = map(self.create_event, events)
        if self.buffer_events:
            self.event_buffer.extend(events)
        else:
            self.write_events(*events)

    def write_events(self, *events):
        return self.write(self.create_message({'events': events}))

    def flush_events(self):
        return self.write_events(*self.event_buffer)

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
