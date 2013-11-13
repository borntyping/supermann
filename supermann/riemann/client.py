"""Riemann protocol buffer client"""

from __future__ import absolute_import, unicode_literals

import socket

import supermann.riemann.riemann_pb2

from supermann.riemann.riemann_pb2 import State, Query, Attribute

__all__ = ['State', 'Event', 'Query', 'Msg', 'Attribute']


class ProtocolBufferProxy(object):
    def set_repeated(self, name, values):
        """Sets a repeated attribute if it is present"""
        getattr(self.obj, name).extend(values)

    def set_default(self, name, value):
        """Set an attribute that may be overridden by set_values()"""
        setattr(self.obj, name, value)

    def set_values(self, data):
        """Transfers attributes from a dict to the protocol buffer object"""
        for name, value in data.items():
            setattr(self.obj, name, value)


class Event(ProtocolBufferProxy):
    def __init__(self, **data):
        self.obj = supermann.riemann.riemann_pb2.Event()
        self.set_repeated('tags', data.pop('tags', []))
        self.set_repeated('attributes', data.pop('attributes', []))
        self.set_default('host', socket.gethostname())
        self.set_values(data)


class Msg(ProtocolBufferProxy):
    def __init__(self, **data):
        self.obj = supermann.riemann.riemann_pb2.Msg()
        self.set_repeated('states', [s.obj for s in data.pop('states', [])])
        self.set_repeated('events', [e.obj for e in data.pop('events', [])])
        self.set_values(data)


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __lshift__(self, data):
        self.send_event(data)

    def send_event(self, **data):
        return self.send_message(events=[Event(**data)])

    def send_message(self, **data):
        return self.send_object(Msg(**data))

    def send_object(self, obj):
        self.write(obj.obj.SerializeToString())
        return obj


class UDPClient(Client):
    def __enter__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()

    def write(self, message):
        self.socket.sendto(message, (self.host, self.port))
