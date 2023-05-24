import platform
from dataclasses import dataclass
from typing import Any, List, Tuple

import flopy
import numpy as np
import pytest
from flopy.mf6 import MFSimulation

from xmipy import XmiWrapper


@pytest.fixture(scope="session")
def modflow_lib_path(tmp_path_factory):
    tmp_path = tmp_path_factory.getbasetemp()
    sysinfo = platform.system()
    if sysinfo == "Windows":
        lib_path = tmp_path / "libmf6.dll"
    elif sysinfo == "Linux":
        lib_path = tmp_path / "libmf6.so"
    elif sysinfo == "Darwin":
        lib_path = tmp_path / "libmf6.dylib"
    else:
        raise RuntimeError(f"system not supported: {sysinfo}")

    flopy.utils.get_modflow(bindir=str(tmp_path), repo="modflow6-nightly-build")
    return str(lib_path)


@dataclass
class FlopyDis:
    sim_path: str
    sim: MFSimulation
    tdis_rc: List[Tuple]
    model_name: str
    nrow: int
    ncol: int
    nlay: int
    stress_period_data: List[Any]


@pytest.fixture(scope="function")
def flopy_dis(tmp_path, modflow_lib_path):
    sim_path = str(tmp_path)
    sim = flopy.mf6.MFSimulation(
        sim_name="TEST_SIM_DIS",
        version="mf6",
        sim_ws=sim_path,
    )
    flopy_dis = FlopyDis(
        sim_path=sim_path,
        sim=sim,
        tdis_rc=[(6.0, 2, 1.0), (6.0, 3, 1.0)],
        model_name="TEST_MODEL_DIS",
        nrow=9,
        ncol=10,
        nlay=1,
        stress_period_data=[[(0, 2, 0), 1.0, "BNDA"], [(0, 6, 8), 0.0, "BNDB"]],
    )
    flopy.mf6.ModflowTdis(sim, time_units="DAYS", nper=2, perioddata=flopy_dis.tdis_rc)
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(sim, modelname=flopy_dis.model_name, save_flows=True)
    flopy.mf6.ModflowGwfdis(
        gwf, nrow=flopy_dis.nrow, ncol=flopy_dis.ncol, delr=10.0, delc=10.0
    )
    flopy.mf6.ModflowGwfic(gwf)
    flopy.mf6.ModflowGwfnpf(gwf, save_specific_discharge=True)
    flopy.mf6.ModflowGwfchd(
        gwf,
        stress_period_data=flopy_dis.stress_period_data,
        boundnames=True,
        maxbound=len(flopy_dis.stress_period_data),
    )
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


@pytest.fixture
def flopy_dis_mf6(flopy_dis, modflow_lib_path, request):
    mf6 = XmiWrapper(lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path)

    # If initialized, call finalize() at end of use
    request.addfinalizer(mf6.__del__)

    # Write output to screen
    mf6.set_int("ISTDOUTTOFILE", 0)

    return flopy_dis, mf6


@pytest.fixture(scope="function")
def flopy_dis_idomain(tmp_path, modflow_lib_path):
    sim_path = str(tmp_path)
    sim = flopy.mf6.MFSimulation(
        sim_name="TEST_SIM_DIS", version="mf6", sim_ws=sim_path
    )
    flopy_dis = FlopyDis(
        sim_path=sim_path,
        sim=sim,
        tdis_rc=[(6.0, 2, 1.0), (6.0, 3, 1.0)],
        model_name="TEST_MODEL_DIS",
        nrow=9,
        ncol=10,
        nlay=1,
        stress_period_data=[[(0, 2, 0), 1.0], [(0, 6, 8), 0.0]],
    )
    idomain_vals = np.ones(flopy_dis.nrow * flopy_dis.ncol)
    idomain_vals[0] = -1
    flopy.mf6.ModflowTdis(sim, time_units="DAYS", nper=2, perioddata=flopy_dis.tdis_rc)
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(sim, modelname=flopy_dis.model_name, save_flows=True)
    flopy.mf6.ModflowGwfdis(
        gwf,
        nrow=flopy_dis.nrow,
        ncol=flopy_dis.ncol,
        delr=10.0,
        delc=10.0,
        idomain=idomain_vals,
    )
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


@dataclass
class FlopyDisu:
    sim_path: str
    sim: MFSimulation
    tdis_rc: List[Tuple]
    model_name: str
    nlay: int
    nrow: int
    ncol: int


@pytest.fixture(scope="function")
def flopy_disu(tmp_path):
    sim_path = str(tmp_path)
    sim = flopy.mf6.MFSimulation(sim_name="TEST_SIM_DISU", sim_ws=sim_path)
    flopy_disu = FlopyDisu(
        sim_path=sim_path,
        sim=sim,
        tdis_rc=[(6.0, 2, 1.0), (6.0, 3, 1.0)],
        model_name="TEST_MODEL_DISU",
        nlay=1,
        nrow=3,
        ncol=3,
    )
    flopy.mf6.ModflowTdis(sim, time_units="DAYS", nper=2, perioddata=flopy_disu.tdis_rc)
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(sim, modelname=flopy_disu.model_name, save_flows=True)
    flopy.mf6.ModflowGwfdisu(
        gwf,
        nodes=9,
        nja=33,
        nvert=16,
        top=[0.0],
        bot=[-2.0],
        area=np.full(9, 1.0),
        iac=[3, 4, 3, 4, 5, 4, 3, 4, 3],
        ja=[
            0,
            1,
            3,
            1,
            0,
            2,
            4,
            2,
            1,
            5,
            3,
            0,
            4,
            6,
            4,
            1,
            3,
            5,
            7,
            5,
            2,
            4,
            8,
            6,
            3,
            7,
            7,
            4,
            6,
            8,
            8,
            5,
            7,
        ],
        ihc=[1],
        cl12=[
            0,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
            0.5,
            0,
            0.5,
            0.5,
        ],
        hwva=[
            0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
            1.0,
            0,
            1.0,
            1.0,
        ],
        vertices=[
            [0, 0.0, 0.0],
            [1, 0.0, 1.0],
            [2, 0.0, 2.0],
            [3, 0.0, 3.0],
            [4, 1.0, 0.0],
            [5, 1.0, 1.0],
            [6, 1.0, 2.0],
            [7, 1.0, 3.0],
            [8, 2.0, 0.0],
            [9, 2.0, 1.0],
            [10, 2.0, 2.0],
            [11, 2.0, 3.0],
            [12, 3.0, 0.0],
            [13, 3.0, 1.0],
            [14, 3.0, 2.0],
            [15, 3.0, 3.0],
        ],
        cell2d=[
            [0, 0.5, 0.5, 4, 1, 2, 6, 5],
            [1, 0.5, 1.5, 4, 2, 3, 7, 6],
            [2, 0.5, 2.5, 4, 3, 4, 8, 7],
            [3, 1.5, 0.5, 4, 5, 6, 10, 9],
            [4, 1.5, 1.5, 4, 6, 7, 11, 10],
            [5, 1.5, 2.5, 4, 7, 8, 12, 11],
            [6, 2.5, 0.5, 4, 9, 10, 14, 13],
            [7, 2.5, 1.5, 4, 10, 11, 15, 14],
            [8, 2.5, 2.5, 4, 11, 12, 16, 15],
        ],
    )
    flopy.mf6.ModflowGwfic(gwf)
    flopy.mf6.ModflowGwfnpf(gwf, save_specific_discharge=True)
    sim.write_simulation()
    return flopy_disu


@dataclass
class FlopyGwfSto:
    sim_path: str
    sim: MFSimulation
    model_name: str


@pytest.fixture(scope="function")
def flopy_gwf_sto(tmp_path, modflow_lib_path):
    sim_path = str(tmp_path)
    sim = flopy.mf6.MFSimulation(
        sim_name="TEST_SIM_DIS", version="mf6", sim_ws=sim_path
    )
    flopy_gwf_sto = FlopyGwfSto(sim_path=sim_path, sim=sim, model_name="TEST_MODEL_STO")
    flopy.mf6.ModflowTdis(
        sim, time_units="DAYS", nper=2, perioddata=[(6.0, 2, 1.0), (6.0, 3, 1.0)]
    )
    flopy.mf6.ModflowIms(sim)
    gwf = flopy.mf6.ModflowGwf(sim, modelname=flopy_gwf_sto.model_name, save_flows=True)
    flopy.mf6.ModflowGwfdis(gwf, nrow=1, ncol=10, delr=10.0, delc=10.0)
    flopy.mf6.ModflowGwfic(gwf)
    flopy.mf6.ModflowGwfnpf(gwf, save_specific_discharge=True)
    flopy.mf6.ModflowGwfchd(
        gwf, stress_period_data=[[(0, 0, 0), 1.0], [(0, 0, 9), 0.0]]
    )
    flopy.mf6.ModflowGwfsto(gwf, ss=[1.0e-4] * 10, sy=[0.5e-1] * 10)
    budget_file = flopy_gwf_sto.model_name + ".bud"
    head_file = flopy_gwf_sto.model_name + ".hds"
    flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    )
    sim.write_simulation()
    return flopy_gwf_sto
