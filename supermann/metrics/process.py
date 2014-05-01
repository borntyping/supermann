"""Process metrics"""

from __future__ import absolute_import, unicode_literals

import functools

import supermann.utils


def running_process(function):
    """Decorates a signals.process reciver to only run if the process exists"""
    @functools.wraps(function)
    def wrapper(sender, process, data):
        if process is None:
            log = supermann.utils.getLogger(function)
            log.debug("Process '{0}' does not exist (state: {1})".format(
                data['name'], data['statename']))
        else:
            return function(sender, process, data)
    return wrapper


@running_process
def cpu(sender, process, data):
    sender.riemann.event(
        service='process:{name}:cpu:percent'.format(**data),
        metric_f=process.get_cpu_percent(interval=None))
    sender.riemann.event(
        service='process:{name}:cpu:absolute'.format(**data),
        metric_f=sum(process.get_cpu_times()))


@running_process
def mem(sender, process, data):
    sender.riemann.event(
        service='process:{name}:mem:percent'.format(name=data['name']),
        metric_f=process.get_memory_percent())
    sender.riemann.event(
        service='process:{name}:mem:absolute'.format(name=data['name']),
        metric_f=process.get_memory_info()[0])


@running_process
def fds(sender, process, data):
    sender.riemann.event(
        service='process:{name}:fds'.format(**data),
        metric_f=process.get_num_fds())


def state(sender, process, data):
    sender.riemann.event(
        service='process:{name}:state'.format(**data),
        state=data['statename'])


def uptime(sender, process, data):
    sender.riemann.event(
        service='process:{name}:uptime'.format(**data),
        metric_f=data['stop' if process is None else 'now'] - data['start'])
