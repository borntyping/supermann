"""Process metrics"""

from __future__ import absolute_import, unicode_literals

import psutil

def cpu(sender, process, name, **data):
    sender.riemann.event(
        service='process:{name}:cpu:percent'.format(name=name),
        metric_f=process.get_cpu_percent())

def mem(sender, process, name, **data):
    sender.riemann.event(
        service='process:{name}:mem:percent'.format(name=name),
        metric_f=process.get_memory_percent())

def state(sender, process, name, **data):
    sender.riemann.event(
        service='process:{name}:state'.format(name=name),
        state=data['statename'])
