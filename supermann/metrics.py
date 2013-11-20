"""Actions that send metrics to Riemann"""

from __future__ import absolute_import, unicode_literals

import logging

import socket

import psutil


import supermann.supervisor.events
import supermann.utils


def metric_name(*components):
    return ':'.join(components)


def process_metrics(pid, name=None):
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


def process_state_change(instance, event):
    assert isinstance(event, supermann.supervisor.events.PROCESS_STATE)
    return [{
        'service': metric_name('process', event.name, 'state'),
        'state': event.state,
        'tags': ['supermann', 'supervisor', 'process', 'process_state']
    }]


def monitor_system(instance, event):
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
    return process_metrics(instance.supervisor.getPID())


def monitor_supervisor_children(instance, event):
    metrics = list()
    for child in instance.supervisor.getAllProcessInfo():
        metrics.extend(process_metrics(child['pid'], child['name']))
    return metrics
