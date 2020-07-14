"""Definition of Timer

Adapted from https://pypi.org/project/codetiming/.
"""

# Standard library imports
import math
import time
from contextlib import ContextDecorator
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Optional

# Codetiming imports
from codetiming._timers import Timers


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


@dataclass
class Timer:
    """Time your code using a class, context manager, or decorator"""

    def __init__(self, text="Elapsed time: {:0.4f} seconds", logger=print):
        self.timers = Timers()
        self._start_time = {}
        self.text = text
        self.logger = logger
        self.last = math.nan

    def start(self, name) -> None:
        """Start a new timer"""
        if self._start_time[name] is not None:
            raise TimerError(
                f"Timer for {name} is already running. Use .stop() to stop it"
            )

        self._start_time[name] = time.perf_counter()

    def stop(self, name) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time[name] is None:
            raise TimerError(
                f"Timer for {name} is not running yet. Use .start() to start it"
            )

        # Calculate elapsed time
        self.last = time.perf_counter() - self._start_time[name]
        self._start_time[name] = None

        # Report elapsed time
        if self.logger:
            attributes = {
                "name": self.name,
                "milliseconds": self.last * 1000,
                "seconds": self.last,
                "minutes": self.last / 60,
            }
            self.logger(self.text.format(self.last, **attributes))
        if self.name:
            self.timers.add(self.name, self.last)

        return self.last
