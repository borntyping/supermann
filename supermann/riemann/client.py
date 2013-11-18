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
        # Set lists by clearing the field and then extending
        # Welcome to the Protocol Buffers library!
        if isinstance(value, (list, tuple)):
            field = getattr(obj, name)
            del field[:]
            field.extend(value)
        else:
            setattr(obj, name, value)
    return obj


class Client(object):
    def __init__(self, host, port):
        self.log = supermann.utils.getLogger(self)
        self.log.info("Sending messages to Riemann at %s:%s", host, port)
        self.host = host
        self.port = port

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def __lshift__(self, data):
        return self.send_event(data)

    def send_event(self, *events):
        message = self.create_message({
            'events': [self.create_event(e) for e in events]
        })
        self.write(message.SerializeToString())
        return message

    def create_event(self, data):
        return create_pb_object(supermann.riemann.riemann_pb2.Event, data)

    def create_message(self, data):
        return create_pb_object(supermann.riemann.riemann_pb2.Msg, data)


class UDPClient(Client):
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def disconnect(self):
        self.socket.close()

    def write(self, message):
        self.socket.sendto(message, (self.host, self.port))
