"""Primitive rank-zero backend type facts shared by wrapper generators."""

from __future__ import annotations

from dataclasses import replace
from typing import ClassVar

from x2py.wrapper_codegen.nodes import BackendScalarType


class PrimitiveScalarTypeRegistry:
    """Return first-lane scalar facts without coupling binding and bridge emitters."""

    TYPES: ClassVar[dict[str, BackendScalarType]] = {
        "Bool": BackendScalarType(
            "Bool",
            "bool",
            "logical(c_bool)",
            "O",
            "NPY_BOOL",
            "Bool_to_PyBool",
            "PyBool_to_Bool",
            "PyArray_IsScalar({object_name}, Bool)",
            "numpy.bool_",
            "Bool_to_PyBool",
        ),
        "Int32": BackendScalarType(
            "Int32",
            "int32_t",
            "integer(c_int32_t)",
            "O",
            "NPY_INT32",
            "Int32_to_PyLong",
            "PyInt32_to_Int32",
            "PyArray_IsScalar({object_name}, Int)",
            "numpy.int32",
            "Int32_to_NumpyLong",
        ),
        "Float32": BackendScalarType(
            "Float32",
            "float",
            "real(c_float)",
            "O",
            "NPY_FLOAT32",
            "Float_to_NumpyDouble",
            "PyFloat_to_Float",
            "PyArray_IsScalar({object_name}, Float)",
            "numpy.float32",
            "Float_to_NumpyDouble",
        ),
        "Float64": BackendScalarType(
            "Float64",
            "double",
            "real(c_double)",
            "O",
            "NPY_FLOAT64",
            "Double_to_PyDouble",
            "PyDouble_to_Double",
            "PyArray_IsScalar({object_name}, Double)",
            "numpy.float64",
            "Double_to_NumpyDouble",
        ),
        "Complex64": BackendScalarType(
            "Complex64",
            "float complex",
            "complex(c_float_complex)",
            "O",
            "NPY_COMPLEX64",
            "Complex64_to_NumpyComplex",
            "PyComplex_to_Complex64",
            "PyArray_IsScalar({object_name}, CFloat)",
            "numpy.complex64",
            "Complex64_to_NumpyComplex",
        ),
        "Complex128": BackendScalarType(
            "Complex128",
            "double complex",
            "complex(c_double_complex)",
            "O",
            "NPY_COMPLEX128",
            "Complex128_to_PyComplex",
            "PyComplex_to_Complex128",
            "PyArray_IsScalar({object_name}, CDouble)",
            "numpy.complex128",
            "Complex128_to_NumpyComplex",
        ),
    }

    @classmethod
    def type_for(cls, semantic_type_name: str) -> BackendScalarType:
        """Return editable scalar backend facts or fail with one stable diagnostic."""
        try:
            return replace(cls.TYPES[semantic_type_name])
        except KeyError:
            raise ValueError(f"Unsupported first-lane scalar type {semantic_type_name!r}") from None
