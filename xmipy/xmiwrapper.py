import logging
import os
import platform
import sys
from ctypes import (
    CDLL,
    byref,
    c_char_p,
    c_double,
    c_int,
    c_void_p,
    cdll,
    create_string_buffer,
)
from enum import Enum, IntEnum, unique
from typing import Iterable, Tuple

import numpy as np

from xmipy.xmi import Xmi
from xmipy.timers.timer import Timer

logger = logging.getLogger(__name__)


@unique
class Status(IntEnum):
    SUCCESS = 0
    FAILURE = 1


@unique
class State(Enum):
    UNINITIALIZED = 1
    INITIALIZED = 2


class XmiWrapper(Xmi):
    """
    This is the XMI (BMI++) wrapper for marshalling python types into
    the kernels, and v.v.
    """

    def __init__(
        self,
        lib_path: str,
        lib_dependencies: Iterable[str] = None,
        working_directory: str = ".",
        timing: bool = False,
    ):

        self._add_lib_dependencies(lib_dependencies)
        if sys.version_info[0:2] < (3, 8):
            # Python version < 3.8
            self.lib = CDLL(lib_path)
        else:
            # LoadLibraryEx flag: LOAD_WITH_ALTERED_SEARCH_PATH 0x08
            # -> uses the altered search path for resolving ddl dependencies
            # `winmode` has no effect while running on Linux or macOS
            # Note: this could make xmipy less secure (dll-injection)
            # Can we get it to work without this flag?
            self.lib = CDLL(lib_path, winmode=0x08)

        self.LENVARTYPE = self.get_constant_int("BMI_LENVARTYPE")
        self.LENGRIDTYPE = self.get_constant_int("BMI_LENGRIDTYPE")
        self.LENVARADDRESS = self.get_constant_int("BMI_LENVARADDRESS")

        self.working_directory = working_directory
        self._state = State.UNINITIALIZED
        self.timing = timing
        self.libname = os.path.basename(lib_path)

        if self.timing:
            self.timer = Timer(
                name=self.libname,
                text="Elapsed time for {name}.{fn_name}: {seconds:0.4f} seconds",
            )

    def __del__(self):
        if hasattr(self, "_state"):
            if self._state == State.INITIALIZED:
                self.finalize()

    @staticmethod
    def _add_lib_dependencies(lib_dependencies):
        if lib_dependencies:
            if platform.system() == "Windows":
                for dep_path in lib_dependencies:
                    os.environ["PATH"] = dep_path + os.pathsep + os.environ["PATH"]
            else:
                # Assume a Unix-like system
                for dep_path in lib_dependencies:
                    os.environ["LD_LIBRARY_PATH"] = (
                        dep_path + os.pathsep + os.environ["LD_LIBRARY_PATH"]
                    )

    def report_timing_totals(self):
        if self.timing:
            total = self.timer.report_totals()
            logger.info(f"Total elapsed time for {self.libname}: {total:0.4f} seconds")
            return total
        else:
            raise Exception("Timing not activated")

    def get_constant_int(self, name: str) -> int:
        c_var = c_int.in_dll(self.lib, name)
        return c_var.value

    def set_int(self, name: str, value: int) -> None:
        c_var = c_int.in_dll(self.lib, name)
        c_var.value = value

    def initialize(self, config_file: str = "") -> None:
        if self._state == State.UNINITIALIZED:
            previous_directory = os.getcwd()
            os.chdir(self.working_directory)
            self.execute_function(self.lib.initialize, config_file)
            os.chdir(previous_directory)
            self._state = State.INITIALIZED
        else:
            raise Exception("Modflow is already initialized")

    def update(self) -> None:
        previous_directory = os.getcwd()
        os.chdir(self.working_directory)
        self.execute_function(self.lib.update)
        os.chdir(previous_directory)

    def update_until(self, time: float) -> None:
        raise NotImplementedError

    def finalize(self) -> None:
        if self._state == State.INITIALIZED:
            previous_directory = os.getcwd()
            os.chdir(self.working_directory)
            self.execute_function(self.lib.finalize)
            os.chdir(previous_directory)
            self._state = State.UNINITIALIZED
        else:
            raise Exception("Modflow is not initialized yet")

    def get_current_time(self) -> float:
        current_time = c_double(0.0)
        self.execute_function(self.lib.get_current_time, byref(current_time))
        return current_time.value

    def get_start_time(self) -> float:
        start_time = c_double(0.0)
        self.execute_function(self.lib.get_start_time, byref(start_time))
        return start_time.value

    def get_end_time(self) -> float:
        end_time = c_double(0.0)
        self.execute_function(self.lib.get_end_time, byref(end_time))
        return end_time.value

    def get_time_step(self) -> float:
        dt = c_double(0.0)
        self.execute_function(self.lib.get_time_step, byref(dt))
        return dt.value

    def get_component_name(self) -> str:
        raise NotImplementedError

    def get_input_item_count(self) -> int:
        raise NotImplementedError

    def get_output_item_count(self) -> int:
        raise NotImplementedError

    def get_input_var_names(self) -> Tuple[str]:
        raise NotImplementedError

    def get_output_var_names(self) -> Tuple[str]:
        raise NotImplementedError

    def get_var_grid(self, name: str) -> int:
        grid_id = c_int(0)
        self.execute_function(
            self.lib.get_var_grid,
            c_char_p(name.encode()),
            byref(grid_id),
            detail="for variable " + name,
        )
        return grid_id.value

    def get_var_type(self, name: str) -> str:
        var_type = create_string_buffer(self.LENVARTYPE)
        self.execute_function(
            self.lib.get_var_type,
            c_char_p(name.encode()),
            byref(var_type),
            detail="for variable " + name,
        )
        return var_type.value.decode()

    # strictly speaking not BMI...
    def get_var_shape(self, name: str) -> np.ndarray:
        rank = self.get_var_rank(name)
        array = np.zeros(rank, dtype=np.int32)
        self.execute_function(
            self.lib.get_var_shape,
            c_char_p(name.encode()),
            c_void_p(array.ctypes.data),
            detail="for variable " + name,
        )
        return array

    def get_var_rank(self, name: str) -> int:
        rank = c_int(0)
        self.execute_function(
            self.lib.get_var_rank,
            c_char_p(name.encode()),
            byref(rank),
            detail="for variable " + name,
        )
        return rank.value

    def get_var_units(self, name: str) -> str:
        raise NotImplementedError

    def get_var_itemsize(self, name: str) -> int:
        item_size = c_int(0)
        self.execute_function(
            self.lib.get_var_itemsize,
            c_char_p(name.encode()),
            byref(item_size),
            detail="for variable " + name,
        )
        return item_size.value

    def get_var_nbytes(self, name: str) -> int:
        nbytes = c_int(0)
        self.execute_function(
            self.lib.get_var_nbytes,
            c_char_p(name.encode()),
            byref(nbytes),
            detail="for variable " + name,
        )
        return nbytes.value

    def get_var_location(self, name: str) -> str:
        raise NotImplementedError

    def get_time_units(self) -> str:
        raise NotImplementedError

    def get_value(self, name: str, dest: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_value_ptr(self, name: str) -> np.ndarray:

        # first scalars
        rank = self.get_var_rank(name)
        if rank == 0:
            return self.get_value_ptr_scalar(name)

        vartype = self.get_var_type(name)
        shape_array = self.get_var_shape(name)

        # convert shape array to python tuple
        shape_tuple = tuple(np.trim_zeros(shape_array))
        ndim = len(shape_tuple)

        if vartype.lower().startswith("double"):
            arraytype = np.ctypeslib.ndpointer(
                dtype=np.float64, ndim=ndim, shape=shape_tuple, flags="F"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_double,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
            return values.contents
        elif vartype.lower().startswith("int"):
            arraytype = np.ctypeslib.ndpointer(
                dtype=np.int32, ndim=ndim, shape=shape_tuple, flags="F"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_int,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
            return values.contents

    def get_value_ptr_scalar(self, name: str) -> np.ndarray:
        vartype = self.get_var_type(name)
        if vartype.lower().startswith("double"):
            arraytype = np.ctypeslib.ndpointer(
                dtype=np.double, ndim=1, shape=(1,), flags="F"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_double,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
        elif vartype.lower().startswith("float"):
            arraytype = np.ctypeslib.ndpointer(
                dtype=np.float, ndim=1, shape=(1,), flags="F"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_float,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
        elif vartype.lower().startswith("int"):
            arraytype = np.ctypeslib.ndpointer(
                dtype=np.int32, ndim=1, shape=(1,), flags="F"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_int,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
        else:
            raise Exception("Unsupported value type")

        return values.contents

    def get_value_at_indices(
        self, name: str, dest: np.ndarray, inds: np.ndarray
    ) -> np.ndarray:
        raise NotImplementedError

    def set_value(self, name: str, values: np.ndarray) -> None:
        raise NotImplementedError

    def set_value_at_indices(
        self, name: str, inds: np.ndarray, src: np.ndarray
    ) -> None:
        raise NotImplementedError

    def get_grid_rank(self, grid: int) -> int:
        item_size = c_int(0)
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_rank,
            byref(c_grid),
            byref(item_size),
            detail="for id " + str(grid),
        )
        return item_size.value

    def get_grid_size(self, grid: int) -> int:
        raise NotImplementedError

    def get_grid_type(self, grid: int) -> str:
        grid_type = create_string_buffer(self.LENVARTYPE)
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_type,
            byref(c_grid),
            byref(grid_type),
            detail="for id " + str(grid),
        )
        return grid_type.value.decode()

    def get_grid_shape(self, grid: int, shape: np.ndarray) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_shape,
            byref(c_grid),
            c_void_p(shape.ctypes.data),
            detail="for id " + str(id),
        )
        return shape

    def get_grid_spacing(self, grid: int, spacing: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_grid_origin(self, grid: int, origin: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_grid_x(self, grid: int, x: np.ndarray) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_x,
            byref(c_grid),
            c_void_p(x.ctypes.data),
            detail="for id " + str(id),
        )
        return x

    def get_grid_y(self, grid: int, y: np.ndarray) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_y,
            byref(c_grid),
            c_void_p(y.ctypes.data),
            detail="for id " + str(id),
        )
        return y

    def get_grid_z(self, grid: int, z: np.ndarray) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_z,
            byref(c_grid),
            c_void_p(z.ctypes.data),
            detail="for id " + str(id),
        )
        return z

    def get_grid_node_count(self, grid: int) -> int:
        raise NotImplementedError

    def get_grid_edge_count(self, grid: int) -> int:
        raise NotImplementedError

    def get_grid_face_count(self, grid: int) -> int:
        raise NotImplementedError

    def get_grid_edge_nodes(self, grid: int, edge_nodes: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_grid_face_edges(self, grid: int, face_edges: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_grid_face_nodes(self, grid: int, face_nodes: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_grid_nodes_per_face(
        self, grid: int, nodes_per_face: np.ndarray
    ) -> np.ndarray:
        raise NotImplementedError

    # ===========================
    # here starts the XMI
    # ===========================
    def prepare_time_step(self, dt) -> None:
        previous_directory = os.getcwd()
        os.chdir(self.working_directory)
        dt = c_double(dt)
        self.execute_function(self.lib.prepare_time_step, byref(dt))
        os.chdir(previous_directory)

    def do_time_step(self) -> None:
        previous_directory = os.getcwd()
        os.chdir(self.working_directory)
        self.execute_function(self.lib.do_time_step)
        os.chdir(previous_directory)

    def finalize_time_step(self) -> None:
        previous_directory = os.getcwd()
        os.chdir(self.working_directory)
        self.execute_function(self.lib.finalize_time_step)
        os.chdir(previous_directory)

    def get_subcomponent_count(self) -> int:
        count = c_int(0)
        self.execute_function(self.lib.get_subcomponent_count, byref(count))
        return count.value

    def prepare_solve(self, component_id) -> None:
        cid = c_int(component_id)

        previous_directory = os.getcwd()
        os.chdir(self.working_directory)
        self.execute_function(self.lib.prepare_solve, byref(cid))
        os.chdir(previous_directory)

    def solve(self, component_id) -> bool:
        cid = c_int(component_id)
        has_converged = c_int(0)

        previous_directory = os.getcwd()
        os.chdir(self.working_directory)
        self.execute_function(self.lib.solve, byref(cid), byref(has_converged))
        os.chdir(previous_directory)

        return has_converged.value == 1

    def finalize_solve(self, component_id) -> None:
        cid = c_int(component_id)

        previous_directory = os.getcwd()
        os.chdir(self.working_directory)
        self.execute_function(self.lib.finalize_solve, byref(cid))
        os.chdir(previous_directory)

    def get_var_address(self, var_name: str, component_name: str,
                        subcomponent_name="") -> str:
        var_address = create_string_buffer(self.LENVARADDRESS)
        self.execute_function(self.lib.get_var_address,
                              c_char_p(component_name.encode()),
                              c_char_p(subcomponent_name.encode()),
                              c_char_p(var_name.encode()),
                              byref(var_address))

        return var_address.value.decode()

    def execute_function(self, function, *args, detail=""):
        """
        Utility function to execute a BMI function in the kernel and checks its status
        """

        if self.timing:
            self.timer.start(function.__name__)

        try:
            if function(*args) != Status.SUCCESS:
                msg = f"MODFLOW 6 BMI, exception in: {function.__name__} ({detail})"
                raise Exception(msg)
        finally:
            if self.timing:
                self.timer.stop(function.__name__)

