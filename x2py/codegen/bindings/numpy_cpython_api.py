"""
Handling the transitions between Python code and C code using (Numpy/C Api).
"""

import numpy as np

from .c_concepts import CNativeInt
from ..models.core import FunctionDef, FunctionDefArgument, FunctionDefResult
from .cpython_api import (
    PythonObjectType,
    c_to_py_registry,
    check_type_registry,
    pytype_parse_registry,
)
from ..models.datatypes import CharType, FixedSizeType, GenericType, NumpyBoolType, VoidType
from ..models.datatypes import (
    NumpyComplex64Type,
    NumpyComplex128Type,
    NumpyComplex256Type,
    NumpyFloat32Type,
    NumpyFloat64Type,
    NumpyFloat128Type,
    NumpyInt8Type,
    NumpyInt16Type,
    NumpyInt32Type,
    NumpyInt64Type,
    NumpyNDArrayType,
)
from ..models.core import Variable

__all__ = (
    # --------- DATATYPES ---------
    "NumpyArrayObjectType",
    # -------HELPERS ------
    "PyArray_SetBaseObject",
    # -------OTHERS--------
    "get_numpy_max_acceptable_version_file",
    # ------- CAST FUNCTIONS ------
    "pyarray_to_ndarray",
)


class NumpyArrayObjectType(FixedSizeType):
    """
    Datatype representing a `PyArrayObject`.

    Datatype representing a `PyArrayObject` which is the
    class used to hold NumPy array objects in Python.
    """

    __slots__ = ()
    _name = "PyArrayObject"


# -------------------------------------------------------------------
#                      Numpy functions
# -------------------------------------------------------------------


def get_numpy_max_acceptable_version_file():
    """
    Get the macro specifying the most recent acceptable NumPy version.

    Get the macro specifying the most recent acceptable NumPy version.
    If NumPy is more recent than this then deprecation warnings are shown.

    The most recent acceptable NumPy version is 1.19. If the current version is older
    than this then the last acceptable NumPy version is the current version.

    Returns
    -------
    str
        A string containing the code which defines the macro.
    """
    numpy_max_acceptable_version = [1, 19]
    numpy_current_version = [int(v) for v in np.version.version.split(".")[:2]]
    numpy_api_acceptable_version = min(numpy_max_acceptable_version, numpy_current_version)
    major, minor = numpy_api_acceptable_version
    numpy_api_macro = f"# define NPY_NO_DEPRECATED_API NPY_{major}_{minor}_API_VERSION\n"
    version_file = "#ifndef NPY_NO_DEPRECATED_API\n" + numpy_api_macro + "#endif\n"
    if numpy_current_version[0] >= 2:
        version_file += "#ifndef NPY_TARGET_VERSION\n# define NPY_TARGET_VERSION NPY_2_0_API_VERSION\n#endif\n"
    return version_file


PyArray_Check = FunctionDef(
    name="PyArray_Check",
    body=[],
    arguments=[FunctionDefArgument(Variable(PythonObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(Variable(NumpyBoolType(), name="b")),
)

PyArray_DATA = FunctionDef(
    name="PyArray_DATA",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(Variable(VoidType(), name="b", memory_handling="alias")),
)

PyArray_NDIM = FunctionDef(
    name="PyArray_NDIM",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(Variable(CNativeInt(), name="nd")),
)

PyArray_TYPE = FunctionDef(
    name="PyArray_TYPE",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(Variable(CNativeInt(), name="typenum")),
)

PyArray_BASE = FunctionDef(
    name="PyArray_BASE",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias")),
)

PyArray_SHAPE = FunctionDef(
    name="PyArray_SHAPE",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(
        Variable(NumpyNDArrayType.get_new(NumpyInt32Type(), 1, None, raw=True), name="s", memory_handling="alias")
    ),
)

PyArray_STRIDES = FunctionDef(
    name="PyArray_STRIDES",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(
        Variable(NumpyNDArrayType.get_new(NumpyInt32Type(), 1, None, raw=True), name="s", memory_handling="alias")
    ),
)

PyArray_ITEMSIZE = FunctionDef(
    name="PyArray_ITEMSIZE",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    results=FunctionDefResult(Variable(NumpyInt32Type(), name="s")),
)

# NumPy array to c ndarray : function definition in x2py/stdlib/x2py_runtime/python_runtime.c
pyarray_to_ndarray = FunctionDef(
    name="pyarray_to_ndarray",
    body=[],
    arguments=[FunctionDefArgument(Variable(PythonObjectType(), "a", memory_handling="alias"))],
    results=FunctionDefResult(Variable(NumpyNDArrayType.get_new(GenericType(), 1, None), "array")),
)

numpy_to_stc_strides = FunctionDef(
    name="numpy_to_stc_strides",
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="o", memory_handling="alias"))],
    body=[],
    results=FunctionDefResult(Variable(NumpyNDArrayType.get_new(NumpyInt32Type(), 1, None, raw=True), "strides")),
)

# NumPy array check elements : function definition in x2py/stdlib/x2py_runtime/python_runtime.c
pyarray_check = FunctionDef(
    name="pyarray_check",
    arguments=[
        FunctionDefArgument(Variable(CharType(), "name", memory_handling="alias")),
        FunctionDefArgument(Variable(PythonObjectType(), "a", memory_handling="alias")),
        FunctionDefArgument(Variable(CNativeInt(), "dtype")),
        FunctionDefArgument(Variable(CNativeInt(), "rank")),
        FunctionDefArgument(Variable(CNativeInt(), "flag")),
        FunctionDefArgument(Variable(NumpyBoolType(), "allow_empty")),
    ],
    body=[],
    results=FunctionDefResult(Variable(NumpyBoolType(), "b")),
)

is_numpy_array = FunctionDef(
    name="is_numpy_array",
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), "a", memory_handling="alias")),
        FunctionDefArgument(Variable(CNativeInt(), "dtype")),
        FunctionDefArgument(Variable(CNativeInt(), "rank")),
        FunctionDefArgument(Variable(CNativeInt(), "flag")),
        FunctionDefArgument(Variable(NumpyBoolType(), "allow_empty")),
    ],
    body=[],
    results=FunctionDefResult(Variable(NumpyBoolType(), "b")),
)

get_strides_and_shape_from_numpy_array = FunctionDef(
    name="get_strides_and_shape_from_numpy_array",
    arguments=[
        FunctionDefArgument(Variable(PythonObjectType(), "arr", memory_handling="alias")),
        FunctionDefArgument(
            Variable(
                NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True),
                "base_shape",
                memory_handling="alias",
            )
        ),
        FunctionDefArgument(
            Variable(
                NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True),
                "ubounds",
                memory_handling="alias",
            )
        ),
        FunctionDefArgument(
            Variable(
                NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True),
                "strides",
                memory_handling="alias",
            )
        ),
        FunctionDefArgument(Variable(NumpyBoolType(), "c_order")),
    ],
    body=[],
)

PyArray_DATA = FunctionDef(
    name="PyArray_DATA",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), "arr", memory_handling="alias"))],
    results=FunctionDefResult(Variable(VoidType(), "data", memory_handling="alias")),
)

PyArray_SetBaseObject = FunctionDef(
    name="PyArray_SetBaseObject",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(NumpyArrayObjectType(), name="arr", memory_handling="alias")),
        FunctionDefArgument(Variable(PythonObjectType(), name="obj", memory_handling="alias")),
    ],
    results=FunctionDefResult(Variable(CNativeInt(), name="d")),
)

PyArray_CHKFLAGS = FunctionDef(
    name="PyArray_CHKFLAGS",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(NumpyArrayObjectType(), name="arr", memory_handling="alias")),
        FunctionDefArgument(Variable(CNativeInt(), name="flags")),
    ],
    results=FunctionDefResult(Variable(NumpyBoolType(), name="b")),
)

PyArray_CLEARFLAGS = FunctionDef(
    name="PyArray_CLEARFLAGS",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(NumpyArrayObjectType(), name="arr", memory_handling="alias")),
        FunctionDefArgument(Variable(CNativeInt(), name="flags")),
    ],
)

PyArray_ISNOTSWAPPED = FunctionDef(
    name="PyArray_ISNOTSWAPPED",
    body=[],
    arguments=[FunctionDefArgument(Variable(NumpyArrayObjectType(), name="arr", memory_handling="alias"))],
    results=FunctionDefResult(Variable(NumpyBoolType(), name="b")),
)

to_pyarray = FunctionDef(
    name="to_pyarray",
    body=[],
    arguments=[
        FunctionDefArgument(Variable(CNativeInt(), name="nd")),
        FunctionDefArgument(Variable(CNativeInt(), name="typenum")),
        FunctionDefArgument(Variable(VoidType(), name="data", memory_handling="alias")),
        FunctionDefArgument(Variable(NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None, raw=True), "shape")),
        FunctionDefArgument(Variable(NumpyBoolType(), "c_order")),
        FunctionDefArgument(Variable(NumpyBoolType(), "release_memory")),
    ],
    results=FunctionDefResult(Variable(PythonObjectType(), name="arr", memory_handling="alias")),
)


import_array = FunctionDef("import_array", (), ())

# Basic Array Flags
# https://numpy.org/doc/stable/reference/c-api/array.html#c.NPY_ARRAY_OWNDATA
numpy_flag_own_data = Variable(CNativeInt(), name="NPY_ARRAY_OWNDATA")
# https://numpy.org/doc/stable/reference/c-api/array.html#c.NPY_ARRAY_WRITEABLE
numpy_flag_writeable = Variable(CNativeInt(), name="NPY_ARRAY_WRITEABLE")
# https://numpy.org/doc/stable/reference/c-api/array.html#c.NPY_ARRAY_ALIGNED
numpy_flag_aligned = Variable(CNativeInt(), name="NPY_ARRAY_ALIGNED")
# https://numpy.org/doc/stable/reference/c-api/array.html#c.NPY_ARRAY_C_CONTIGUOUS
numpy_flag_c_contig = Variable(CNativeInt(), name="NPY_ARRAY_C_CONTIGUOUS")
# https://numpy.org/doc/stable/reference/c-api/array.html#c.NPY_ARRAY_F_CONTIGUOUS
numpy_flag_f_contig = Variable(CNativeInt(), name="NPY_ARRAY_F_CONTIGUOUS")

# Custom Array Flags defined in x2py/stdlib/x2py_runtime/python_runtime.h
no_type_check = Variable(CNativeInt(), name="NO_TYPE_CHECK")
no_order_check = Variable(CNativeInt(), name="NO_ORDER_CHECK")
require_c_contiguous = Variable(CNativeInt(), name="REQUIRE_C_CONTIGUOUS")
require_f_contiguous = Variable(CNativeInt(), name="REQUIRE_F_CONTIGUOUS")
require_any_contiguous = Variable(CNativeInt(), name="REQUIRE_ANY_CONTIGUOUS")

# https://numpy.org/doc/stable/reference/c-api/dtype.html
numpy_bool_type = Variable(CNativeInt(), name="NPY_BOOL")
numpy_byte_type = Variable(CNativeInt(), name="NPY_BYTE")
numpy_ubyte_type = Variable(CNativeInt(), name="NPY_UBYTE")
numpy_short_type = Variable(CNativeInt(), name="NPY_SHORT")
numpy_ushort_type = Variable(CNativeInt(), name="NPY_USHORT")
numpy_int32_type = Variable(CNativeInt(), name="NPY_INT32")
numpy_uint_type = Variable(CNativeInt(), name="NPY_UINT")
numpy_long_type = Variable(CNativeInt(), name="NPY_LONG")
numpy_ulong_type = Variable(CNativeInt(), name="NPY_ULONG")
numpy_int64_type = Variable(CNativeInt(), name="NPY_INT64")
numpy_ulonglong_type = Variable(CNativeInt(), name="NPY_ULONGLONG")
numpy_float_type = Variable(CNativeInt(), name="NPY_FLOAT")
numpy_double_type = Variable(CNativeInt(), name="NPY_DOUBLE")
numpy_longdouble_type = Variable(CNativeInt(), name="NPY_LONGDOUBLE")
numpy_cfloat_type = Variable(CNativeInt(), name="NPY_CFLOAT")
numpy_cdouble_type = Variable(CNativeInt(), name="NPY_CDOUBLE")
numpy_clongdouble_type = Variable(CNativeInt(), name="NPY_CLONGDOUBLE")

numpy_dtype_registry = {
    CharType(): numpy_byte_type,
    NumpyBoolType(): numpy_bool_type,
    NumpyInt8Type(): numpy_byte_type,
    NumpyInt16Type(): numpy_short_type,
    NumpyInt32Type(): numpy_int32_type,
    NumpyInt64Type(): numpy_int64_type,
    NumpyFloat32Type(): numpy_float_type,
    NumpyFloat64Type(): numpy_double_type,
    NumpyFloat128Type(): numpy_longdouble_type,
    NumpyComplex64Type(): numpy_cfloat_type,
    NumpyComplex128Type(): numpy_cdouble_type,
    NumpyComplex256Type(): numpy_clongdouble_type,
}

# Needed to check for NumPy arguments type
check_type_registry.update(
    {
        NumpyInt8Type(): "PyIs_Int8",
        NumpyInt16Type(): "PyIs_Int16",
        NumpyInt32Type(): "PyIs_Int32",
        NumpyInt64Type(): "PyIs_Int64",
        NumpyFloat32Type(): "PyIs_Float",
        NumpyFloat64Type(): "PyIs_Double",
        NumpyComplex64Type(): "PyIs_Complex64",
        NumpyComplex128Type(): "PyIs_Complex128",
    }
)

c_to_py_registry.update(
    {
        NumpyInt8Type(): "Int8_to_NumpyLong",
        NumpyInt16Type(): "Int16_to_NumpyLong",
        NumpyInt32Type(): "Int32_to_NumpyLong",
        NumpyInt64Type(): "Int64_to_NumpyLong",
        NumpyFloat32Type(): "Float_to_NumpyDouble",
        NumpyFloat64Type(): "Double_to_NumpyDouble",
        NumpyComplex64Type(): "Complex64_to_NumpyComplex",
        NumpyComplex128Type(): "Complex128_to_NumpyComplex",
    }
)

pytype_parse_registry.update(
    {
        NumpyInt8Type(): "b",
        NumpyInt16Type(): "h",
        NumpyInt32Type(): "i",
        NumpyInt64Type(): "l",
        NumpyFloat32Type(): "f",
        NumpyFloat64Type(): "d",
        NumpyComplex64Type(): "O",
        NumpyComplex128Type(): "O",
    }
)
