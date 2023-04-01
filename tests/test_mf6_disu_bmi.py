import numpy as np
import pytest

from xmipy import XmiWrapper


@pytest.fixture
def flopy_disu_mf6(flopy_disu, modflow_lib_path, request):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_disu.sim_path)

    # If initialized, call finalize() at end of use
    request.addfinalizer(mf6.__del__)

    # Write output to screen
    mf6.set_int("ISTDOUTTOFILE", 0)

    return flopy_disu, mf6


def test_get_grid_face_count(flopy_disu_mf6):
    """Tests if the grid_face_count can be extracted"""
    mf6 = flopy_disu_mf6[1]
    mf6.initialize()

    nrow = 3
    ncol = 3
    assert nrow * ncol == mf6.get_grid_face_count(1)


def test_get_grid_node_count(flopy_disu_mf6):
    """Tests if the grid_node_count can be extracted"""
    mf6 = flopy_disu_mf6[1]
    mf6.initialize()

    nrow = 3
    ncol = 3
    assert (nrow + 1) * (ncol + 1) == mf6.get_grid_node_count(1)


def test_get_grid_nodes_per_face(flopy_disu_mf6):
    """Tests if the grid_nodes_per_face can be extracted"""
    mf6 = flopy_disu_mf6[1]
    mf6.initialize()

    grid_id = 1
    face_count = 9

    model_nodes_per_face = np.empty(shape=(face_count,), dtype=np.int32)
    result = mf6.get_grid_nodes_per_face(grid_id, model_nodes_per_face)
    np.testing.assert_array_equal(
        np.full((face_count,), 4),
        model_nodes_per_face,
    )
    # these are the same objects
    assert model_nodes_per_face is result


@pytest.mark.xfail(strict=True)
def test_get_grid_face_nodes(flopy_disu_mf6):
    """Tests if the grid_face_nodes can be extracted."""
    # todo: fix this test
    mf6 = flopy_disu_mf6[1]
    mf6.initialize()

    # First 5 prescribed elements
    expected_grid_face_nodes = np.array([1, 2, 6, 5, 1])

    grid_id = 1
    face_count = 9
    face_nodes_count = face_count * (4 + 1)

    model_grid_face_nodes = np.empty(shape=(face_nodes_count,), dtype=np.int32)
    result = mf6.get_grid_face_nodes(grid_id, model_grid_face_nodes)
    np.testing.assert_array_equal(
        expected_grid_face_nodes,
        model_grid_face_nodes,
    )
    # these are the same objects
    assert model_grid_face_nodes is result
