import numpy as np


def test_pretty_ctypes_execute_function():
    from ctypes import (
        POINTER,
        byref,
        c_char,
        c_char_p,
        c_double,
        c_float,
        c_void_p,
        create_string_buffer,
        pointer,
    )

    from xmipy.utils import pretty_ctypes_execute_function

    ar = np.zeros(2, dtype=np.int32)
    sar = np.zeros(1, dtype="<S4")
    far = np.zeros(shape=(2, 3), dtype="<f8", order="C")
    arraytype = np.ctypeslib.ndpointer(dtype="<f8", ndim=2, shape=(2, 3), flags="C")

    cases = [
        ("x()", []),
        ("x(b'')", ["".encode()]),
        ("x(b'z', 5)", ["z".encode(), 5]),
        ("x(c_double(1.0))", [c_double(1)]),
        ("x(&c_double(8.0))", [byref(c_double(8))]),
        ("x(*c_double(9.0))", [pointer(c_double(9))]),
        ("x(c_char_Array_5(b''))", [create_string_buffer(5)]),
        ("x(c_char_Array_2(b'z'))", [create_string_buffer("z".encode())]),
        ("x(&c_char_Array_5(b''))", [byref(create_string_buffer(5))]),
        ("x(&c_char_Array_2(b'z'))", [byref(create_string_buffer(b"z"))]),
        ("x(c_char_p(b'z'))", [c_char_p("z".encode())]),
        ("x(&c_char_p(b'z'))", [byref(c_char_p("z".encode()))]),
        (f"x(c_void_p({ar.ctypes.data}))", [c_void_p(ar.ctypes.data)]),
        (r"x(*c_char(b'\x00'))", [sar.ctypes.data_as(POINTER(c_char))]),
        (r"x(&*c_char(b'\x00'))", [byref(sar.ctypes.data_as(POINTER(c_char)))]),
        ("x(*c_float(0.0))", [far.ctypes.data_as(POINTER(c_float))]),
        ("x(&*c_float(0.0))", [byref(far.ctypes.data_as(POINTER(c_float)))]),
        ("x(ndpointer_<f8_2d_2x3_C)", [arraytype()]),
        ("x(&ndpointer_<f8_2d_2x3_C)", [byref(arraytype())]),
    ]
    for expected, args in cases:
        assert expected == pretty_ctypes_execute_function("x", *args)
