import os
from xmipy import XmiWrapper
import math
import pytest


def test_set_int(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)
    mf6.set_int("ISTDOUTTOFILE", 0)


def test_initialize(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Run initialize
    mf6.initialize()


def test_double_initialize(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Run initialize
    mf6.initialize()

    # Test if initialize fails, if initialize was called a second time
    with pytest.raises(Exception):
        mf6.initialize()


def test_finalize_without_initialize(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Test if finalize fails, if initialize was not called yet
    with pytest.raises(Exception):
        mf6.finalize()


def test_get_start_time(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    # prescribed_start_time for modflow models is always 0
    prescribed_start_time = 0.0

    actual_start_time = mf6.get_start_time()
    assert math.isclose(prescribed_start_time, actual_start_time)


def test_get_end_time(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    prescribed_end_time = 0.0
    for perlen, _, _ in flopy_dis.tdis_rc:
        prescribed_end_time += perlen

    actual_end_time = mf6.get_end_time()
    assert math.isclose(prescribed_end_time, actual_end_time)


def test_update(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    # Advance model by single time step
    mf6.update()


def test_get_current_time(flopy_dis, modflow_lib_path):
    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    # Advance model by single time step
    mf6.update()

    # prescribed_start_time for modflow models is always 0
    start_time = 0.0

    perlen, nstp, tsmult = flopy_dis.tdis_rc[0]

    if math.isclose(tsmult, 1):
        prescribed_current_time = start_time + perlen / nstp
    else:
        prescribed_current_time = start_time + perlen * (tsmult - 1.0) / (
            tsmult ** nstp - 1.0
        )

    actual_current_time = mf6.get_current_time()

    assert math.isclose(prescribed_current_time, actual_current_time)


def test_get_value_ptr_sln(flopy_dis, modflow_lib_path):
    """`flopy_dis` sets constant head values.
       This test checks if these can be properly extracted with origin="SLN"."""

    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    stress_period_data = flopy_dis.stress_period_data
    ncol = flopy_dis.ncol

    mf6.update()
    actual_head = mf6.get_value_ptr("SLN_1/X")

    for cell_id, presciped_head in stress_period_data:
        layer, row, column = cell_id
        head_index = column + row * ncol
        assert math.isclose(presciped_head, actual_head[head_index])


def test_get_value_ptr_modelname(flopy_dis, modflow_lib_path):
    """`flopy_dis` sets constant head values.
       This test checks if these can be properly extracted with origin=modelname."""

    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    stress_period_data = flopy_dis.stress_period_data
    ncol = flopy_dis.ncol

    mf6.update()
    actual_head = mf6.get_value_ptr(flopy_dis.model_name + "/X")

    for cell_id, presciped_head in stress_period_data:
        layer, row, column = cell_id
        head_index = column + row * ncol
        assert math.isclose(presciped_head, actual_head[head_index])


def test_get_var_grid(flopy_dis, modflow_lib_path):
    """Tests if the the grid type can be extracted"""

    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    # TODO: Find a better way to get the grid id than hardcoding one variable
    grid_id = mf6.get_var_grid(flopy_dis.model_name + " NPF/K11")

    # Only one model is defined => grid_id should be 1
    assert grid_id == 1


def test_get_grid_type(flopy_dis, modflow_lib_path):
    """Tests if the the grid type can be extracted"""

    os.chdir(flopy_dis.sim_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    # TODO: Find a better way to get the grid id than hardcoding one variable
    grid_id = mf6.get_var_grid(flopy_dis.model_name + " NPF/K11")
    grid_type = mf6.get_grid_type(grid_id)

    assert grid_type == "rectilinear"
