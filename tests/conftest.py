import pytest
import platform
from pathlib import Path
import flopy
import pymake
from dataclasses import dataclass
from typing import List, Tuple, Any
from flopy.mf6 import MFSimulation


@pytest.fixture(scope="session")
def modflow_lib_path(tmp_path_factory):
    tmp_path = tmp_path_factory.getbasetemp()
    url = "https://github.com/MODFLOW-USGS/modflow6-nightly-build/releases/latest/download/"
    sysinfo = platform.system()
    if sysinfo == "Windows":
        url += "win64.zip"
        lib_path = tmp_path / "libmf6.dll"
    elif sysinfo == "Linux":
        url += "linux.zip"
        lib_path = tmp_path / "libmf6.so"
    elif sysinfo == "Darwin":
        url += "mac.zip"
        lib_path = tmp_path / "libmf6.so"

    pymake.download_and_unzip(
        url=url, pth=str(tmp_path),
    )
    return str(lib_path)


@dataclass
class FlopyDis:
    sim_path: str
    sim: MFSimulation
    tdis_rc: List[Tuple]
    model_name: str
    nrow: int
    ncol: int
    stress_period_data: List[Any]


@pytest.fixture(scope="function")
def flopy_dis(tmp_path, modflow_lib_path):
    sim_path = str(tmp_path)
    sim = flopy.mf6.MFSimulation(sim_name="TEST_SIM_DIS", sim_ws=sim_path)
    flopy_dis = FlopyDis(
        sim_path=sim_path,
        sim=sim,
        tdis_rc=[(6.0, 2, 1.0), (6.0, 3, 1.0)],
        model_name="TEST_MODEL_DIS",
        nrow=9,
        ncol=10,
        stress_period_data=[[(0, 2, 0), 1.0], [(0, 6, 8), 0.0]],
    )
    flopy.mf6.ModflowTdis(sim, time_units="DAYS", nper=2, perioddata=flopy_dis.tdis_rc)
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(sim, modelname=flopy_dis.model_name, save_flows=True)
    flopy.mf6.ModflowGwfdis(gwf, nrow=9, ncol=10)
    flopy.mf6.ModflowGwfic(gwf)
    flopy.mf6.ModflowGwfnpf(gwf, save_specific_discharge=True)
    flopy.mf6.ModflowGwfchd(gwf, stress_period_data=flopy_dis.stress_period_data)
    budget_file = flopy_dis.model_name + ".bud"
    head_file = flopy_dis.model_name + ".hds"
    flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    )
    sim.write_simulation()
    return flopy_dis
