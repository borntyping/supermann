"""
Supervisor event hierarchy

http://supervisord.org/events.html

Event class names are capitalised to match the supervisor documentation.
"""

from __future__ import absolute_import, unicode_literals


class PayloadAttribute(object):
    """An attribute that returns a value from the instance's .payload dict"""

    def __init__(self, name, function=lambda obj: obj):
        self.name = name
        self.function = function

    def __get__(self, instance, owner):
        return instance.payload[self.name]


class Event(object):
    """A Supervisor event

    This is an abstract class, and creating instances of Event will create an
    instance of a subclass when possible (see __new__()). Instances of Event
    will only be created when the event type is unknown."""

    SUBCLASSES = dict()

    @classmethod
    def register(cls, subcls):
        """Registers a subclass that can be used when creating new Events"""
        cls.SUBCLASSES[subcls.__name__] = subcls
        return subcls

    def __new__(cls, headers, payload):
        """If a subclass for this event type exists, use that instead"""
        if headers['eventname'] in cls.SUBCLASSES:
            cls = cls.SUBCLASSES[headers['eventname']]
        return super(Event, cls).__new__(cls)

    def __init__(self, headers, payload):
        self.headers = headers
        self.payload = payload

    def __repr__(self):
        return "<{0} {1}>".format(
            self.headers['eventname'],
            ' '.join([':'.join(item) for item in self.payload.items()]))


class PROCESS_STATE(Event):
    name = PayloadAttribute('processname')
    group = PayloadAttribute('groupname')
    from_state = PayloadAttribute('from_state')


@Event.register
class PROCESS_STATE_STARTING(PROCESS_STATE):
    tries = PayloadAttribute('tries', int)


@Event.register
class PROCESS_STATE_RUNNING(PROCESS_STATE):
    pass


@Event.register
class PROCESS_STATE_BACKOFF(PROCESS_STATE):
    pass


@Event.register
class PROCESS_STATE_STOPPING(PROCESS_STATE):
    pass


@Event.register
class PROCESS_STATE_EXITED(PROCESS_STATE):
    pass


@Event.register
class PROCESS_STATE_STOPPED(PROCESS_STATE):
    pass


@Event.register
class PROCESS_STATE_FATAL(PROCESS_STATE):
    pass


@Event.register
class PROCESS_STATE_UNKNOWN(PROCESS_STATE):
    pass


class TICK(Event):
    when = PayloadAttribute('when')


@Event.register
class TICK_5(TICK):
    frequency = 5


@Event.register
class TICK_60(TICK):
    frequency = 60


@Event.register
class TICK_3600(TICK):
    frequency = 3600
