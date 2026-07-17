#include "x2py_binding.h"

#include <stdlib.h>

bool x2py_scalar_matches(PyObject *value, int numpy_type)
{
    switch (numpy_type) {
    case NPY_BOOL:
        return PyBool_Check(value) || PyArray_IsScalar(value, Bool);
    case NPY_INT8:
        return PyArray_IsScalar(value, Int8);
    case NPY_INT16:
        return PyArray_IsScalar(value, Int16);
    case NPY_INT32:
        return PyArray_IsScalar(value, Int);
    case NPY_INT64:
        return PyArray_IsScalar(value, Int64);
    case NPY_FLOAT32:
        return PyArray_IsScalar(value, Float);
    case NPY_FLOAT64:
        return PyArray_IsScalar(value, Double);
    case NPY_COMPLEX64:
        return PyArray_IsScalar(value, CFloat);
    case NPY_COMPLEX128:
        return PyArray_IsScalar(value, CDouble);
    default:
        return false;
    }
}

int x2py_scalar_unpack(PyObject *value, int numpy_type, void *destination)
{
    if (destination == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "x2py generated a null scalar destination");
        return -1;
    }

    if (numpy_type == NPY_BOOL) {
        int truth = PyObject_IsTrue(value);
        if (truth < 0) {
            return -1;
        }
        *(bool *)destination = truth != 0;
        return 0;
    }
    if (x2py_scalar_matches(value, numpy_type)) {
        PyArray_ScalarAsCtype(value, destination);
        return PyErr_Occurred() == NULL ? 0 : -1;
    }

    switch (numpy_type) {
    case NPY_INT8:
        *(int8_t *)destination = (int8_t)PyLong_AsLong(value);
        break;
    case NPY_INT16:
        *(int16_t *)destination = (int16_t)PyLong_AsLong(value);
        break;
    case NPY_INT32:
        *(int32_t *)destination = (int32_t)PyLong_AsLong(value);
        break;
    case NPY_INT64:
        *(int64_t *)destination = (int64_t)PyLong_AsLongLong(value);
        break;
    case NPY_FLOAT32:
        *(float *)destination = (float)PyFloat_AsDouble(value);
        break;
    case NPY_FLOAT64:
        *(double *)destination = PyFloat_AsDouble(value);
        break;
    case NPY_COMPLEX64: {
        float real = (float)PyComplex_RealAsDouble(value);
        float imaginary = (float)PyComplex_ImagAsDouble(value);
        *(float complex *)destination = real + imaginary * I;
        break;
    }
    case NPY_COMPLEX128: {
        double real = PyComplex_RealAsDouble(value);
        double imaginary = PyComplex_ImagAsDouble(value);
        *(double complex *)destination = real + imaginary * I;
        break;
    }
    default:
        PyErr_Format(PyExc_TypeError, "unsupported x2py scalar type %d", numpy_type);
        return -1;
    }
    return PyErr_Occurred() == NULL ? 0 : -1;
}

PyObject *x2py_scalar_to_python(int numpy_type, const void *value)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "x2py generated a null scalar value");
        return NULL;
    }

    switch (numpy_type) {
    case NPY_BOOL:
        return PyBool_FromLong(*(const bool *)value);
    case NPY_INT8:
        return PyLong_FromLong(*(const int8_t *)value);
    case NPY_INT16:
        return PyLong_FromLong(*(const int16_t *)value);
    case NPY_INT32:
        return PyLong_FromLong(*(const int32_t *)value);
    case NPY_INT64:
        return PyLong_FromLongLong(*(const int64_t *)value);
    case NPY_FLOAT32:
        return PyFloat_FromDouble(*(const float *)value);
    case NPY_FLOAT64:
        return PyFloat_FromDouble(*(const double *)value);
    case NPY_COMPLEX64: {
        float complex number = *(const float complex *)value;
        return PyComplex_FromDoubles(crealf(number), cimagf(number));
    }
    case NPY_COMPLEX128: {
        double complex number = *(const double complex *)value;
        return PyComplex_FromDoubles(creal(number), cimag(number));
    }
    default:
        PyErr_Format(PyExc_TypeError, "unsupported x2py scalar type %d", numpy_type);
        return NULL;
    }
}

PyObject *x2py_scalar_to_numpy(int numpy_type, const void *value)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "x2py generated a null scalar value");
        return NULL;
    }

    PyArray_Descr *descriptor = PyArray_DescrFromType(numpy_type);
    if (descriptor == NULL) {
        return NULL;
    }
    return PyArray_Scalar((void *)value, descriptor, NULL);
}

void x2py_release_owned_memory(PyObject *capsule)
{
    void *memory = PyCapsule_GetPointer(capsule, NULL);
    if (memory == NULL) {
        PyErr_Clear();
        return;
    }
    free(memory);
}
