from __future__ import absolute_import, unicode_literals, print_function

import pytest

from supermann.supervisor.events import Event, Tick, Tick_5


@pytest.fixture
def tick_event():
    return Event({'eventname': 'TICK_5'}, {'when': '1384261590'})


def test_event_creation(tick_event):
    assert isinstance(tick_event, Tick)
    assert isinstance(tick_event, Tick_5)


def test_tick_when_attribute(tick_event):
    assert tick_event.when == tick_event.payload['when'] == "1384261590"
