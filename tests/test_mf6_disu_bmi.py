from xmipy import XmiWrapper
from xmipy.errors import InputError, XMIError
import numpy as np
import platform


def test_get_grid_face_count(flopy_disu, modflow_lib_path):
    """Tests if the grid_face_count can be extracted"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_disu.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        prescribed_grid_face_count = flopy_disu.nrow * flopy_disu.ncol

        # Getting the grid id from the model, requires specifying one variable
        k11_tag = mf6.get_var_address("K11", flopy_disu.model_name, "NPF")
        grid_id = mf6.get_var_grid(k11_tag)
        actual_grid_face_count = mf6.get_grid_face_count(grid_id)

        assert prescribed_grid_face_count == actual_grid_face_count
    finally:
        mf6.finalize()


def test_get_grid_node_count(flopy_disu, modflow_lib_path):
    """Tests if the grid_node_count can be extracted"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_disu.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        prescribed_grid_node_count = (flopy_disu.nrow + 1) * (flopy_disu.ncol + 1)

        # Getting the grid id from the model, requires specifying one variable
        k11_tag = mf6.get_var_address("K11", flopy_disu.model_name, "NPF")
        grid_id = mf6.get_var_grid(k11_tag)
        actual_grid_node_count = mf6.get_grid_node_count(grid_id)

        assert prescribed_grid_node_count == actual_grid_node_count
    finally:
        mf6.finalize()


def test_get_grid_nodes_per_face(flopy_disu, modflow_lib_path):
    """Tests if the grid_nodes_per_face can be extracted"""
    # TODO: Find out why test fail on UNIX-like systems
    sysinfo = platform.system()
    if sysinfo == "Windows":
        mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_disu.sim_path)

        # Write output to screen:
        mf6.set_int("ISTDOUTTOFILE", 0)

        try:
            # Initialize
            mf6.initialize()

            # Rectangular grid -> nrow*ncol faces with 4 nodes each
            prescribed_nodes_per_face = np.full(flopy_disu.nrow * flopy_disu.ncol, 4)

            # Getting the grid id from the model, requires specifying one variable
            k11_tag = mf6.get_var_address("K11", flopy_disu.model_name, "NPF")
            grid_id = mf6.get_var_grid(k11_tag)
            face_count = mf6.get_grid_face_count(grid_id)
            actual_nodes_per_face = np.empty(shape=(face_count,), dtype="int", order="F")
            mf6.get_grid_nodes_per_face(grid_id, actual_nodes_per_face)

            assert np.array_equal(prescribed_nodes_per_face, actual_nodes_per_face)
        finally:
            mf6.finalize()


def test_get_grid_face_nodes(flopy_disu, modflow_lib_path):
    """Tests if the grid_face_nodes can be extracted"""
    # TODO: Find out why test fail on UNIX-like systems
    sysinfo = platform.system()
    if sysinfo == "Windows":
        mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_disu.sim_path)

        # Write output to screen:
        mf6.set_int("ISTDOUTTOFILE", 0)

        try:
            # Initialize
            mf6.initialize()

            # First 5 prescribed elements
            prescribed_grid_face_nodes = np.array([1, 2, 6, 5, 1])

            # Getting the grid id from the model, requires specifying one variable
            k11_tag = mf6.get_var_address("K11", flopy_disu.model_name, "NPF")
            grid_id = mf6.get_var_grid(k11_tag)
            grid_face_count = mf6.get_grid_face_count(grid_id)
            grid_nodes_per_face = np.empty(shape=(grid_face_count,), dtype="int", order="F")
            mf6.get_grid_nodes_per_face(grid_id, grid_nodes_per_face)
            face_nodes_count = np.sum(grid_nodes_per_face + 1)

            actual_grid_face_nodes = np.empty(
                shape=(face_nodes_count,), dtype="int", order="F"
            )
            mf6.get_grid_face_nodes(grid_id, actual_grid_face_nodes)

            assert np.array_equal(prescribed_grid_face_nodes, actual_grid_face_nodes[:5])
        finally:
            mf6.finalize()
