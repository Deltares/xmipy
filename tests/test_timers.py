import time

import pytest

from xmipy.errors import TimerError
from xmipy.timers.timer import Timer


def test_timer_create_and_run():
    """Create and run a timer"""
    scope_label = "theMethod"
    timer = Timer("aTimer", "Some text with details")
    timer.start(scope_label)
    time.sleep(0.1)
    timer.stop(scope_label)

    value = timer.report_totals()
    assert value > 0.09


def test_timer_start_twice_fails():
    scope_label = "theMethod"
    timer = Timer("aTimer", "Some text with details")
    timer.start(scope_label)

    with pytest.raises(TimerError):
        timer.start(scope_label)


def test_timer_stop_nonexisting_fails():
    timer = Timer("aTimer", "Some text with details")
    with pytest.raises(TimerError):
        timer.stop("imnotthere")


def test_timer_multiple_subtimers():
    scope_label_1 = "methodA"
    scope_label_2 = "methodA"

    timer = Timer("timer", "Some text")

    timer.start(scope_label_1)
    time.sleep(0.1)
    timer.stop(scope_label_1)

    timer.start(scope_label_2)
    time.sleep(0.1)
    timer.stop(scope_label_2)

    value = timer.report_totals()
    assert value > 0.019
