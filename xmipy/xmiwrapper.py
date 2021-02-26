import logging
import os
import platform
import sys
from ctypes import (
    CDLL,
    byref,
    POINTER,
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

from xmipy.errors import InputError, TimerError, XMIError
from xmipy.timers.timer import Timer
from xmipy.utils import cd
from xmipy.xmi import Xmi

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
        lib_dependency: str = None,
        working_directory: str = ".",
        timing: bool = False,
    ):

        self._add_lib_dependency(lib_dependency)
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

        self.working_directory = working_directory
        self._state = State.UNINITIALIZED
        self.timing = timing
        self.libname = os.path.basename(lib_path)

        if self.timing:
            self.timer = Timer(
                name=self.libname,
                text="Elapsed time for {name}.{fn_name}: {seconds:0.4f} seconds",
            )

    @staticmethod
    def _add_lib_dependency(lib_dependency):
        if lib_dependency:
            if platform.system() == "Windows":
                os.environ["PATH"] = lib_dependency + os.pathsep + os.environ["PATH"]
            else:
                # Assume a Unix-like system
                if "LD_LIBRARY_PATH" in os.environ:
                    os.environ["LD_LIBRARY_PATH"] = (
                        lib_dependency + os.pathsep + os.environ["LD_LIBRARY_PATH"]
                    )
                else:
                    os.environ["LD_LIBRARY_PATH"] = lib_dependency

    def report_timing_totals(self):
        if self.timing:
            total = self.timer.report_totals()
            logger.info(f"Total elapsed time for {self.libname}: {total:0.4f} seconds")
            return total
        else:
            raise TimerError("Timing not activated")

    def get_constant_int(self, name: str) -> int:
        c_var = c_int.in_dll(self.lib, name)
        return c_var.value

    def set_int(self, name: str, value: int) -> None:
        c_var = c_int.in_dll(self.lib, name)
        c_var.value = value

    def initialize(self, config_file: str = "") -> None:
        if self._state == State.UNINITIALIZED:
            with cd(self.working_directory):
                self.execute_function(self.lib.initialize, config_file)
                self._state = State.INITIALIZED
        else:
            raise InputError("The library is already initialized")

    def update(self) -> None:
        with cd(self.working_directory):
            self.execute_function(self.lib.update)

    def update_until(self, time: float) -> None:
        raise NotImplementedError

    def finalize(self) -> None:
        if self._state == State.INITIALIZED:
            with cd(self.working_directory):
                self.execute_function(self.lib.finalize)
                self._state = State.UNINITIALIZED
        else:
            raise InputError("The library is not initialized yet")

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
        len_name = self.get_constant_int("BMI_LENCOMPONENTNAME")
        component_name = create_string_buffer(len_name)
        self.execute_function(self.lib.get_component_name, byref(component_name))
        return component_name.value.decode("ascii")

    def get_input_item_count(self) -> int:
        count = c_int(0)
        self.execute_function(self.lib.get_input_item_count, byref(count))
        return count.value

    def get_output_item_count(self) -> int:
        count = c_int(0)
        self.execute_function(self.lib.get_output_item_count, byref(count))
        return count.value

    def get_input_var_names(self) -> Tuple[str]:
        len_address = self.get_constant_int("BMI_LENVARADDRESS")
        nr_input_vars = self.get_input_item_count()
        len_names = nr_input_vars * len_address
        names = create_string_buffer(len_names)

        # get a (1-dim) char array (char*) containing the input variable
        # names as \x00 terminated sub-strings
        self.execute_function(self.lib.get_input_var_names, byref(names))

        # decode
        input_vars = [
            names[i * len_address : (i + 1) * len_address]
            .split(b"\0", 1)[0]
            .decode("ascii")
            for i in range(nr_input_vars)
        ]
        return tuple(input_vars)

    def get_output_var_names(self) -> Tuple[str]:
        len_address = self.get_constant_int("BMI_LENVARADDRESS")
        nr_output_vars = self.get_output_item_count()
        len_names = nr_output_vars * len_address
        names = create_string_buffer(len_names)

        # get a (1-dim) char array (char*) containing the output variable
        # names as \x00 terminated sub-strings
        self.execute_function(self.lib.get_output_var_names, byref(names))

        # decode
        output_vars = [
            names[i * len_address : (i + 1) * len_address]
            .split(b"\0", 1)[0]
            .decode("ascii")
            for i in range(nr_output_vars)
        ]
        return tuple(output_vars)

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
        len_var_type = self.get_constant_int("BMI_LENVARTYPE")
        var_type = create_string_buffer(len_var_type)
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

    def get_value(self, name: str, dest: np.ndarray = None) -> np.ndarray:
        # make sure that optional array is of correct layout:
        if dest is not None:
            if not dest.flags["C"]:
                raise InputError("Array should have C layout")

        # first deal with scalars
        rank = self.get_var_rank(name)
        if rank == 0:
            src = self.get_value_ptr_scalar(name)
            if dest is None:
                return self.get_value_ptr_scalar(name).copy()
            else:
                dest[0] = src[0]
                return dest

        var_type = self.get_var_type(name)
        var_shape = self.get_var_shape(name)

        if var_type.lower().startswith("double"):
            if dest is None:
                dest = np.empty(shape=var_shape, dtype=np.float64, order="C")
            self.execute_function(
                self.lib.get_value_double,
                c_char_p(name.encode()),
                byref(dest.ctypes.data_as(POINTER(c_double))),
                detail="for variable " + name,
            )
        elif var_type.lower().startswith("int"):
            if dest is None:
                dest = np.empty(shape=var_shape, dtype=np.int32, order="C")
            self.execute_function(
                self.lib.get_value_int,
                c_char_p(name.encode()),
                byref(dest.ctypes.data_as(POINTER(c_int))),
                detail="for variable " + name,
            )
        else:
            raise InputError("Unsupported value type")

        return dest

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
                dtype=np.float64, ndim=ndim, shape=shape_tuple, flags="C"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_double,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
            return values.contents
        elif vartype.lower().startswith("float"):
            arraytype = np.ctypeslib.ndpointer(
                dtype=np.float32, ndim=ndim, shape=shape_tuple, flags="C"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_float,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
            return values.contents
        elif vartype.lower().startswith("int"):
            arraytype = np.ctypeslib.ndpointer(
                dtype=np.int32, ndim=ndim, shape=shape_tuple, flags="C"
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
                dtype=np.double, ndim=1, shape=(1,), flags="C"
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
                dtype=np.float, ndim=1, shape=(1,), flags="C"
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
                dtype=np.int32, ndim=1, shape=(1,), flags="C"
            )
            values = arraytype()
            self.execute_function(
                self.lib.get_value_ptr_int,
                c_char_p(name.encode()),
                byref(values),
                detail="for variable " + name,
            )
        else:
            raise InputError("Unsupported value type")

        return values.contents

    def get_value_at_indices(
        self, name: str, dest: np.ndarray, inds: np.ndarray
    ) -> np.ndarray:
        raise NotImplementedError

    def set_value(self, name: str, values: np.ndarray) -> None:
        if not values.flags["C"]:
            raise InputError("Array should have C layout")
        vartype = self.get_var_type(name)
        if vartype.lower().startswith("double"):
            if values.dtype != np.float64:
                raise InputError("Array should have float64 elements")
            self.execute_function(
                self.lib.set_value_double,
                c_char_p(name.encode()),
                byref(values.ctypes.data_as(POINTER(c_double))),
                detail="for variable " + name,
            )
        elif vartype.lower().startswith("int"):
            if values.dtype != np.int32:
                raise InputError("Array should have int32 elements")
            self.execute_function(
                self.lib.set_value_int,
                c_char_p(name.encode()),
                byref(values.ctypes.data_as(POINTER(c_int))),
                detail="for variable " + name,
            )
        else:
            raise InputError("Unsupported value type")

    def set_value_at_indices(
        self, name: str, inds: np.ndarray, src: np.ndarray
    ) -> None:
        raise NotImplementedError

    def get_grid_rank(self, grid: int) -> int:
        grid_rank = c_int(0)
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_rank,
            byref(c_grid),
            byref(grid_rank),
            detail="for id " + str(grid),
        )
        return grid_rank.value

    def get_grid_size(self, grid: int) -> int:
        grid_size = c_int(0)
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_size,
            byref(c_grid),
            byref(grid_size),
            detail="for id " + str(grid),
        )
        return grid_size.value

    def get_grid_type(self, grid: int) -> str:
        len_grid_type = self.get_constant_int("BMI_LENGRIDTYPE")
        grid_type = create_string_buffer(len_grid_type)
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
            detail="for id " + str(grid),
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
            detail="for id " + str(grid),
        )
        return x

    def get_grid_y(self, grid: int, y: np.ndarray) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_y,
            byref(c_grid),
            c_void_p(y.ctypes.data),
            detail="for id " + str(grid),
        )
        return y

    def get_grid_z(self, grid: int, z: np.ndarray) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_z,
            byref(c_grid),
            c_void_p(z.ctypes.data),
            detail="for id " + str(grid),
        )
        return z

    def get_grid_node_count(self, grid: int) -> int:
        grid_node_count = c_int(0)
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_node_count,
            byref(c_grid),
            byref(grid_node_count),
            detail="for id " + str(grid),
        )
        return grid_node_count.value

    def get_grid_edge_count(self, grid: int) -> int:
        raise NotImplementedError

    def get_grid_face_count(self, grid: int) -> int:
        grid_face_count = c_int(0)
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_face_count,
            byref(c_grid),
            byref(grid_face_count),
            detail="for id " + str(grid),
        )
        return grid_face_count.value

    def get_grid_edge_nodes(self, grid: int, edge_nodes: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_grid_face_edges(self, grid: int, face_edges: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def get_grid_face_nodes(self, grid: int, face_nodes: np.ndarray) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_face_nodes,
            byref(c_grid),
            c_void_p(face_nodes.ctypes.data),
            detail="for id " + str(grid),
        )
        return face_nodes

    def get_grid_nodes_per_face(
        self, grid: int, nodes_per_face: np.ndarray
    ) -> np.ndarray:
        c_grid = c_int(grid)
        self.execute_function(
            self.lib.get_grid_nodes_per_face,
            byref(c_grid),
            c_void_p(nodes_per_face.ctypes.data),
            detail="for id " + str(grid),
        )
        return nodes_per_face

    # ===========================
    # here starts the XMI
    # ===========================
    def prepare_time_step(self, dt) -> None:
        with cd(self.working_directory):
            dt = c_double(dt)
            self.execute_function(self.lib.prepare_time_step, byref(dt))

    def do_time_step(self) -> None:
        with cd(self.working_directory):
            self.execute_function(self.lib.do_time_step)

    def finalize_time_step(self) -> None:
        with cd(self.working_directory):
            self.execute_function(self.lib.finalize_time_step)

    def get_subcomponent_count(self) -> int:
        count = c_int(0)
        self.execute_function(self.lib.get_subcomponent_count, byref(count))
        return count.value

    def prepare_solve(self, component_id=1) -> None:
        cid = c_int(component_id)
        with cd(self.working_directory):
            self.execute_function(self.lib.prepare_solve, byref(cid))

    def solve(self, component_id=1) -> bool:
        cid = c_int(component_id)
        has_converged = c_int(0)
        with cd(self.working_directory):
            self.execute_function(self.lib.solve, byref(cid), byref(has_converged))
        return has_converged.value == 1

    def finalize_solve(self, component_id=1) -> None:
        cid = c_int(component_id)

        with cd(self.working_directory):
            self.execute_function(self.lib.finalize_solve, byref(cid))

    def get_var_address(
        self, var_name: str, component_name: str, subcomponent_name=""
    ) -> str:
        var_name = var_name.upper()
        component_name = component_name.upper()
        subcomponent_name = subcomponent_name.upper()

        len_var_address = self.get_constant_int("BMI_LENVARADDRESS")
        var_address = create_string_buffer(len_var_address)
        self.execute_function(
            self.lib.get_var_address,
            c_char_p(component_name.encode()),
            c_char_p(subcomponent_name.encode()),
            c_char_p(var_name.encode()),
            byref(var_address),
        )

        return var_address.value.decode()

    def execute_function(self, function, *args, detail=""):
        """
        Utility function to execute a BMI function in the kernel and checks its status
        """

        if self.timing:
            self.timer.start(function.__name__)

        try:
            if function(*args) != Status.SUCCESS:
                msg = f"BMI exception in: {function.__name__} ({detail})"

                # try to get detailed error msg, beware:
                # directly call CDLL methods to avoid recursion
                try:
                    len_err_msg = self.get_constant_int("BMI_LENERRMESSAGE")
                    err_msg = create_string_buffer(len_err_msg)
                    self.lib.get_last_bmi_error(byref(err_msg))

                    len_name = self.get_constant_int("BMI_LENCOMPONENTNAME")
                    component_name = create_string_buffer(len_name)
                    self.lib.get_component_name(byref(component_name))

                    print(
                        "--- Kernel message ("
                        + component_name.value.decode()
                        + ") ---\n=> "
                        + err_msg.value.decode()
                    )
                except AttributeError:
                    print("--- Kernel message ---\n" + "=> no details ...")

                raise XMIError(msg)
        finally:
            if self.timing:
                self.timer.stop(function.__name__)
