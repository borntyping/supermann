"""Actions that send metrics to Riemann"""

from __future__ import absolute_import, unicode_literals

import logging

import socket

import psutil


import supermann.supervisor.events
import supermann.utils


class Metric(object):
    def __init__(self, instance):
        self.log = supermann.utils.getLogger(self)
        self.supermann = instance

    def __call__(self, event):
        raise NotImplementedError


class ProcessMetric(Metric):
    def monitor_process(self, name, pid):
        process = psutil.Process(pid)
        self.supermann.riemann.send_events({
            'service': 'process:{name}:cpu'.format(name=name),
            'metric_f': process.get_cpu_percent(),
            'tags': ['supermann', 'supervisor', 'process', 'process_cpu']
        }, {
            'service': 'process:{name}:mem'.format(name=name),
            'metric_f': process.get_memory_percent(),
            'tags': ['supermann', 'supervisor', 'process', 'process_mem']
        })


class ProcessResourceUsage(ProcessMetric):
    def __call__(self, event):
        for child in self.supermann.supervisor.processes():
            self.log.debug("Monitoring process {name}({pid})".format(**child))
            if child['pid'] == 0:
                return
            self.monitor_process(child['name'], child['pid'])


class ProcessStateChange(Metric):
    def __call__(self, event):
        assert isinstance(event, supermann.supervisor.events.PROCESS_STATE)
        self.log.debug("Process {0} changed state from {1} to {2}".format(
            event.name, event.state, event.from_state))
        self.supermann.riemann.send_events({
            'service': 'process:{name}:state'.format(name=event.name),
            'state': event.state,
            'tags': ['supermann', 'supervisor', 'process', 'process_state']
        })


class SupervisorMonitor(ProcessMetric):
    def __call__(self, event):
        self.monitor_process('supervisor', self.supermann.supervisor.pid())
        self.supermann.riemann.send_events({
            'service': 'supervisor:tick',
            'state': 'ok',
            'time': event.when,
            'metric_f': event.serial,
            'tags': ['supermann', 'supervisor', 'supervisor_tick']
        })


class SystemResourceUsage(Metric):
    def __call__(self, event):
        """Monitors the system's CPU and memory percentages"""
        self.supermann.riemann.send_events({
            'service': 'system:cpu:percent',
            'metric_f': psutil.cpu_percent(interval=0),
            'tags': ['supermann', 'system', 'system_cpu']
        }, {
            'service': 'system:mem:percent',
            'metric_f': psutil.virtual_memory().percent,
            'tags': ['supermann', 'system', 'system_mem']
        })
