import math
import os

import numpy as np
import pytest

from xmipy import XmiWrapper
from xmipy.errors import InputError, XMIError


def test_set_int(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)
    mf6.set_int("ISTDOUTTOFILE", 0)


def test_initialize(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Run initialize
        mf6.initialize()
    finally:
        mf6.finalize()


def test_double_initialize(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)
    try:
        # Run initialize
        mf6.initialize()

        # Test if initialize fails, if initialize was called a second time
        with pytest.raises(InputError):
            mf6.initialize()
    finally:
        mf6.finalize()


def test_finalize_without_initialize(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Test if finalize fails, if initialize was not called yet
    with pytest.raises(InputError):
        mf6.finalize()


def test_get_start_time(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # prescribed_start_time for modflow models is always 0
        prescribed_start_time = 0.0

        actual_start_time = mf6.get_start_time()
        assert math.isclose(prescribed_start_time, actual_start_time)
    finally:
        mf6.finalize()


def test_get_end_time(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        prescribed_end_time = 0.0
        for perlen, _, _ in flopy_dis.tdis_rc:
            prescribed_end_time += perlen

        actual_end_time = mf6.get_end_time()
        assert math.isclose(prescribed_end_time, actual_end_time)
    finally:
        mf6.finalize()


def test_update(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # Advance model by single time step
        mf6.update()
    finally:
        mf6.finalize()


def test_get_current_time(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
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
    finally:
        mf6.finalize()


def test_get_var_type_double(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        head_tag = mf6.get_var_address("X", "SLN_1")
        var_type = mf6.get_var_type(head_tag)
        assert var_type == "DOUBLE (90)"
    finally:
        mf6.finalize()


def test_get_var_type_int(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        iactive_tag = mf6.get_var_address("IACTIVE", "SLN_1")
        var_type = mf6.get_var_type(iactive_tag)
        assert var_type == "INTEGER (90)"
    finally:
        mf6.finalize()


def test_get_value_ptr_sln(flopy_dis, modflow_lib_path):
    """`flopy_dis` sets constant head values.
    This test checks if these can be properly extracted with origin="SLN"."""

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        stress_period_data = flopy_dis.stress_period_data
        ncol = flopy_dis.ncol

        mf6.update()
        head_tag = mf6.get_var_address("X", "SLN_1")
        actual_head = mf6.get_value_ptr(head_tag)

        for cell_id, presciped_head in stress_period_data:
            layer, row, column = cell_id
            head_index = column + row * ncol
            assert math.isclose(presciped_head, actual_head[head_index])
    finally:
        mf6.finalize()


def test_get_value_ptr_modelname(flopy_dis, modflow_lib_path):
    """`flopy_dis` sets constant head values.
    This test checks if these can be properly extracted with origin=modelname."""

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        stress_period_data = flopy_dis.stress_period_data
        ncol = flopy_dis.ncol

        mf6.update()
        head_tag = mf6.get_var_address("X", flopy_dis.model_name)
        actual_head = mf6.get_value_ptr(head_tag)

        for cell_id, presciped_head in stress_period_data:
            layer, row, column = cell_id
            head_index = column + row * ncol
            assert math.isclose(presciped_head, actual_head[head_index])
    finally:
        mf6.finalize()


def test_get_value_ptr_scalar(flopy_dis, modflow_lib_path):

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        mf6.update()
        id_tag = mf6.get_var_address("ID", flopy_dis.model_name)
        grid_id = mf6.get_value_ptr_scalar(id_tag)

        # Only one model is defined => id should be 1
        # grid_id[0], because even scalars are defined as arrays
        assert grid_id[0] == 1
    finally:
        mf6.finalize()


def test_get_var_grid(flopy_dis, modflow_lib_path):
    """Tests if the the grid id can be extracted"""

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # Getting the grid id from the model, requires specifying one variable
        k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
        prescriped_grid_id = mf6.get_var_grid(k11_tag)

        id_tag = mf6.get_var_address("ID", flopy_dis.model_name)
        actual_grid_id = mf6.get_value_ptr(id_tag)

        assert prescriped_grid_id == actual_grid_id[0]
    finally:
        mf6.finalize()


def test_get_grid_type(flopy_dis, modflow_lib_path):
    """Tests if the grid type can be extracted"""

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # Getting the grid id from the model, requires specifying one variable
        k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
        grid_id = mf6.get_var_grid(k11_tag)
        grid_type = mf6.get_grid_type(grid_id)

        assert grid_type == "rectilinear"
    finally:
        mf6.finalize()


def test_get_component_name(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_component_name` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_component_name()


def test_get_input_item_count(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_input_item_count` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_input_item_count()


def test_get_output_item_count(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_output_item_count` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_output_item_count()


def test_get_input_var_names(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_input_var_names` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_input_var_names()


def test_get_output_var_names(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_output_var_names` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_output_var_names()


def test_get_var_units(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_var_units` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_var_units("")


def test_get_var_location(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_var_location` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_var_location("")


def test_get_time_units(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_time_units` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_time_units()


def test_get_value(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_value` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_value("", np.zeros((1, 1)))


def test_get_value_at_indices(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_value_at_indices` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_value_at_indices("", np.zeros((1, 1)), np.zeros((1, 1)))


def test_set_value(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    try:
        # Initialize
        mf6.initialize()

        # 1D double array
        head_tag = mf6.get_var_address("X", flopy_dis.model_name)
        orig_head = mf6.get_value_ptr(head_tag)
        new_head = 2.0 * orig_head
        mf6.set_value(head_tag, new_head)
        assert np.array_equal(orig_head, new_head)

        # 1D integer array
        with pytest.raises(NotImplementedError):
            mxit_tag = mf6.get_var_address("MXITER", "SLN_1")
            arr_int = np.zeros(shape=(1,), dtype=np.int32)
            mf6.set_value(mxit_tag, arr_int)

    finally:
        mf6.finalize()


def test_set_value_at_indices(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `set_value_at_indices` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.set_value_at_indices("", np.zeros((1, 1)), np.zeros((1, 1)))


def test_get_grid_rank(flopy_dis, modflow_lib_path):
    """Tests if the the grid rank can be extracted"""

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        mf6.initialize()

        if flopy_dis.nlay == 1:
            prescribed_grid_rank = 2
        else:
            prescribed_grid_rank = 3

        # Getting the grid id from the model, requires specifying one variable
        k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
        grid_id = mf6.get_var_grid(k11_tag)

        actual_grid_rank = mf6.get_grid_rank(grid_id)

        assert prescribed_grid_rank == actual_grid_rank
    finally:
        mf6.finalize()


def test_get_grid_size(flopy_dis, modflow_lib_path):
    """Tests if the the grid size can be extracted"""

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        mf6.initialize()

        prescribed_grid_size = flopy_dis.nrow * flopy_dis.ncol

        # Getting the grid id from the model, requires specifying one variable
        k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
        grid_id = mf6.get_var_grid(k11_tag)

        actual_grid_size = mf6.get_grid_size(grid_id)

        assert prescribed_grid_size == actual_grid_size
    finally:
        mf6.finalize()


def test_get_grid_spacing(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_grid_spacing` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_grid_spacing(1, np.zeros((1, 1)))


def test_get_grid_origin(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_grid_origin` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_grid_origin(1, np.zeros((1, 1)))


def test_get_grid_edge_count(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_grid_edge_count` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_grid_edge_count(1)


def test_get_grid_edge_nodes(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_grid_edge_nodes` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_grid_edge_nodes(1, np.zeros((1, 1)))


def test_get_grid_face_edges(flopy_dis, modflow_lib_path):
    """Expects to be implemented as soon as `get_grid_face_edges` is implemented"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    with pytest.raises(NotImplementedError):
        mf6.get_grid_face_edges(1, np.zeros((1, 1)))
