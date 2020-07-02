import os
from amipy import AmiWrapper


def test_initialize_dis(flopy_dis, modflow_lib_path):
    model_path, sim = flopy_dis
    os.chdir(model_path)
    mf6 = AmiWrapper(modflow_lib_path)

    # write output to screen:
    mf6.set_int("ISTDOUTTOFILE", 0)

    # run initialize
    mf6_config_file = os.path.join(model_path, "mfsim.nam")
    mf6.initialize(mf6_config_file)
