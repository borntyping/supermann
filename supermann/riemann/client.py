"""Riemann protocol buffer client"""

from __future__ import absolute_import, unicode_literals

import abc
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
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, port, buffer_events=False):
        self.log = supermann.utils.getLogger(self)
        self.log.info("Sending messages to Riemann at %s:%s", host, port)
        self.host = host
        self.port = port

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def write(self):
        pass

    def send_events(self, *events):
        self.log.debug("Sending {n} events to Riemann at {host}:{port}".format(
            n=len(events), host=self.host, port=self.port))
        self.write(self.create_message({
            'events': map(self.create_event, events)
        }))

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
