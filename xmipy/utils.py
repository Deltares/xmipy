import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def cd(newdir: Path):
    prevdir = Path().cwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)
