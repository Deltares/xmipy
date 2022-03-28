"""Definition of Timer

Adapted from https://pypi.org/project/codetiming/.
"""

import logging
import math
import time

from xmipy.errors import TimerError
from xmipy.timers.timers import Timers

logger = logging.getLogger(__name__)


class Timer:
    """Time your code using a class, context manager, or decorator"""

    def __init__(self, name: str, text: str):
        self.name = name
        self.timers = Timers()
        self._start_time: dict[str, float] = {}
        self.text = text
        self.last = math.nan

    def start(self, fn_name: str) -> None:
        """Start a new timer"""
        if fn_name in self._start_time:
            raise TimerError(
                f"Timer for {fn_name} is already running. Use .stop() to stop it"
            )

        self._start_time[fn_name] = time.perf_counter()

    def stop(self, fn_name: str) -> float:
        """Stop the timer, and report the elapsed time"""
        if fn_name not in self._start_time:
            raise TimerError(
                f"Timer for {fn_name} is not running yet. Use .start() to start it"
            )

        # Calculate elapsed time
        self.last = time.perf_counter() - self._start_time[fn_name]
        del self._start_time[fn_name]

        # Report elapsed time
        attributes = {
            "name": self.name,
            "fn_name": fn_name,
            "milliseconds": self.last * 1000,
            "seconds": self.last,
            "minutes": self.last / 60,
        }
        logger.debug(self.text.format(self.last, **attributes))
        self.timers.add(fn_name, self.last)

        return self.last

    def report_totals(self) -> float:
        totals = {}
        for fn_name in self.timers:
            totals[fn_name] = self.timers.total(fn_name)

        total = 0.0
        for fn_name, seconds in sorted(totals.items(), key=lambda item: item[1]):
            logger.info(
                f"Total elapsed time for {self.name}.{fn_name}: {seconds:0.4f} seconds"
            )
            total += seconds
        return total
