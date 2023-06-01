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


def pretty_ctypes_execute_function(function: str, *args):
    """Return a descriptive ctypes function call."""

    def format_item(arg):
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
            item = "&" + format_item(arg._obj)
        else:
            item = format_item(arg)
        items.append(item)
    return f"{function}({', '.join(items)})"
