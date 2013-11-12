"""
Supervisor event hierarchy

http://supervisord.org/events.html

Event class names are capitalised to match the supervisor documentation.
"""

from __future__ import absolute_import, unicode_literals


class PayloadAttribute(object):
    """An attribute that returns a value from the instance's .payload dict"""

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.payload[self.name]


class Event(object):
    """A Supervisor event

    This is an abstract class, and creating instances of Event will create an
    instance of a subclass when possible (see __new__()). Events of an unknown
    type will use the UnknownEvent subclass."""

    SUBCLASSES = dict()
    DEFAULT_SUBCLASS = UnknownEvent

    @classmethod
    def register(cls, subcls):
        """Registers a subclass that can be used when creating new Events"""
        cls.SUBCLASSES[subcls.__name__.upper()] = subcls
        return subcls

    def __new__(cls, headers, payload):
        """If a subclass for this event type exists, use that instead"""
        try:
            cls = cls.SUBCLASSES[headers['eventname']]
        except KeyError:
            cls = cls.DEFAULT_SUBCLASS
        return object.__new__(cls, headers, payload)

    def __init__(self, headers, payload):
        self.headers = headers
        self.payload = payload

    def __repr__(self):
        return "<{0} {1}>".format(
            self.headers['eventname'], self.__repr_payload__())

    def __repr_payload__(self):
        return ' '.join([':'.join(item) for item in self.payload.items()])


class UnknownEvent(Event):
    pass


@Event.register
class PROCESS_STATE(Event):
    name = PayloadAttribute('processname')
    group = PayloadAttribute('groupname')
    from_state = PayloadAttribute('from_state')


class Tick(Event):
    when = PayloadAttribute('when')


@Event.register
class TICK_5(Tick):
    frequency = 5


@Event.register
class TICK_60(Tick):
    frequency = 60


@Event.register
class TICK_3600(Tick):
    frequency = 3600
