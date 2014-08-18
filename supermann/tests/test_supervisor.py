from __future__ import absolute_import, unicode_literals

import os
import StringIO

import mock
import py.test

import supermann.supervisor


def local_file(name):
    return os.path.join(os.path.dirname(__file__), name)


@py.test.fixture
def listener():
    with open(local_file('supervisor.txt'), 'r') as f:
        return supermann.supervisor.EventListener(
            stdin=StringIO.StringIO(f.read()),
            stdout=StringIO.StringIO(),
            reserve_stdin=False,
            reserve_stdout=False)


class TestEventListener(object):
    def test_parse(self):
        line = "processname:cat groupname:cat from_state:STARTING pid:2766"
        payload = supermann.supervisor.EventListener.parse(line)
        assert payload['processname'] == 'cat'

    def test_output(self, listener):
        listener.ready()
        listener.wait()
        listener.ok()
        assert listener.stdout.getvalue() == "READY\nRESULT 2\nOK"

    def test_wait(self, listener):
        assert isinstance(listener.wait(), supermann.supervisor.Event)

    def test_event(self, listener):
        event = listener.wait()
        assert event.headers['ver'] == '3.0'
        assert event.payload['pid'] == '2766'


class TestSupervisor(object):
    @mock.patch.dict('os.environ', {'SUPERVISOR_SERVER_URL': '-'})
    @mock.patch('supervisor.childutils.getRPCInterface')
    def test_rpc_property(self, getRPCInterface):
        assert supermann.supervisor.Supervisor().rpc
