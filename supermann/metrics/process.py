"""Process metrics"""

from __future__ import absolute_import, unicode_literals

import functools

import supermann.utils


def running_process(function):
    """Decorates a signals.process reciver to only run if the process exists"""
    @functools.wraps(function)
    def wrapper(sender, process, **data):
        if process:
            return function(sender, process, **data)
        log = supermann.utils.getLogger(function)
        log.warn("Process {name} does not exist ({statename})".format(**data))
    return wrapper


@running_process
def cpu(sender, process, name, **data):
    sender.riemann.event(
        service='process:{name}:cpu:percent'.format(name=name),
        metric_f=process.get_cpu_percent())


@running_process
def mem(sender, process, name, **data):
    sender.riemann.event(
        service='process:{name}:mem:percent'.format(name=name),
        metric_f=process.get_memory_percent())


def state(sender, process, name, **data):
    sender.riemann.event(
        service='process:{name}:state'.format(name=name),
        state=data['statename'])
