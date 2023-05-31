"""Logger module."""

__all__ = ["get_logger", "show_logger_message"]

import logging
import sys
from logging import Logger
from contextlib import contextmanager
from typing import Union


def get_logger(name: str, level: Union[str, int] = 0):
    """Return a named logger.

    Parameters
    ----------
    name : str
        Logger name.
    logger_level : str, int, optional
        Logger level, default 0 ("NOTSET"). Accepted values are
        "DEBUG" (10), "INFO" (20), "WARNING" (30), "ERROR" (40) or
        "CRITICAL" (50).

    Returns
    -------
    Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


@contextmanager
def show_logger_message(
    logger: Logger, level: int = logging.INFO, ignore_disabled: bool = False
):
    """Context manager to show logger messages at and above a given level.

    Parameters
    ----------
    logger : Logger
        Logger instance.
    level : int, optional
        Logger level threshold to show messages, default 20 ("INFO").
    ignore_disabled : bool, default False
        If True, disabled loggers may still emit messages. If False (default),
        disabled loggers never emit messages.
    """
    not_enabled = not logger.isEnabledFor(level)
    if not_enabled:
        prev_level = logger.level
        logger.setLevel(level)
    toggle_disabled = logger.disabled and ignore_disabled
    if toggle_disabled:
        logger.disabled = False
    yield
    if not_enabled:
        logger.setLevel(prev_level)
    if toggle_disabled:
        logger.disabled = True
