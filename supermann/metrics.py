"""Actions that send metrics to Riemann"""

from __future__ import absolute_import, unicode_literals

import logging
import socket

import psutil

import supermann.supervisor.events
import supermann.utils


def metric_name(*components):
    return ':'.join(components)


def process_resource_usage(pid, name=None):
    """Returns CPU and memory metrics for a single process"""
    process = psutil.Process(pid)
    if name is None:
        name = process.name
    return ({
        'service': metric_name('process', name, 'cpu'),
        'metric_f': process.get_cpu_percent(),
        'tags': ['supermann', 'supervisor', 'process', 'process_cpu']
    }, {
        'service': metric_name('process', name, 'mem'),
        'metric_f': process.get_memory_percent(),
        'tags': ['supermann', 'supervisor', 'process', 'process_mem']
    })


def supervisor_child_state(name, state):
    """Returns metrics for the current state of a Supervisor child"""
    return [{
        'service': metric_name('process', name, 'state'),
        'state': state,
        'tags': ['supermann', 'supervisor', 'process', 'process_state']
    }]


def monitor_system(instance, event):
    """Returns the systems total CPU and memory usage"""
    return [{
        'service': metric_name('system', 'cpu', 'percent'),
        'metric_f': psutil.cpu_percent(interval=0),
        'tags': ['supermann', 'system', 'system_cpu']
    }, {
        'service': metric_name('system', 'mem', 'percent'),
        'metric_f': psutil.virtual_memory().percent,
        'tags': ['supermann', 'system', 'system_mem']
    }]


def monitor_supervisor(instance, event):
    """Returns resource usage for the supervisord process"""
    return process_resource_usage(instance.supervisor.getPID())


def monitor_supervisor_children(instance, event):
    """Returns state and resource usage for each supervisor child"""
    metrics = list()
    for child in instance.supervisor.getAllProcessInfo():
        if child['statename'] in ("STARTING", "RUNNING"):
            metrics.extend(process_resource_usage(child['pid'], child['name']))
        metrics.extend(supervisor_child_state(child['name'], child['statename']))
    return metrics


def monitor_process_state_change(instance, event):
    """Returns a metric with a processes new state"""
    assert isinstance(event, supermann.supervisor.events.PROCESS_STATE)
    return supervisor_child_state(event.name, event.state)
