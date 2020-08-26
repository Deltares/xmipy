class Error(Exception):
    """Base class for exceptions in this module."""


class InputError(Error):
    """Exception raised for errors in the input."""


class XMIError(Error):
    """Exception raised for errors returned from the XMI interface."""


class TimerError(Error):
    """Exception raised for errors of the Timer class"""
