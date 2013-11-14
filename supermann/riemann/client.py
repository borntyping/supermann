"""Riemann protocol buffer client"""

from __future__ import absolute_import, unicode_literals, print_function

import socket

import supermann.riemann.riemann_pb2


def create_pb_object(cls, data):
    """Creates a Protocol Buffer object from a dictionary"""
    obj = cls()
    for name, value in data.items():
        # Set lists by clearing the field and then extending
        # Welcome to Python Protocol Buffers! -.-
        if isinstance(value, (list, tuple)):
            field = getattr(obj, name)
            del field[:]
            field.extend(value)
        else:
            setattr(obj, name, value)
    return obj


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __lshift__(self, data):
        return self.send_event(**data)

    def send_event(self, **data):
        """Sends an event and returns the Msg object sent"""
        event = create_pb_object(supermann.riemann.riemann_pb2.Event, data)
        message = create_pb_object(supermann.riemann.riemann_pb2.Msg, {
            'events': [event]
        })
        self.write(message.SerializeToString())
        return message


class UDPClient(Client):
    def __enter__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()

    def write(self, message):
        self.socket.sendto(message, (self.host, self.port))
