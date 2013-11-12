from __future__ import absolute_import, unicode_literals, print_function

import pytest

from supermann.supervisor.events import (
    Event, TICK, TICK_5, PROCESS_STATE_STARTING, PROCESS_STATE_RUNNING)


@pytest.fixture
def tick_5():
    return Event({'eventname': 'TICK_5'}, {'when': '1384261590'})


@pytest.fixture
def process_state_starting():
    return Event({'eventname': 'PROCESS_STATE_STARTING'}, {
        'from_state': 'STOPPED',
        'processname': 'supermann',
        'groupname': 'supermann',
        'tries': 0
    })


@pytest.fixture
def process_state_running():
    return Event({'eventname': 'PROCESS_STATE_RUNNING'}, {
        'from_state': 'STOPPED',
        'processname': 'supermann',
        'groupname': 'supermann',
        'pid': 14275
    })


class TestEventTypes(object):
    def test_process_state_starting(self, process_state_starting):
        assert isinstance(process_state_starting, PROCESS_STATE_STARTING)

    def test_process_state_running(self, process_state_running):
        assert isinstance(process_state_running, PROCESS_STATE_RUNNING)

    def test_tick_5(self, tick_5):
        assert isinstance(tick_5, TICK)
        assert isinstance(tick_5, TICK_5)


class TestEventClasses(object):
    def test_tick_when_attribute(self, tick_5):
        assert tick_5.when == tick_5.payload['when'] == "1384261590"

    def test_process_state_starting(self, process_state_starting):
        assert process_state_starting.from_state == 'STOPPED'
        assert process_state_starting.name == 'supermann'
        assert process_state_starting.group == 'supermann'
        assert process_state_starting.tries == 0

    def test_process_state_starting_types(self, process_state_starting):
        assert isinstance(process_state_starting.tries, int)
