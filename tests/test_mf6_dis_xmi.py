from xmipy import XmiWrapper


def test_get_get_var_address(flopy_dis, modflow_lib_path):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # Write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # Initialize
    mf6.initialize()

    head_tag = mf6.get_var_address("X", "SLN_1")
    assert head_tag == "SLN_1/X"
