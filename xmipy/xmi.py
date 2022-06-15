from abc import abstractmethod

from bmipy import Bmi


class Xmi(Bmi):
    """
    This class extends the CSDMS Basic Model Interface

    The extension to the BMI is twofold:

    - the model's outer convergence loop is exposed to facilitate coupling at
      this level

    - a model can have sub-components which share the time stepping but have
      their own convergence loop

    It does not change anything in the BMI interface, so models implementing
    the XMI interface are compatible with BMI

    """

    @abstractmethod
    def prepare_time_step(self, dt: float) -> None:
        """Prepare a single time step.

        Read data from input files and calculate the current time step length
        and the simulation time at the end of the current time step.

        Parameters
        ----------
        dt : float
            MODFLOW time step length for the current time step. Currently
            MODFLOW does not allow this value to be altered after
            initialization, so it is ignored.
        """
        ...

    @abstractmethod
    def do_time_step(self) -> None:
        """Perform a single time step.

        Build and solve a time step to completion. This method encapsulates
        the prepare_solve, solve, and finalize_solve methods.
        """
        ...

    @abstractmethod
    def finalize_time_step(self) -> None:
        """Finalize the time step.

        Write messsages and output after model convergence has
        been achieved.
        """
        ...

    @abstractmethod
    def get_subcomponent_count(self) -> int:
        """Get the number of Numerical Solutions in the simulation.

        For most applications, this number will be equal to 1. Note that this
        part of the XMI only works when the simulation is defined with a single
        Solution Group

        Returns
        -------
        int
          The number of MODFLOW 6 numerical solutions in the simulation.
        """
        ...

    @abstractmethod
    def prepare_solve(self, component_id: int) -> None:
        """Prepare for solving the system of equations.

        This preparation mostly consists of advancing model states.

        Parameters
        ----------
        component_id : int
            MODFLOW 6 numerical solution id number.
        """
        ...

    @abstractmethod
    def solve(self, component_id: int) -> bool:
        """Build and solve the linear system of equations.

        Formulate the system of equations for this outer (Picard) iteration and
        solve. New data used when formulating the system of equations can be
        injected prior to solve().  Before calling this, a matching call to
        prepare_solve() should be performed.

        Parameters
        ----------
        component_id : int
            MODFLOW 6 numerical solution id number.

        Returns
        -------
        bool
          Boolean indicating if convergence has been achieved.

        """
        ...

    @abstractmethod
    def finalize_solve(self, component_id: int) -> None:
        """Finalize the model solve for the current time step.

        Finalize model variables prior to calling finalize_time_step(). This
        method should always be called after calls to prepare_solve() and
        solve()

        Parameters
        ----------
        component_id : int
            MODFLOW 6 numerical solution id number.

        """
        ...
