from typing import Tuple

import numpy as np

from ami import Ami
from ctypes import *
from enum import Enum

class BmiStatus(Enum):
    """The BMI status code as returned from the kernel"""
    BMI_SUCCESS = 0
    BMI_FAILURE = 1

class Mf6(Ami):
    """This is the BMI+AMI wrapper for the MODFLOW 6 kernel"""

    def __init__(self, path):
        self.path = path
        self.dll = cdll.LoadLibrary(path)

    def initialize(self, config_file: str) -> None:
        check_result(self.dll.initialize(config_file), "initialize")

    def update(self) -> None:
        check_result(self.dll.update(), "update")

    def update_until(self, time: float) -> None:
        check_result(BmiStatus.BMI_FAILURE, "update_until")

    def finalize(self) -> None:
        check_result(self.dll.finalize, "finalize")

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
    # here start the AMI
    # ===========================
    def prepare_timestep(self) -> None:
        pass

    def finalize_timestep(self) -> None:
        pass

    def get_subcomponent_count(self) -> int:
        pass

    def prepare_iteration(self, component_id) -> None:
        pass

    def do_iteration(self, component_id) -> bool:
        pass

    def finalize_iteration(self, component_id) -> None:
        pass




def check_result(result, function_name):
    """Utility function to check the BMI status in the kernel"""
    if result != BmiStatus.BMI_SUCCESS:
        raise Exception("MODFLOW 6 BMI, exception in: " + function_name)