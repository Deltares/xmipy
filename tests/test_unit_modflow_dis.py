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


def test_get_start_time(flopy_dis, modflow_lib_path):
    model_path, sim = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)

    # prescribed_start_time for modflow models is always 0
    prescribed_start_time = 0.0

    actual_start_time = mf6.get_start_time()
    assert math.isclose(prescribed_start_time, actual_start_time)


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
    prescribed_end_time = 0.0
    for perlen, _, _ in perioddata:
        prescribed_end_time += perlen

    actual_end_time = mf6.get_end_time()
    assert math.isclose(prescribed_end_time, actual_end_time)


def test_update(flopy_dis, modflow_lib_path):
    model_path, sim = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)

    # Advance model by single time step
    mf6.update()


def test_get_current_time(flopy_dis, modflow_lib_path):
    model_path, sim = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)

    # Advance model by single time step
    mf6.update()

    # prescribed_start_time for modflow models is always 0
    start_time = 0.0

    # Get prescribed_end_time from TDIS package
    tdis = sim.get_package("TDIS")
    perioddata = tdis.perioddata.array
    perlen, nstp, tsmult = perioddata[0]

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

    model_path, sim = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)

    model = sim.get_model(sim.name)
    chd = model.get_package("chd_0")
    stress_period_data = chd.stress_period_data.array[0]

    # TODO: Refactor this as soon as `get_var_grid` is implemented
    dis = model.get_package("dis")
    len_column = len(dis.delr.array)

    mf6.update()
    actual_head = mf6.get_value_ptr("SLN_1/X")

    for cell_id, presciped_head in stress_period_data:
        layer, row, column = cell_id
        head_index = column + row * len_column
        assert math.isclose(presciped_head, actual_head[head_index])


def test_get_value_ptr_modelname(flopy_dis, modflow_lib_path):
    """`flopy_dis` sets constant head values.
       This test checks if these can be properly extracted with origin=modelname."""

    model_path, sim = flopy_dis
    os.chdir(model_path)
    mf6 = XmiWrapper(modflow_lib_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)

    model = sim.get_model(sim.name)
    chd = model.get_package("chd_0")
    stress_period_data = chd.stress_period_data.array[0]

    # TODO: Refactor this as soon as `get_var_grid` is implemented
    dis = model.get_package("dis")
    len_column = len(dis.delr.array)

    mf6.update()
    actual_head = mf6.get_value_ptr(sim.name + "/X")

    for cell_id, presciped_head in stress_period_data:
        layer, row, column = cell_id
        head_index = column + row * len_column
        assert math.isclose(presciped_head, actual_head[head_index])
