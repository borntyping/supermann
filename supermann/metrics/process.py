"""Process metrics"""

from __future__ import absolute_import, unicode_literals

import psutil

import supermann.supervisor.events

def cpu(self, process):
    self.riemann.event(
        service='process:{name}:cpu:percent'.format(name=process.name),
        metric_f=process.get_cpu_percent())

def mem(self, event):
    self.riemann.event(
        service='process:{name}:mem:percent'.format(name=process.name),
        metric_f=process.get_memory_percent())
