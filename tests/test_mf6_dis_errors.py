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
