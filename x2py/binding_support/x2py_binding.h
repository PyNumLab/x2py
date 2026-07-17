/* Native mechanics shared by x2py-generated CPython bindings. */

#ifndef X2PY_BINDING_H
#define X2PY_BINDING_H

#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <complex.h>
#include <stdbool.h>
#include <stdint.h>

#include "numpy_version.h"

#ifndef PY_ARRAY_UNIQUE_SYMBOL
#define PY_ARRAY_UNIQUE_SYMBOL X2PY_BINDING_ARRAY_API
#endif
#ifndef X2PY_BINDING_IMPORT_ARRAY
#define NO_IMPORT_ARRAY
#endif
#include <numpy/arrayobject.h>

/* Return whether value is exactly the NumPy scalar required by numpy_type. */
bool x2py_scalar_matches(PyObject *value, int numpy_type);

/* Copy one Python scalar into caller-owned native storage after boundary checks. */
int x2py_scalar_unpack(PyObject *value, int numpy_type, void *destination);

/* Create a normal Python scalar from native storage. */
PyObject *x2py_scalar_to_python(int numpy_type, const void *value);

/* Create a NumPy scalar from native storage. */
PyObject *x2py_scalar_to_numpy(int numpy_type, const void *value);

/* Release a bridge-owned allocation transferred through a NumPy base capsule. */
void x2py_release_owned_memory(PyObject *capsule);

#endif
