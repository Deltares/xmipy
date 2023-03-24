import numpy as np
import pytest

from xmipy import XmiWrapper
from xmipy.errors import InputError


@pytest.fixture
def flopy_dis_mf6(flopy_dis, modflow_lib_path, request):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # If initialized, call finalize() at end of use
    request.addfinalizer(mf6.__del__)

    # Write output to screen
    mf6.set_int("ISTDOUTTOFILE", 0)

    return flopy_dis, mf6


@pytest.fixture
def flopy_dis_idomain_mf6(flopy_dis_idomain, modflow_lib_path, request):
    mf6 = XmiWrapper(
        lib_path=modflow_lib_path, working_directory=flopy_dis_idomain.sim_path
    )

    # If initialized, call finalize() at end of use
    request.addfinalizer(mf6.__del__)

    # Write output to screen
    mf6.set_int("ISTDOUTTOFILE", 0)

    return flopy_dis_idomain, mf6


def test_get_component_name(flopy_dis_mf6):
    assert flopy_dis_mf6[1].get_component_name() == "MODFLOW 6"


def test_initialize_finalize(flopy_dis_mf6):
    from xmipy.xmiwrapper import State

    mf6 = flopy_dis_mf6[1]

    # Check _state before and after initialize() and finalize()
    assert mf6._state == State.UNINITIALIZED
    mf6.initialize()
    assert mf6._state == State.INITIALIZED
    mf6.finalize()
    assert mf6._state == State.UNINITIALIZED


def test_double_initialize(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]

    mf6.initialize()

    # Test if initialize fails, if initialize was called a second time
    with pytest.raises(InputError, match="library is already initialized"):
        mf6.initialize()


def test_finalize_without_initialize(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]

    # Test if finalize fails, if initialize was not called yet
    with pytest.raises(InputError, match="library is not initialized yet"):
        mf6.finalize()


def test_get_start_time(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    # prescribed_start_time for modflow models is always 0.0
    assert mf6.get_start_time() == 0.0


def test_get_end_time(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    assert mf6.get_end_time() == 12.0


def test_update_and_get_current_time(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    assert mf6.get_current_time() == 0.0

    # Advance model by single time step
    mf6.update()
    assert mf6.get_current_time() == 3.0


def test_get_var_type_double(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    head_tag = mf6.get_var_address("X", "SLN_1")
    assert mf6.get_var_type(head_tag) == "DOUBLE (90)"


def test_get_var_type_int(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    iactive_tag = mf6.get_var_address("IACTIVE", "SLN_1")
    assert mf6.get_var_type(iactive_tag) == "INTEGER (90)"


def test_get_var_string(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    name_tag = mf6.get_var_address("NAME", flopy_dis.model_name)
    assert mf6.get_var_rank(name_tag) == 0
    assert mf6.get_var_type(name_tag) == "STRING LEN=16"
    assert mf6.get_value(name_tag).tolist() == ["TEST_MODEL_DIS"]


def test_set_var_string(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    name_tag = mf6.get_var_address("NAME", flopy_dis.model_name)
    assert mf6.get_var_type(name_tag) == "STRING LEN=16"

    # this is not yet supported
    with pytest.raises(InputError, match="Unsupported value type"):
        mf6.set_value(name_tag, np.array(["VladDeSpietser"]))


def test_get_var_stringarray(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    # boundary names are not set until _rp, so we need this update()
    mf6.update()

    bnd_name_tag = mf6.get_var_address("BOUNDNAME_CST", flopy_dis.model_name, "CHD_0")
    var_shape = mf6.get_var_shape(bnd_name_tag)
    assert var_shape == [2]

    var_nbytes = mf6.get_var_nbytes(bnd_name_tag)
    assert var_nbytes == 2 * 40  # NB: LENBOUNDNAME = 40
    ilen = var_nbytes // var_shape[0]
    assert mf6.get_var_type(bnd_name_tag) == f"STRING LEN={ilen} (2)"
    assert mf6.get_value(bnd_name_tag).tolist() == ["BNDA", "BNDB"]

    # test var with rank 1 and shape [0]
    name_tag = mf6.get_var_address("AUXNAME_CST", flopy_dis.model_name, "CHD_0")
    assert mf6.get_var_rank(name_tag) == 1
    assert mf6.get_var_shape(name_tag) == [0]
    assert mf6.get_var_nbytes(name_tag) == 0
    assert mf6.get_var_type(name_tag) == "STRING LEN=16 (0)"
    assert mf6.get_value(name_tag).tolist() == []


def test_get_value_ptr_modelname(flopy_dis_mf6):
    """`flopy_dis` sets constant head values.
    This test checks if these can be properly extracted with origin=modelname."""
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    stress_period_data = flopy_dis.stress_period_data
    shape = flopy_dis.nlay, flopy_dis.nrow, flopy_dis.ncol

    mf6.update()
    head_tag = mf6.get_var_address("X", flopy_dis.model_name)
    actual_head = mf6.get_value_ptr(head_tag)

    for cell_id, presciped_head, _ in stress_period_data:
        head_index = np.ravel_multi_index(cell_id, shape)
        assert presciped_head == actual_head[head_index]


def test_get_value_ptr_scalar(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    mf6.update()
    id_tag = mf6.get_var_address("ID", flopy_dis.model_name)
    grid_id = mf6.get_value_ptr_scalar(id_tag)

    # Only one model is defined => id should be 1
    # grid_id[0], because even scalars are defined as arrays
    assert grid_id[0] == 1


def test_get_var_grid(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    # Getting the grid id from the model, requires specifying one variable
    k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
    prescribed_grid_id = mf6.get_var_grid(k11_tag)

    id_tag = mf6.get_var_address("ID", flopy_dis.model_name)
    assert mf6.get_value_ptr(id_tag) == [prescribed_grid_id]


def test_get_grid_type(flopy_dis_mf6):
    """Tests if the grid type can be extracted"""
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    # Getting the grid id from the model, requires specifying one variable
    k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
    grid_id = mf6.get_var_grid(k11_tag)
    assert mf6.get_grid_type(grid_id) == "rectilinear"


def test_get_input_item_count(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    assert mf6.get_input_item_count() > 0


def test_get_output_item_count(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    assert mf6.get_output_item_count() > 0


def test_get_input_var_names(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    assert "TEST_MODEL_DIS/X" in mf6.get_input_var_names()


def test_get_output_var_names(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    var_names = mf6.get_output_var_names()
    assert "TEST_MODEL_DIS/X" in var_names  # this is readwrite
    assert "SLN_1/IA" in var_names  # and this is readonly


def test_get_var_units(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_var_units` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_var_units("")


def test_get_var_location(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_var_location` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_var_location("")


def test_get_time_units(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_time_units` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_time_units()


def test_get_value_double(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    some_output_var = next(
        var for var in mf6.get_output_var_names() if var.endswith("/X")
    )

    # compare to array in MODFLOW memory:
    np.testing.assert_array_equal(
        mf6.get_value(some_output_var),
        mf6.get_value_ptr(some_output_var),
    )


def test_get_value_double_inplace(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    some_output_var = next(
        var for var in mf6.get_output_var_names() if var.endswith("/X")
    )
    copy_arr = mf6.get_value_ptr(some_output_var).copy()
    copy_arr[:] = -99999.0
    mf6.get_value(some_output_var, copy_arr)

    # compare to array in MODFLOW memory:
    np.testing.assert_array_equal(
        copy_arr,
        mf6.get_value_ptr(some_output_var),
    )


def test_get_value_int(flopy_dis_idomain_mf6):
    mf6 = flopy_dis_idomain_mf6[1]
    mf6.initialize()

    nodes_reduced_tag = next(
        var for var in mf6.get_output_var_names() if var.endswith("/NODEREDUCED")
    )

    # compare to array in MODFLOW memory:
    np.testing.assert_array_equal(
        mf6.get_value(nodes_reduced_tag),
        mf6.get_value_ptr(nodes_reduced_tag),
    )


def test_get_value_int_scalar(flopy_dis_idomain_mf6):
    mf6 = flopy_dis_idomain_mf6[1]
    mf6.initialize()

    # get scalar variable:
    id_tag = next(var for var in mf6.get_output_var_names() if var.endswith("/ID"))
    assert mf6.get_var_rank(id_tag) == 0

    # compare with value in MODFLOW memory:
    np.testing.assert_array_equal(
        mf6.get_value(id_tag),
        mf6.get_value_ptr(id_tag),
    )


def test_get_value_at_indices(flopy_dis_idomain_mf6):
    """Expects to be implemented as soon as `get_value_at_indices` is implemented"""
    mf6 = flopy_dis_idomain_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_value_at_indices("", np.zeros((1, 1)), np.zeros((1, 1)))


def test_set_value(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    # 1D double array
    head_tag = mf6.get_var_address("X", flopy_dis.model_name)
    orig_head = mf6.get_value_ptr(head_tag)
    new_head = 2.0 * orig_head
    mf6.set_value(head_tag, new_head)
    np.testing.assert_array_equal(orig_head, new_head)

    # 1D integer array
    mxit_tag = mf6.get_var_address("MXITER", "SLN_1")
    arr_int = np.zeros(shape=(1,), dtype=np.int32)
    arr_int[0] = 999
    mf6.set_value(mxit_tag, arr_int)
    assert mf6.get_value(mxit_tag).tolist() == [999]


def test_set_value_at_indices(flopy_dis_mf6):
    """Expects to be implemented as soon as `set_value_at_indices` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.set_value_at_indices("", np.zeros((1, 1)), np.zeros((1, 1)))


def test_get_grid_rank(flopy_dis_mf6):
    """Tests if the the grid rank can be extracted"""
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    if flopy_dis.nlay == 1:
        prescribed_grid_rank = 2
    else:
        prescribed_grid_rank = 3

    # Getting the grid id from the model, requires specifying one variable
    k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
    grid_id = mf6.get_var_grid(k11_tag)

    assert prescribed_grid_rank == mf6.get_grid_rank(grid_id)


def test_get_grid_size(flopy_dis_mf6):
    """Tests if the the grid size can be extracted"""
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    prescribed_grid_size = flopy_dis.nrow * flopy_dis.ncol

    # Getting the grid id from the model, requires specifying one variable
    k11_tag = mf6.get_var_address("K11", flopy_dis.model_name, "NPF")
    grid_id = mf6.get_var_grid(k11_tag)

    assert prescribed_grid_size == mf6.get_grid_size(grid_id)


def test_get_grid_spacing(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_grid_spacing` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_grid_spacing(1, np.zeros((1, 1)))


def test_get_grid_origin(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_grid_origin` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_grid_origin(1, np.zeros((1, 1)))


def test_get_grid_edge_count(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_grid_edge_count` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_grid_edge_count(1)


def test_get_grid_edge_nodes(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_grid_edge_nodes` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_grid_edge_nodes(1, np.zeros((1, 1)))


def test_get_grid_face_edges(flopy_dis_mf6):
    """Expects to be implemented as soon as `get_grid_face_edges` is implemented"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(NotImplementedError):
        mf6.get_grid_face_edges(1, np.zeros((1, 1)))
