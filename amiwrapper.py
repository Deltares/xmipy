import numpy as np
from ctypes import *
from typing import Tuple

from ami import Ami

BMI_SUCCESS = 0
BMI_FAILURE = 1

class AmiWrapper(Ami):
    """This is the AMI (BMI++) wrapper for marshalling python types into the kernels, and v.v."""

    def __init__(self, path):
        self.path = path
        self.dll = cdll.LoadLibrary(path)

    def initialize(self, config_file: str) -> None:
        check_result(self.dll.initialize(config_file), "initialize")

    def update(self) -> None:
        check_result(self.dll.update(), "update")

    def update_until(self, time: float) -> None:
        check_result(BMI_FAILURE, "update_until")

    def finalize(self) -> None:
        check_result(self.dll.finalize(), "finalize")

    def get_current_time(self) -> float:
        current_time = c_double(0.0)
        check_result(self.dll.get_current_time(byref(current_time)), "get_current_time")
        return current_time.value

    def get_start_time(self) -> float:
        start_time = c_double(0.0)
        check_result(self.dll.get_start_time(byref(start_time)), "get_start_time")
        return start_time.value

    def get_end_time(self) -> float:
        end_time = c_double(0.0)
        check_result(self.dll.get_end_time(byref(end_time)), "get_end_time")
        return end_time.value

    def get_component_name(self) -> str:
        pass

    def get_input_item_count(self) -> int:
        pass

    def get_output_item_count(self) -> int:
        pass

    def get_input_var_names(self) -> Tuple[str]:
        pass

    def get_output_var_names(self) -> Tuple[str]:
        pass

    def get_var_grid(self, name: str) -> int:
        pass

    def get_var_type(self, name: str) -> str:
        pass

    def get_var_units(self, name: str) -> str:
        pass

    def get_var_itemsize(self, name: str) -> int:
        pass

    def get_var_nbytes(self, name: str) -> int:
        pass

    def get_var_location(self, name: str) -> str:
        pass

    def get_time_units(self) -> str:
        pass

    def get_time_step(self) -> float:
        pass

    def get_value(self, name: str, dest: np.ndarray) -> np.ndarray:
        pass

    def get_value_ptr(self, name: str) -> np.ndarray:
        pass

    def get_value_at_indices(self, name: str, dest: np.ndarray, inds: np.ndarray) -> np.ndarray:
        pass

    def set_value(self, name: str, values: np.ndarray) -> None:
        pass

    def set_value_at_indices(self, name: str, inds: np.ndarray, src: np.ndarray) -> None:
        pass

    def get_grid_rank(self, grid: int) -> int:
        pass

    def get_grid_size(self, grid: int) -> int:
        pass

    def get_grid_type(self, grid: int) -> str:
        pass

    def get_grid_shape(self, grid: int, shape: np.ndarray) -> np.ndarray:
        pass

    def get_grid_spacing(self, grid: int, spacing: np.ndarray) -> np.ndarray:
        pass

    def get_grid_origin(self, grid: int, origin: np.ndarray) -> np.ndarray:
        pass

    def get_grid_x(self, grid: int, x: np.ndarray) -> np.ndarray:
        pass

    def get_grid_y(self, grid: int, y: np.ndarray) -> np.ndarray:
        pass

    def get_grid_z(self, grid: int, z: np.ndarray) -> np.ndarray:
        pass

    def get_grid_node_count(self, grid: int) -> int:
        pass

    def get_grid_edge_count(self, grid: int) -> int:
        pass

    def get_grid_face_count(self, grid: int) -> int:
        pass

    def get_grid_edge_nodes(self, grid: int, edge_nodes: np.ndarray) -> np.ndarray:
        pass

    def get_grid_face_edges(self, grid: int, face_edges: np.ndarray) -> np.ndarray:
        pass

    def get_grid_face_nodes(self, grid: int, face_nodes: np.ndarray) -> np.ndarray:
        pass

    def get_grid_nodes_per_face(self, grid: int, nodes_per_face: np.ndarray) -> np.ndarray:
        pass

    # ===========================
    # here starts the AMI
    # ===========================
    def prepare_timestep(self) -> None:
        check_result(self.dll.prepare_timestep(), "prepare_timestep")

    def finalize_timestep(self) -> None:
        check_result(self.dll.finalize_timestep(), "finalize_timestep")

    def get_subcomponent_count(self) -> int:
        count = c_int(0)
        check_result(self.dll.get_subcomponent_count(byref(count)), "get_subcomponent_count")
        return count.value

    def prepare_iteration(self, component_id) -> None:
        cid = c_int(component_id)
        check_result(self.dll.prepare_iteration(byref(cid)), "prepare_iteration")

    def do_iteration(self, component_id) -> bool:
        cid = c_int(component_id)
        has_converged = c_int(0)
        check_result(self.dll.do_iteration(byref(cid), byref(has_converged)), "do_iteration")
        return has_converged.value == 1

    def finalize_iteration(self, component_id) -> None:
        cid = c_int(component_id)
        check_result(self.dll.finalize_iteration(byref(cid)), "finalize_iteration")




def check_result(result, function_name):
    """Utility function to check the BMI status in the kernel"""
    if result != BMI_SUCCESS:
        raise Exception("MODFLOW 6 BMI, exception in: " + function_name)