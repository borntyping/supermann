"""Supermann actions"""

from __future__ import absolute_import, unicode_literals

import logging
import socket

import psutil

import supermann.utils


class Action(object):
    def __init__(self, instance):
        self.log = supermann.utils.getLogger(self)
        self.supermann = instance

    def __call__(self, event):
        self.log.debug("Sending metrics due to a {event} event".format(event=event.eventname))
        metrics = self.metrics(event)
        for metric in metrics:
            # This ensures all metrics have a hostname set
            # Metrics with no hostname are bad...
            metric.setdefault('host', socket.gethostname())
        self.supermann.riemann.send_event(*metrics)


class SupervisorMonitorAction(Action):
    def metrics(self, event):
        return [{
            'service': 'supervisor:tick',
            'state': 'ok',
            'time': event.when,
            'metric_f': event.serial,
            'tags': ['supermann', 'supervisor', 'supervisor_tick']
        }]


class ProcessMonitorAction(Action):
    def metrics(self, event):
        metrics = []
        processes = self.supermann.parent.get_children()

        for process in processes:
            self.log.debug("Monitoring process {name}".format(name=process.name))
            metrics.append({
                'service': 'process:{name}:cpu'.format(name=process.name),
                'metric_f': process.get_cpu_percent(),
                'tags': ['supermann', 'supervisor', 'process', 'process_cpu']
            })
            metrics.append({
                'service': 'process:{name}:mem'.format(name=process.name),
                'metric_f': process.get_memory_percent(),
                'tags': ['supermann', 'supervisor', 'process', 'process_mem']
            })
        return metrics


class SystemMonitorAction(Action):
    def metrics(self, event):
        """Monitors the system's CPU and memory percentages"""
        return [{
            'service': 'system:cpu:percent',
            'metric_f': psutil.cpu_percent(interval=0),
            'tags': ['supermann', 'system', 'system_cpu']
        }, {
            'service': 'system:mem:percent',
            'metric_f': psutil.virtual_memory().percent,
            'tags': ['supermann', 'system', 'system_mem']
        }]


class ProcessStateAction(Action):
    def metrics(self, event):
        return [{
            'service': 'process:{name}:state'.format(name=event.name),
            'state': event.state,
            'tags': ['supermann', 'supervisor', 'process', 'process_state']
        }]
