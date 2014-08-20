"""Process metrics"""

from __future__ import absolute_import, unicode_literals

import functools

import psutil

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
        metric_f=process.cpu_percent(interval=None))
    sender.riemann.event(
        service='process:{name}:cpu:absolute'.format(**data),
        metric_f=sum(process.cpu_times()))


@running_process
def mem(sender, process, data):
    rss, vms = process.memory_info()
    sender.riemann.event(
        service='process:{name}:mem:virt:absolute'.format(name=data['name']),
        metric_f=vms)
    sender.riemann.event(
        service='process:{name}:mem:rss:absolute'.format(name=data['name']),
        metric_f=rss)
    sender.riemann.event(
        service='process:{name}:mem:rss:percent'.format(name=data['name']),
        metric_f=process.memory_percent())


@running_process
def fds(sender, process, data):
    num_fds = process.num_fds()
    sender.riemann.event(
        service='process:{name}:fds:absolute'.format(**data),
        metric_f=num_fds)


@running_process
def io(sender, process, data):
    io_counters = process.io_counters()
    sender.riemann.event(
        service='process:{name}:io:read_bytes'.format(**data),
        metric_f=io_counters.read_bytes)
    sender.riemann.event(
        service='process:{name}:io:write_bytes'.format(**data),
        metric_f=io_counters.write_bytes)


def state(sender, process, data):
    sender.riemann.event(
        service='process:{name}:state'.format(**data),
        state=data['statename'])


def uptime(sender, process, data):
    sender.riemann.event(
        service='process:{name}:uptime'.format(**data),
        metric_f=data['stop' if process is None else 'now'] - data['start'])
