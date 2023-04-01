import pytest


def test_get_var_address(flopy_dis_mf6):
    flopy_dis, mf6 = flopy_dis_mf6
    mf6.initialize()

    head_tag = mf6.get_var_address("X", "SLN_1")
    assert head_tag == "SLN_1/X"

    # with lowercase should work too
    k11_tag = mf6.get_var_address("k11", flopy_dis.model_name.lower(), "NPF")
    assert k11_tag == flopy_dis.model_name.upper() + "/NPF/K11"


def test_prepare_time_step(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    dt = mf6.get_time_step()
    assert dt == 0.0
    mf6.prepare_time_step(dt)
    assert mf6.get_time_step() == 3.0


def test_get_subcomponent_count(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    # Modflow 6 BMI does only support the use of a single solution groups
    assert mf6.get_subcomponent_count() == 1


@pytest.mark.parametrize("sol_id", [(1,), ()])
def test_manual_do_time_step(flopy_dis_mf6, sol_id):
    """Test four xmi functions:

        - prepare_solve
        - solve
        - finalize_solve
        - finalize_time_step

    Parameterized using a component_id (sol_id) or default for XmiWrapper.
    """
    mf6 = flopy_dis_mf6[1]
    mf6.initialize()

    # Prepare solve
    mf6.prepare_solve(*sol_id)

    # mf6.get_var_address("MXITER", "SLN_1")
    max_iter = 25
    for kiter in range(max_iter):
        has_converged = mf6.solve(*sol_id)

        if has_converged:
            break

    assert has_converged

    mf6.finalize_solve(*sol_id)
    mf6.finalize_time_step()


def test_get_version(flopy_dis_mf6):
    mf6 = flopy_dis_mf6[1]

    assert len(mf6.get_version()) > 0
