"""System metrics"""

from __future__ import absolute_import, unicode_literals

import os

import psutil


def cpu(self, event):
    """Returns the systems total CPU and memory usage"""
    self.riemann.event(
        service='system:cpu:percent',
        metric_f=psutil.cpu_percent(interval=None))


def mem(self, event):
    mem = psutil.virtual_memory()
    self.riemann.event(service='system:mem:percent', metric_f=mem.percent)
    self.riemann.event(service='system:mem:absolute', metric_f=mem.used)


def swap(self, event):
    swap = psutil.swap_memory()
    self.riemann.event(service='system:swap:percent', metric_f=swap.percent)
    self.riemann.event(service='system:swap:absolute', metric_f=swap.used)


def load(self, event):
    load1, load5, load15 = os.getloadavg()
    self.riemann.event(service='system:load:1min', metric_f=load1)
    self.riemann.event(service='system:load:5min', metric_f=load5)
    self.riemann.event(service='system:load:15min', metric_f=load15)
