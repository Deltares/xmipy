import pytest

from xmipy.errors import XMIError


def test_err_unknown_var(flopy_dis_mf6):
    """Unknown or invalid variable address should trigger python Exception,
    print the kernel error, and not crash the library"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(XMIError):
        mf6.get_var_rank("jnexistepas")

    with pytest.raises(XMIError):
        var_address = mf6.get_var_address("X", "dissolution")
        mf6.get_value_ptr(var_address)


def test_err_cvg_failure(flopy_dis_mf6):
    """Test convergence failure (and a helper for checking I/O)"""
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    # prepare, don't solve to completion, should give error
    mf6.prepare_time_step(mf6.get_time_step())
    mf6.prepare_solve()
    mf6.solve()

    with pytest.raises(XMIError):
        mf6.finalize_solve()

    mf6.finalize_time_step()
