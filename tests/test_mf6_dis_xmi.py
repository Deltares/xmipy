import pytest
from xmipy import XmiWrapper


def test_get_var_address(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        head_tag = mf6.get_var_address("X", "SLN_1")
        assert head_tag == "SLN_1/X"

        # with lowercase should work too
        k11_tag = mf6.get_var_address("k11", flopy_dis.model_name.lower(), "NPF")
        assert k11_tag == flopy_dis.model_name.upper() + "/NPF/K11"
    finally:
        mf6.finalize()


def test_prepare_time_step(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        dt = mf6.get_time_step()
        mf6.prepare_time_step(dt)
    finally:
        mf6.finalize()


def test_get_subcomponent_count(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        n_solutions = mf6.get_subcomponent_count()

        # Modflow 6 BMI does only support the use of a single solution groups
        assert n_solutions == 1
    finally:
        mf6.finalize()


def test_prepare_solve(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # Prepare solve
        sol_id = 1
        mf6.prepare_solve(sol_id)
    finally:
        mf6.finalize()


def test_solve(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # Prepare solve
        sol_id = 1
        mf6.prepare_solve(sol_id)

        # Get max iteration
        mxit_tag = mf6.get_var_address("MXITER", "SLN_1")
        max_iter_arr = mf6.get_value_ptr(mxit_tag)
        max_iter = max_iter_arr[0]

        kiter = 0
        while kiter < max_iter:
            has_converged = mf6.solve(sol_id)
            kiter += 1

            if has_converged:
                break

        assert has_converged
    finally:
        mf6.finalize()


def test_finalize_solve(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # Prepare solve
        sol_id = 1
        mf6.prepare_solve(sol_id)

        # Get max iteration
        mxit_tag = mf6.get_var_address("MXITER", "SLN_1")
        max_iter_arr = mf6.get_value_ptr(mxit_tag)
        max_iter = max_iter_arr[0]

        kiter = 0
        while kiter < max_iter:
            has_converged = mf6.solve(sol_id)
            kiter += 1

            if has_converged:
                break

        assert has_converged
        mf6.finalize_solve(sol_id)
    finally:
        mf6.finalize()


def test_solve_default_solution_id(flopy_dis, modflow_lib_path):
    """Should no longer be needed to put in the solution id,
    when there is only one (or you want to use the first one
    in the sequence"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        #
        mf6.prepare_solve()

        # Get max iteration
        mxit_tag = mf6.get_var_address("MXITER", "SLN_1")
        max_iter_arr = mf6.get_value_ptr(mxit_tag)
        max_iter = max_iter_arr[0]

        kiter = 0
        while kiter < max_iter:
            has_converged = mf6.solve()
            kiter += 1

            if has_converged:
                break

        assert has_converged

        mf6.finalize_solve()
    finally:
        mf6.finalize()


def test_finalize_time_step(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    try:
        # Initialize
        mf6.initialize()

        # Prepare solve
        sol_id = 1
        mf6.prepare_solve(sol_id)

        # Get max iteration
        mxit_tag = mf6.get_var_address("MXITER", "SLN_1")
        max_iter_arr = mf6.get_value_ptr(mxit_tag)
        max_iter = max_iter_arr[0]

        kiter = 0
        while kiter < max_iter:
            has_converged = mf6.solve(sol_id)
            kiter += 1

            if has_converged:
                break

        assert has_converged
        mf6.finalize_solve(sol_id)
        mf6.finalize_time_step()
    finally:
        mf6.finalize()


def test_get_version(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    with pytest.raises(ValueError) as e:
        mf6.get_version()
