"""Actions that send metrics to Riemann"""

from __future__ import absolute_import, unicode_literals

import logging
import socket

import psutil

import supermann.supervisor.events
import supermann.utils


def metric_name(*components):
    return ':'.join(components)


def usage(pid, name=None):
    """Returns CPU and memory metrics for a single process"""
    process = psutil.Process(pid)
    if name is None:
        name = process.name
    return [{
        'service': metric_name('process', name, 'cpu'),
        'metric_f': process.get_cpu_percent(),
        'tags': ['supermann', 'supervisor', 'process', 'process_cpu']
    }, {
        'service': metric_name('process', name, 'mem'),
        'metric_f': process.get_memory_percent(),
        'tags': ['supermann', 'supervisor', 'process', 'process_mem']
    }]


def state(name, state):
    """Returns metrics for the current state of a Supervisor child"""
    return [{
        'service': metric_name('process', name, 'state'),
        'state': state,
        'tags': ['supermann', 'supervisor', 'process', 'process_state']
    }]


def monitor_system(instance, event):
    """Returns the systems total CPU and memory usage"""
    instance.metric('system:cpu:percent', psutil.cpu_percent(interval=0))
    instance.metric('system:mem:percent', psutil.virtual_memory().percent)
    instance.metric('system:mem:absolute', psutil.virtual_memory().used)


def monitor_supervisor(instance, event):
    """Returns resource usage for the supervisord process"""
    instance.queue_events(*usage(instance.supervisor.getPID()))


def monitor_supervisor_children(instance, event):
    """Returns state and resource usage for each supervisor child"""
    for child in instance.supervisor.getAllProcessInfo():
        instance.queue_events(*state(child['name'], child['statename']))
        if child['statename'] in ("STARTING", "RUNNING"):
            instance.queue_events(*usage(child['pid'], child['name']))

def monitor_process_state_change(instance, event):
    """Returns a metric with a processes new state"""
    assert isinstance(event, supermann.supervisor.events.PROCESS_STATE)
    instance.queue_events(*state(event.name, event.state))
