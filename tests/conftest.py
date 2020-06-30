import pytest
import pymake
import platform
import os
from pathlib import Path


@pytest.fixture(scope="session")
def get_shared_object_path():
    sysinfo = platform.system()
    if sysinfo.lower() == "windows":
        lib_name = "libmf6.dll"
    else:
        lib_name = "libmf6.so"
    return str(Path(__file__).parent / "bin" / lib_name)

