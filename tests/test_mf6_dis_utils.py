import pytest

from xmipy import XmiWrapper
from xmipy.errors import TimerError


@pytest.fixture
def flopy_dis_mf6_timing(flopy_dis, modflow_lib_path, request):
    mf6 = XmiWrapper(
        lib_path=modflow_lib_path, working_directory=flopy_dis.sim_path, timing=True
    )

    # If initialized, call finalize() at end of use
    request.addfinalizer(mf6.__del__)

    # Write output to screen
    mf6.set_int("ISTDOUTTOFILE", 0)

    return flopy_dis, mf6


def test_timing_initialize(flopy_dis_mf6_timing):
    mf6 = flopy_dis_mf6_timing[1]
    mf6.initialize()

    assert mf6.report_timing_totals() > 0.0


def test_timing_nothing(flopy_dis_mf6_timing):
    mf6 = flopy_dis_mf6_timing[1]

    total = mf6.report_timing_totals()
    assert pytest.approx(total) == 0.0


def test_deactivated_timing(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    with pytest.raises(TimerError, match="Timing not activated"):
        mf6.report_timing_totals()


def test_dependencies(flopy_dis, modflow_lib_path):
    XmiWrapper(
        lib_path=modflow_lib_path,
        lib_dependency=modflow_lib_path,
        working_directory=flopy_dis.sim_path,
    )
