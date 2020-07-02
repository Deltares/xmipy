import pytest
import platform
from pathlib import Path
import flopy


@pytest.fixture(scope="session")
def modflow_lib_path():
    sysinfo = platform.system()
    if sysinfo.lower() == "windows":
        lib_name = "libmf6.dll"
    else:
        lib_name = "libmf6.so"
    return str(Path(__file__).parent / "bin" / lib_name)


@pytest.fixture(scope="function")
def flopy_dis(tmp_path_factory):
    name = "test_model_dis"
    tmp_dir = tmp_path_factory.mktemp(name)
    sim = flopy.mf6.MFSimulation(sim_name=name, sim_ws=str(tmp_dir))
    flopy.mf6.ModflowTdis(sim)
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(sim, modelname=name, save_flows=True)
    flopy.mf6.ModflowGwfdis(gwf, nrow=10, ncol=10)
    flopy.mf6.ModflowGwfic(gwf)
    flopy.mf6.ModflowGwfnpf(gwf, save_specific_discharge=True)
    flopy.mf6.ModflowGwfchd(
        gwf, stress_period_data=[[(0, 0, 0), 1.0], [(0, 9, 9), 0.0]]
    )
    budget_file = name + ".bud"
    head_file = name + ".hds"
    flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    )
    sim.write_simulation()
    model_dir = str(tmp_dir)
    return (model_dir, sim)
