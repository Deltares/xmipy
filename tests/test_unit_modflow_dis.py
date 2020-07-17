import os
from xmipy import XmiWrapper
import math
import pytest


def test_set_int(flopy_dis, modflow_lib_path):
    model_path, _ = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)


def test_initialize(flopy_dis, modflow_lib_path):
    model_path, _ = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Run initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)


def test_double_initialize(flopy_dis, modflow_lib_path):
    model_path, _ = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Run initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)

    # Test if initialize fails, if initialize was called a second time
    with pytest.raises(Exception):
        mf6.initialize()


def test_finalize_without_initialize(flopy_dis, modflow_lib_path):
    model_path, _ = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Test if finalize fails, if initialize was not called yet
    with pytest.raises(Exception):
        mf6.finalize()


def test_get_end_time(flopy_dis, modflow_lib_path):
    model_path, sim = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)

    # Get prescribed_end_time from TDIS package
    tdis = sim.get_package("TDIS")
    perioddata = tdis.perioddata.array
    prescribed_end_time = 0
    for perlen, _, _ in perioddata:
        prescribed_end_time += perlen

    actual_end_time = mf6.get_end_time()
    assert math.isclose(prescribed_end_time, actual_end_time)
