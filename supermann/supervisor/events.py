"""
Supervisor event hierarchy

http://supervisord.org/events.html

Event class names are capitalised to match the supervisor documentation.
"""

from __future__ import absolute_import, unicode_literals, print_function


class DictAttribute(object):
    def __init__(self, name, func=None, attribute=None):
        self.name = name
        self.func = func
        self.attribute = attribute

    def __get__(self, instance, owner):
        value = getattr(instance, self.attribute)[self.name]
        return value if self.func is None else self.func(value)


class PayloadAttribute(DictAttribute):
    def __init__(self, name, func=None):
        super(PayloadAttribute, self).__init__(name, func, 'payload')


class HeaderAttribute(DictAttribute):
    def __init__(self, name, func=None):
        super(HeaderAttribute, self).__init__(name, func, 'headers')


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

    ver = HeaderAttribute('ver', int)
    server = HeaderAttribute('server')
    serial = HeaderAttribute('serial', int)
    pool = HeaderAttribute('pool')
    poolserial = HeaderAttribute('poolserial')


class ProcessStateMetaclass(type):
    """Creates the state class attribute on PROCESS_STATE subclasses"""

    def __new__(cls, name, bases, attributes):
        if name != 'PROCESS_STATE':
            attributes['state'] = name.split('_')[-1].lower()
        return type.__new__(cls, name, bases, attributes)


class PROCESS_STATE(Event):
    __metaclass__ = ProcessStateMetaclass

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


class TickMetaclass(type):
    """Creates the frequency class attribute on TICK subclasses"""

    def __new__(cls, name, bases, attributes):
        if name != 'TICK':
            attributes['frequency'] = int(name.split('_')[-1])
        return type.__new__(cls, name, bases, attributes)


class TICK(Event):
    when = PayloadAttribute('when', int)


@Event.register
class TICK_5(TICK):
    pass


@Event.register
class TICK_60(TICK):
    pass


@Event.register
class TICK_3600(TICK):
    pass
