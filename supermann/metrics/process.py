"""Metrics reported for each process running under Supervisor"""

from __future__ import absolute_import, unicode_literals, division

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


def get_nofile_limit(pid):
    """Returns the NOFILE limit for a given PID

    :param int pid: The PID of the process
    :returns: (*int*) The NOFILE limit
    """
    with open('/proc/%s/limits' % pid, 'r') as f:
        for line in f:
            if line.startswith('Max open files'):
                return int(line.split()[4])
    raise RuntimeError('Could not find "Max open files" limit')


@running_process
def cpu(sender, process, data):
    """CPU utilisation as a percentage and total CPU time in seconds

    - ``process:{name}:cpu:percent``
    - ``process:{name}:cpu:absolute``
    """
    sender.riemann.event(
        service='process:{name}:cpu:percent'.format(**data),
        metric_f=process.cpu_percent(interval=None))
    sender.riemann.event(
        service='process:{name}:cpu:absolute'.format(**data),
        metric_f=sum(process.cpu_times()))


@running_process
def mem(sender, process, data):
    """Total virtual memory, total RSS memory, RSS utilisation as percentage

    - ``process:{name}:mem:virt:absolute``
    - ``process:{name}:mem:rss:absolute``
    - ``process:{name}:mem:rss:percent``
    """
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
    """Number of file descriptors a process is using it's hard limit

    - ``process:{name}:fds:absolute``
    - ``process:{name}:fds:percent``
    """
    num_fds = process.num_fds()
    sender.riemann.event(
        service='process:{name}:fds:absolute'.format(**data),
        metric_f=num_fds)
    sender.riemann.event(
        service='process:{name}:fds:percent'.format(**data),
        metric_f=(num_fds / get_nofile_limit(process.pid)) * 100)


@running_process
def io(sender, process, data):
    """Bytes read and written by a process

    - ``process:{name}:io:read:bytes``
    - ``process:{name}:io:write:bytes``
    """
    io_counters = process.io_counters()
    sender.riemann.event(
        service='process:{name}:io:read:bytes'.format(**data),
        metric_f=io_counters.read_bytes)
    sender.riemann.event(
        service='process:{name}:io:write:bytes'.format(**data),
        metric_f=io_counters.write_bytes)


def state(sender, process, data):
    """The process state that Supervisor reports

    - ``process:{name}:state``
    """
    sender.riemann.event(
        service='process:{name}:state'.format(**data),
        state=data['statename'])


def uptime(sender, process, data):
    """The time in seconds Supervisor reports the process has been running

    - ``process:{name}:uptime``
    """
    sender.riemann.event(
        service='process:{name}:uptime'.format(**data),
        metric_f=data['stop' if process is None else 'now'] - data['start'])
