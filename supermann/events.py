"""
Supervisor event hierarchy

http://supervisord.org/events.html
"""


class PayloadAttribute(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.payload[self.name]


class Event(object):
    subclasses = dict()

    @classmethod
    def create(cls, headers, payload):
        if headers['eventname'] in cls.subclasses:
            cls = cls.subclasses[headers['eventname']]
        return cls(headers, payload)

    @classmethod
    def register(cls, subclass):
        cls.subclasses[subclass.__name__.upper()] = subclass
        return subclass

    def __init__(self, headers, payload):
        self.headers = headers
        self.payload = payload

    @property
    def eventname(self):
        return self.headers['eventname']

    def __repr__(self):
        return "<{0} {1}>".format(
            self.eventname,
            ' '.join([':'.join(item) for item in self.payload.items()]))


class Process_State(Event):
    name = PayloadAttribute('processname')
    group = PayloadAttribute('groupname')
    from_state = PayloadAttribute('from_state')


class Tick(Event):
    when = PayloadAttribute('when')


@Event.register
class Tick_5(Tick):
    frequency = 5


@Event.register
class Tick_60(Tick):
    frequency = 60


@Event.register
class Tick_3600(Tick):
    frequency = 3600
