import os
from contextlib import contextmanager
from pathlib import Path
import ctypes

import numpy as np


@contextmanager
def cd(newdir: Path):
    prevdir = Path().cwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)


def repr_function_call(function: str, *args) -> str:
    """Return a descriptive ctypes function call.

    Parameters
    ----------
    function : str
        Name of function.
    *args : tuple
        Zero or more arguments, usally based on ctypes.
    """

    def format_arg(arg) -> str:
        if isinstance(arg, (ctypes.Array, ctypes.c_char_p)):
            return f"{arg.__class__.__name__}({arg.value!r})"
        elif isinstance(arg, np.ctypeslib._ndptr):
            return arg.__class__.__name__
        elif isinstance(arg, ctypes._Pointer):
            return "*" + repr(arg.contents)
        elif isinstance(arg, ctypes._SimpleCData):
            return repr(arg)
        else:
            return repr(arg)

    items = []
    for arg in args:
        if hasattr(arg, "_obj"):
            # Format byref() with "&" prefix
            item = "&" + format_arg(arg._obj)
        else:
            item = format_arg(arg)
        items.append(item)
    return f"{function}({', '.join(items)})"
