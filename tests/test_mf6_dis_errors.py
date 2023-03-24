
import pytest

from xmipy import XmiWrapper
from xmipy.errors import XMIError


def test_err_unknown_var(flopy_dis, modflow_lib_path):
    """Unknown or invalid variable address should trigger python Exception,
    print the kernel error, and not crash the library"""
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    try:
        # Run initialize
        mf6.initialize()

        with pytest.raises(XMIError):
            mf6.get_var_rank("jnexistepas")

        with pytest.raises(XMIError):
            var_address = mf6.get_var_address("X", "dissolution")
            mf6.get_value_ptr(var_address)

    finally:
        mf6.finalize()


def test_err_cvg_failure(flopy_dis, modflow_lib_path):
    """Test convergence failure (and a helper for checking I/O)"""

    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    try:
        # Run initialize
        mf6.initialize()

        # prepare, don't solve to completion, should give error
        mf6.prepare_time_step(mf6.get_time_step())
        mf6.prepare_solve()
        mf6.solve()

        with pytest.raises(XMIError):
            mf6.finalize_solve()

        mf6.finalize_time_step()

    finally:
        mf6.finalize()
