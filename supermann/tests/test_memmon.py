from __future__ import absolute_import, unicode_literals

import psutil

import mock
import py.test

import supermann.memmon


@py.test.fixture
def process():
    return mock.NonCallableMock(
        spec=psutil.Process,
        get_memory_info=mock.Mock(return_value=(2048, 4096)))


@py.test.fixture
def sender():
    return mock.Mock()


class TestMemoryMonitor(object):
    def test_from_args(self):
        memmon = supermann.memmon.MemoryMonitor.from_args(
            'large=1GB', 'medium=10MB', 'small=100KB', 'tiny=500')

        assert memmon.processes['large'] == 1*1024*1024*1024
        assert memmon.processes['medium'] == 10*1024*1024
        assert memmon.processes['small'] == 100*1024
        assert memmon.processes['tiny'] == 500

    def test_restart_called(self, process, sender):
        memmon = supermann.memmon.MemoryMonitor.from_args('test=1KB')
        memmon.process(sender=sender, process=process, data={'name': 'test'})
        rpc = sender.supervisor.rpc
        rpc.stopProcess.assert_called_once_with('test', wait=True)
        rpc.startProcess.assert_called_once_with('test', wait=False)

    def test_restart_warning(self, process, sender):
        memmon = supermann.memmon.MemoryMonitor.from_args('test=1KB')
        memmon.log.warning = mock.Mock()
        memmon.process(sender=sender, process=process, data={'name': 'test'})
        memmon.log.warning.assert_called_once_with(
            "Process 'test' reached the memory limit")

    def test_restart_not_called(self, process, sender):
        memmon = supermann.memmon.MemoryMonitor.from_args('test=3KB')
        memmon.process(sender=sender, process=process, data={'name': 'test'})
        assert sender.supervisor.rpc.stopProcess.call_count == 0
        assert sender.supervisor.rpc.startProcess.call_count == 0

    def test_dead_process(self, sender):
        memmon = supermann.memmon.MemoryMonitor.from_args('test=3KB')
        memmon.log.debug = mock.Mock()
        memmon.process(sender=sender, process=None, data={'name': 'test'})
        memmon.log.debug.assert_called_once_with(
            "Process 'test' is not availible")
