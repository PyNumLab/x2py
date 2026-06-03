# Datatype Mapping

This document records the shared scalar datatype policy used when C and Fortran
parser facts are converted to semantic IR. The semantic names are the stable
bridge between parser-native type spellings, `.pyi` output, readiness checks,
and eventual NumPy-oriented wrapper code.

## Semantic Names

| Semantic dtype | NumPy equivalent | Notes |
| --- | --- | --- |
| `Bool` | `numpy.bool_` | Boolean scalar. |
| `Int8`, `Int16`, `Int32`, `Int64` | `numpy.int8`, `numpy.int16`, `numpy.int32`, `numpy.int64` | Signed integers. |
| `UInt8`, `UInt16`, `UInt32`, `UInt64` | `numpy.uint8`, `numpy.uint16`, `numpy.uint32`, `numpy.uint64` | Unsigned integers. |
| `Float32`, `Float64` | `numpy.float32`, `numpy.float64` | Binary floating-point scalars. |
| `Float128` | `numpy.longdouble` | Platform precision varies; `numpy.float128` is not portable. |
| `Complex64`, `Complex128` | `numpy.complex64`, `numpy.complex128` | Complex scalars. |
| `Complex256` | `numpy.clongdouble` | Platform precision varies. |
| `String` | `numpy.str_` or byte storage at ABI boundary | Character policy depends on wrapper ABI. |
| `SizeT` | `numpy.uintp` | Target width is compiler-probed when available. |
| `Any` | `object` | Used for void pointer pointees and intentionally opaque values. |

## Fortran Intrinsics

| Fortran spelling or kind | Semantic dtype | NumPy equivalent |
| --- | --- | --- |
| `integer`, `integer(kind=4)`, `integer(int32)`, `integer(c_int)`, `integer(c_int32_t)` | `Int32` | `numpy.int32` |
| `integer(kind=1)`, `integer(int8)`, `integer(c_signed_char)`, `integer(c_int8_t)` | `Int8` | `numpy.int8` |
| `integer(kind=2)`, `integer(int16)`, `integer(c_short)`, `integer(c_int16_t)` | `Int16` | `numpy.int16` |
| `integer(kind=8)`, `integer(int64)`, `integer(c_long_long)`, `integer(c_int64_t)` | `Int64` | `numpy.int64` |
| `real`, `real(kind=8)`, `real(real64)`, `real(c_double)`, `real(kind(1.0d0))` | `Float64` | `numpy.float64` |
| `real(kind=4)`, `real(real32)`, `real(c_float)`, `real(kind(1.0e0))` | `Float32` | `numpy.float32` |
| `real(kind=16)`, `real(real128)`, `real(kind(1.0q0))` | `Float128` | `numpy.longdouble` |
| `complex`, `complex(kind=8)`, `complex(real64)`, `complex(c_double_complex)` | `Complex128` | `numpy.complex128` |
| `complex(kind=4)`, `complex(real32)`, `complex(c_float_complex)` | `Complex64` | `numpy.complex64` |
| `complex(kind=16)`, `complex(real128)` | `Complex256` | `numpy.clongdouble` |
| `logical`, `logical(kind=1/2/4/8)`, `logical(c_bool)` | `Bool` | `numpy.bool_` |
| `character`, `character(kind=1)`, `character(kind=c_char)` | `String` | `numpy.str_` or ABI byte storage |
| `procedure(...)` | `Procedure` | Callback/interface policy |

## C Types

| C spelling or parser type | Semantic dtype | NumPy equivalent |
| --- | --- | --- |
| `_Bool` / `CBool` | `Bool` | `numpy.bool_` |
| `char`, `signed char` | `Int8` | `numpy.int8` |
| `unsigned char` | `UInt8` | `numpy.uint8` |
| `short`, `unsigned short` | `Int16`, `UInt16` | `numpy.int16`, `numpy.uint16` |
| `int`, `unsigned int` | `Int32`, `UInt32` | `numpy.int32`, `numpy.uint32` |
| `long`, `long long` | `Int64` | `numpy.int64` |
| `unsigned long`, `unsigned long long` | `UInt64` | `numpy.uint64` |
| `float`, `double`, `long double` | `Float32`, `Float64`, `Float128` | `numpy.float32`, `numpy.float64`, `numpy.longdouble` |
| `float _Complex`, `double _Complex`, `long double _Complex` | `Complex64`, `Complex128`, `Complex256` | `numpy.complex64`, `numpy.complex128`, `numpy.clongdouble` |
| `int8_t`, `int16_t`, `int32_t`, `int64_t` | `Int8`, `Int16`, `Int32`, `Int64` | Matching signed NumPy integer |
| `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t` | `UInt8`, `UInt16`, `UInt32`, `UInt64` | Matching unsigned NumPy integer |
| `size_t` | `SizeT` or probed unsigned width | `numpy.uintp` or matching `numpy.uint*` |

C integer spellings such as `long` are ABI-dependent in general C, but the
current semantic policy maps parsed primitive `long` and `long long` to 64-bit
semantic dtypes. Standard-library typedefs are refined through the compiler
standard-type probe when facts are supplied.
