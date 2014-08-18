from __future__ import absolute_import, unicode_literals

import supermann
import supermann.signals
import supermann.metrics.system

import mock
import py.test


@py.test.fixture
@mock.patch('supermann.supervisor.Supervisor')
@mock.patch('riemann_client.client.QueuedClient')
def supermann_instance(supervisor_class, riemann_client_class):
    instance = supermann.Supermann(None, None)
    instance.connect(supermann.signals.event, supermann.metrics.system.cpu)
    instance.connect(supermann.signals.event, supermann.metrics.system.mem)
    instance.connect(supermann.signals.event, supermann.metrics.system.swap)
    instance.connect(supermann.signals.event, supermann.metrics.system.load)
    return instance


def test_events_created(supermann_instance):
    supermann.signals.event.send(supermann_instance, event=None)
    assert supermann_instance.riemann.event.called


def test_number_of_events_created(supermann_instance):
    """Checks that there are at least as many events as metrics"""
    supermann.signals.event.send(supermann_instance, event=None)
    assert len(supermann_instance.riemann.event.call_args_list) >= 4
