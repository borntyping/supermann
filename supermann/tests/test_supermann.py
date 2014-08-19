from __future__ import absolute_import, unicode_literals

import datetime
import time
import os

from supermann import Supermann, signals
from supermann.metrics import system, process
from supermann.supervisor import Event

import mock
import py.test


def timestamp():
    return time.mktime(datetime.datetime.now().timetuple())


def getAllProcessInfo():
    """Returns some fake process data

    The 'running' process uses the current PID so that the metrics have a
    process to collect data from. The 'stopped' process uses PID 0, which
    Supervisor uses to represent a non-existent process.
    """
    yield {
        'pid': os.getpid(),
        'name': 'this-process',
        'statename': 'RUNNING',

        'start': timestamp(),
        'stop': timestamp(),
        'now': timestamp(),
    }
    yield {
        'pid': 0,
        'name': 'dead-process',
        'statename': 'STOPPED',

        'start': timestamp(),
        'stop': timestamp(),
        'now': timestamp(),
    }


@py.test.fixture
@mock.patch('supermann.supervisor.Supervisor', autospec=True)
@mock.patch('riemann_client.transport.TCPTransport', autospec=True)
def supermann_instance(riemann_client_class, supervisor_class):
    instance = Supermann(None, None)
    instance.supervisor.configure_mock(**{
        # At least one process must be visible for the process metrics to run
        'rpc.getAllProcessInfo': mock.Mock(wraps=getAllProcessInfo),

        # The information in each event isn't important to Supermann
        'run_forever.return_value': [Event({}, {}), Event({}, {})]
    })

    # System metrics
    instance.connect(signals.event, system.cpu)
    instance.connect(signals.event, system.swap)
    instance.connect(signals.event, system.mem)
    instance.connect(signals.event, system.load)
    instance.connect(signals.event, system.load_scaled)
    instance.connect(signals.event, system.uptime)

    # Process metrics
    instance.connect(signals.process, process.cpu)
    instance.connect(signals.process, process.mem)
    instance.connect(signals.process, process.fds)
    instance.connect(signals.process, process.io)
    instance.connect(signals.process, process.state)
    instance.connect(signals.process, process.uptime)

    # 'Run' Supermann using the events in the Supervisor mock
    instance.run()

    return instance


def test_riemann_client(supermann_instance):
    assert supermann_instance.riemann.transport.connect.called


def test_one_message_per_event(supermann_instance):
    assert len(supermann_instance.riemann.transport.send.call_args_list) == 2


def test_supervisor_rpc_called(supermann_instance):
    assert supermann_instance.supervisor.rpc.getAllProcessInfo.called
