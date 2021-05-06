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
    def prepare_time_step(self, dt) -> None:
        """ """
        ...

    @abstractmethod
    def do_time_step(self) -> None:
        """ """
        ...

    @abstractmethod
    def finalize_time_step(self) -> None:
        """ """
        ...

    @abstractmethod
    def get_subcomponent_count(self) -> int:
        """ """
        ...

    @abstractmethod
    def prepare_solve(self, component_id) -> None:
        """ """
        ...

    @abstractmethod
    def solve(self, component_id) -> bool:
        """ """
        ...

    @abstractmethod
    def finalize_solve(self, component_id) -> None:
        """ """
        ...
