"""
Module containing the `CWrapperCodePrinter` class which is responsible for
printing the C-Python interface.
"""

import sys
from typing import ClassVar

from ..bind_c import BindCFunctionDef, BindCModule, BindCPointer
from ..bindings.c_concepts import CStrStr, ObjectAddress
from ..models.core import Declare, FunctionAddress, Import, Module, SeparatorComment
from ..bindings.cpython_api import (
    Py_None,
    Py_ssize_t,
    PyBuildValueNode,
    PyCallbackContextPush,
    PyCapsule_Import,
    PyCapsule_New,
    PyFunctionOverloadSet,
    PythonObjectType,
    PythonTypeObjectType,
    PyModule_Create,
    PyTuple_Pack,
    PythonClassType,
    WrapperCustomDataType,
)
from ..models.datatypes import (
    FinalType,
    Literal,
    NIL,
    NumpyNDArrayType,
    PrimitiveBooleanType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    convert_to_literal,
)
from ..bindings.numpy_cpython_api import NumpyArrayObjectType
from .ccode import CCodePrinter

__all__ = ("CPythonCodePrinter",)

module_imports = [
    Import("numpy_version", Module("numpy_version", (), ())),
    Import("numpy/arrayobject", Module("numpy/arrayobject", (), ())),
    Import("x2py_runtime/python_runtime", Module("x2py_runtime", (), ())),
]


class CPythonCodePrinter(CCodePrinter):
    """
    A printer for printing the C-Python interface.

    A printer to convert X2py's AST describing a translated module,
    to strings of C code which provide an interface between the module
    and Python code.
    As for all printers the navigation of this file is done via _visit_X
    functions.

    Parameters
    ----------
    filename : str
            The name of the file being converted.
    **settings : dict
            Any additional arguments which are necessary for CCodePrinter.
    """

    dtype_registry: ClassVar = {
        **CCodePrinter.dtype_registry,
        PythonObjectType(): "PyObject",
        NumpyArrayObjectType(): "PyArrayObject",
        PythonTypeObjectType(): "PyTypeObject",
        BindCPointer(): "void",
    }

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, filename, **settings):
        """Initialize the state used for one generation run."""
        CCodePrinter.__init__(self, filename, **settings)
        self._to_free_PyObject_list = []
        self._function_wrapper_names = {}
        self._module_name = None

    # --------------------------------------------------------------------
    #                       Helper functions
    # --------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

    def _visit_PyCallbackValidate(self, expr):
        """Render the ``PyCallbackValidate`` model node."""
        metadata = expr.callback.decorators.get("x2py_callback_abi", {})
        callback_name = str(getattr(metadata.get("native"), "name", expr.callback.name))
        python_object = self._visit(ObjectAddress(expr.python_object))
        return (
            f"if (!PyCallable_Check({python_object})) {{\n"
            f'    PyErr_SetString(PyExc_TypeError, "callback {callback_name} must be callable");\n'
            f"    return {self._visit(expr.error_exit)};\n"
            "}\n"
        )

    def _visit_PyCallbackContextPush(self, expr):
        """Render the ``PyCallbackContextPush`` model node."""
        context_type, current_name, _ = self._callback_context_names(expr.callback)
        context_name = f"{self._callback_identifier(expr.callback)}_context"
        python_object = self._visit(ObjectAddress(expr.python_object))
        return (
            f"{context_type} {context_name} = "
            f"{{{python_object}, PyThread_get_thread_ident(), {current_name}, NULL}};\n"
            f"Py_INCREF({python_object});\n"
            f"{current_name} = &{context_name};\n"
        )

    def _visit_PyCallbackContextPop(self, expr):
        """Render the ``PyCallbackContextPop`` model node."""
        _, current_name, _ = self._callback_context_names(expr.callback)
        context_name = f"{self._callback_identifier(expr.callback)}_context"
        return (
            f"{current_name} = {context_name}.previous;\n"
            f"Py_XDECREF({context_name}.last_result);\n"
            f"Py_DECREF({context_name}.callable);\n"
        )

    def _visit_PyAllowThreadsBegin(self, expr):
        """Render the ``PyAllowThreadsBegin`` model node."""
        return "Py_BEGIN_ALLOW_THREADS\n"

    def _visit_PyAllowThreadsEnd(self, expr):
        """Render the ``PyAllowThreadsEnd`` model node."""
        return "Py_END_ALLOW_THREADS\n"

    def _visit_PyFunctionDef(self, expr):
        """Render the ``PyFunctionDef`` model node."""
        callbacks = [item.callback for item in expr.body.body if isinstance(item, PyCallbackContextPush)]
        support = "".join(self._callback_support_code(callback) for callback in callbacks)
        return support + CCodePrinter._visit_FunctionDef(self, expr)

    def _visit_DottedName(self, expr):
        """Render the ``DottedName`` model node."""
        names = expr.name
        return ".".join(self._visit(n) for n in names)

    def _visit_PyFunctionOverloadSet(self, expr):
        """Render the ``PyFunctionOverloadSet`` model node."""
        funcs_to_visit = (*expr.functions, expr.type_check_func, expr.dispatcher_func)
        return "\n".join(self._visit(f) for f in funcs_to_visit)

    def _visit_PyArg_ParseTupleNode(self, expr):
        """Render the ``PyArg_ParseTupleNode`` model node."""
        name = "PyArg_ParseTupleAndKeywords"
        pyarg = expr.pyarg
        pykwarg = expr.pykwarg
        flags = expr.flags
        # All args are modified so even pointers are passed by address
        args = ", ".join(f"&{a.name}" for a in expr.args)

        if expr.args:
            code = f'{name}({pyarg}, {pykwarg}, "{flags}", {expr.arg_names.name}, {args})'
        else:
            code = f'{name}({pyarg}, {pykwarg}, "", {expr.arg_names.name})'

        return code

    def _visit_PyBuildValueNode(self, expr):
        """Render the ``PyBuildValueNode`` model node."""
        name = "Py_BuildValue"
        flags = expr.flags
        args = ", ".join(self._visit(a) for a in expr.args)
        # to change for args rank 1 +
        return f'(*{name}("{flags}", {args}))' if expr.args else f'(*{name}(""))'

    def _visit_PyArgKeywords(self, expr):
        """Render the ``PyArgKeywords`` model node."""
        arg_names = ",\n".join([f'(char*)"{a}"' for a in expr.arg_names] + [self._visit(NIL)])
        return f"static char *{expr.name}[] = {{\n{arg_names}\n}};\n"

    def _visit_PyModule_AddObject(self, expr):
        """Render the ``PyModule_AddObject`` model node."""
        name = self._visit(expr.name)
        var = self._visit(expr.variable)
        if expr.variable.dtype is not PythonObjectType():
            var = f"(PyObject*) {var}"
        return f"PyModule_AddObject({expr.mod_name}, {name}, {var})"

    def _visit_PyCapsule_New(self, expr):
        """Render the ``PyCapsule_New`` model node."""
        name = expr.capsule_name
        var = self._visit(ObjectAddress(expr.API_var))
        return f'PyCapsule_New((void *){var}, "{name}", NULL)'

    def _visit_PyCapsule_Import(self, expr):
        """Render the ``PyCapsule_Import`` model node."""
        name = expr.capsule_name
        return f'(void**)PyCapsule_Import("{name}", 0)'

    def _visit_PyModule_Create(self, expr):
        """Render the ``PyModule_Create`` model node."""
        return f"PyModule_Create(&{expr.module_def_name})"

    def _visit_ModuleHeader(self, expr):
        """Render the ``ModuleHeader`` model node."""
        mod = expr.module
        self.set_scope(mod.scope)
        name = mod.name

        # Print imports last to be sure that all additional_imports have been collected
        imports = [*module_imports, *mod.imports]
        for i in imports:
            self.add_import(i)
        imports = "".join(self._visit(i) for i in imports)

        function_signatures = "".join(
            self._function_signature(f, print_arg_names=False) + ";\n" for f in mod.external_funcs
        )

        API_var = mod.variables[0]

        macro_defs = ""
        type_declarations = ""
        classes = []
        for i, c in enumerate(mod.classes):
            struct_name = c.struct_name
            type_name = c.type_name
            attributes = "".join(self._visit(Declare(a)) for a in c.attributes)
            classes.append(f"struct {struct_name} {{\n    PyObject_HEAD\n" + attributes + "};\n")
            type_declarations += f"static PyTypeObject {c.type_name};\n"
            sig_methods = (
                *c.methods,
                c.new_func,
                *tuple(f for i in c.overload_sets for f in i.functions),
                *tuple(i.dispatcher_func for i in c.overload_sets),
                *tuple(getset for p in c.properties for getset in (p.getter, p.setter) if getset),
                *tuple(
                    method.dispatcher_func if isinstance(method, PyFunctionOverloadSet) else method
                    for method in c.magic_methods
                ),
            )
            function_signatures += "\n" + "".join(self._function_signature(f) + ";\n" for f in sig_methods)
            macro_defs += f"#define {type_name} (*(PyTypeObject*){API_var.name}[{i}])\n"

        class_code = "\n".join(classes)

        static_import_decs = self._visit(Declare(API_var, static=True))
        import_func = self._visit(mod.import_func)

        self.exit_scope()
        header_id = f"{name.upper()}_WRAPPER"
        header_guard = f"{header_id}_H"
        start = f"#ifndef {header_guard}\n#define {header_guard}\n"
        end = f"#endif\n#endif // {header_guard}\n"
        parts = (
            start,
            imports,
            class_code,
            f"#ifdef {header_id}\n",
            type_declarations,
            function_signatures,
            "#else\n",
            static_import_decs,
            macro_defs,
            import_func,
            end,
        )
        return "\n".join(p for p in parts if p)

    def _visit_PyModule(self, expr):
        """Render the ``PyModule`` model node."""
        scope = expr.scope
        self.set_scope(scope)

        # Insert declared objects into scope
        variables = expr.original_module.variables if isinstance(expr, BindCModule) else expr.variables
        for f in expr.funcs:
            scope.insert_symbol(f.name.lower())
        for v in variables:
            if not v.is_private:
                scope.insert_symbol(v.name.lower())

        funcs = []

        self._module_name = expr.name
        sep = self._visit(SeparatorComment(40))

        dispatcher_funcs = [f.name for i in expr.overload_sets for f in i.functions]
        funcs += [
            *expr.overload_sets,
            *(f for f in expr.funcs if f.name not in dispatcher_funcs),
        ]

        self._in_header = True
        decs = "".join(self._visit(d) for d in expr.declarations)
        self._in_header = False

        function_defs = "\n".join(self._visit(f) for f in funcs)

        class_defs = f"\n{sep}\n".join(self._visit(c) for c in expr.classes)

        method_def_func = "".join(
            ('{{\n"{name}",\n(PyCFunction){wrapper_name},\nMETH_VARARGS | METH_KEYWORDS,\n{docstring}\n}},\n').format(
                name=self._get_python_name(expr.scope, f.original_function),
                wrapper_name=f.name,
                docstring=(
                    self._visit(CStrStr(convert_to_literal("\n".join(f.docstring.comments)))) if f.docstring else '""'
                ),
            )
            for f in funcs
            if not getattr(f, "is_header", False)
        )

        method_def_name = self.scope.get_new_name(f"{expr.name}_methods", object_type="wrapper")
        method_def = f"static PyMethodDef {method_def_name}[] = {{\n{method_def_func}{{ NULL, NULL, 0, NULL}}\n}};\n"
        module_doc_lines = [
            str(expr.name),
            "",
            "Functions",
            "---------",
            *[
                self._get_python_name(expr.scope, f.original_function)
                for f in funcs
                if not getattr(f, "is_header", False)
            ],
            "",
            "Classes",
            "-------",
            *[str(expr.scope.get_python_name(c.name)) for c in expr.classes],
        ]
        module_docstring = self._visit(CStrStr(convert_to_literal("\n".join(module_doc_lines))))

        module_def = (
            f"static struct PyModuleDef {expr.module_def_name} = {{\n"
            "PyModuleDef_HEAD_INIT,\n"
            "/* name of module */\n"
            f'"{self._module_name}",\n'
            "/* module documentation, may be NULL */\n"
            f"{module_docstring},\n"
            "/* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */\n"
            "0,\n"
            f"{method_def_name},\n"
            "};\n"
        )

        init_func = self._visit(expr.init_func)

        pymod_name = f"{expr.name}_wrapper"
        imports = [
            Import(pymod_name, Module(pymod_name, (), ())),
            *self._additional_imports.values(),
        ]
        imports = "".join(self._visit(i) for i in imports)

        self.exit_scope()

        return "\n".join(
            [
                "#define PY_ARRAY_UNIQUE_SYMBOL CWRAPPER_ARRAY_API",
                f"#define {pymod_name.upper()}\n",
                imports,
                self._x2py_malloc_helper(),
                decs,
                sep,
                class_defs,
                sep,
                function_defs,
                sep,
                method_def,
                sep,
                module_def,
                sep,
                init_func,
            ]
        )

    def _visit_PyClassDef(self, expr):
        """Render the ``PyClassDef`` model node."""
        struct_name = expr.struct_name
        type_name = expr.type_name
        name = self.scope.get_python_name(expr.name)
        class_docstring = (
            self._visit(CStrStr(convert_to_literal("\n".join(expr.docstring.comments)))) if expr.docstring else '""'
        )

        original_scope = expr.original_class.scope
        getters = tuple(p.getter for p in expr.properties)
        setters = tuple(p.setter for p in expr.properties if p.setter)
        print_methods = (*expr.methods, expr.new_func, *expr.overload_sets, *expr.magic_methods, *getters, *setters)
        functions = "\n".join(self._visit(f) for f in print_methods)
        init_string = ""
        del_string = ""
        funcs = {}
        for f in expr.methods:
            py_name = self._get_python_name(original_scope, f.original_function)
            if py_name == "__init__":
                init_string = f"    .tp_init = (initproc) {f.name},\n"
            elif py_name == "__del__":
                del_string = f"    .tp_dealloc = (destructor) {f.name},\n"
            else:
                method_docstring = (
                    self._visit(CStrStr(convert_to_literal("\n".join(f.docstring.comments)))) if f.docstring else '""'
                )
                original_args = f.original_function.arguments
                flags = "METH_VARARGS | METH_KEYWORDS"
                if not original_args or not original_args[0].bound_argument:
                    flags += " | METH_STATIC"
                funcs[py_name] = (f.name, method_docstring, flags)

        for f in expr.overload_sets:
            py_name = self._get_python_name(original_scope, f.original_function)
            method_docstring = (
                self._visit(CStrStr(convert_to_literal("\n".join(f.docstring.comments)))) if f.docstring else '""'
            )
            funcs[py_name] = (f.name, method_docstring, "METH_VARARGS | METH_KEYWORDS")

        property_definitions = "".join(
            "".join(
                (
                    "{\n",
                    f'"{p.python_name}",\n',
                    f"(getter) {p.getter.name},\n",
                    f"(setter) {p.setter.name},\n" if p.setter else "(setter) NULL,\n",
                    f"{self._visit(p.docstring)},\n",
                    "NULL\n",
                    "},\n",
                )
            )
            for p in expr.properties
        )
        property_definitions += "{ NULL }\n"

        method_def_funcs = "".join(
            (f'{{\n"{name}",\n(PyCFunction){wrapper_name},\n{flags},\n{doc_string}\n}},\n')
            for name, (wrapper_name, doc_string, flags) in funcs.items()
        )

        magic_methods = {self._get_python_name(original_scope, f.original_function): f for f in expr.magic_methods}

        number_magic_method_name = self.scope.get_new_name(f"{expr.name}_number_methods", object_type="wrapper")

        number_magic_methods_def = f"static PyNumberMethods {number_magic_method_name} = {{\n"
        if "__add__" in magic_methods:
            number_magic_methods_def += f"     .nb_add = (binaryfunc){magic_methods['__add__'].name},\n"
        if "__sub__" in magic_methods:
            number_magic_methods_def += f"     .nb_subtract = (binaryfunc){magic_methods['__sub__'].name},\n"
        if "__mul__" in magic_methods:
            number_magic_methods_def += f"     .nb_multiply = (binaryfunc){magic_methods['__mul__'].name},\n"
        if "__truediv__" in magic_methods:
            number_magic_methods_def += f"     .nb_true_divide = (binaryfunc){magic_methods['__truediv__'].name},\n"
        if "__pow__" in magic_methods:
            number_magic_methods_def += f"     .nb_power = (ternaryfunc){magic_methods['__pow__'].name},\n"
        if "__neg__" in magic_methods:
            number_magic_methods_def += f"     .nb_negative = (unaryfunc){magic_methods['__neg__'].name},\n"
        if "__pos__" in magic_methods:
            number_magic_methods_def += f"     .nb_positive = (unaryfunc){magic_methods['__pos__'].name},\n"
        if "__invert__" in magic_methods:
            number_magic_methods_def += f"     .nb_invert = (unaryfunc){magic_methods['__invert__'].name},\n"
        if "__lshift__" in magic_methods:
            number_magic_methods_def += f"     .nb_lshift = (binaryfunc){magic_methods['__lshift__'].name},\n"
        if "__rshift__" in magic_methods:
            number_magic_methods_def += f"     .nb_rshift = (binaryfunc){magic_methods['__rshift__'].name},\n"
        if "__and__" in magic_methods:
            number_magic_methods_def += f"     .nb_and = (binaryfunc){magic_methods['__and__'].name},\n"
        if "__or__" in magic_methods:
            number_magic_methods_def += f"     .nb_or = (binaryfunc){magic_methods['__or__'].name},\n"
        if "__iadd__" in magic_methods:
            number_magic_methods_def += f"     .nb_inplace_add = (binaryfunc){magic_methods['__iadd__'].name},\n"
        if "__isub__" in magic_methods:
            number_magic_methods_def += f"     .nb_inplace_subtract = (binaryfunc){magic_methods['__isub__'].name},\n"
        if "__imul__" in magic_methods:
            number_magic_methods_def += f"     .nb_inplace_multiply = (binaryfunc){magic_methods['__imul__'].name},\n"
        if "__itruediv__" in magic_methods:
            number_magic_methods_def += (
                f"     .nb_inplace_true_divide = (binaryfunc){magic_methods['__itruediv__'].name},\n"
            )
        if "__ilshift__" in magic_methods:
            number_magic_methods_def += f"     .nb_inplace_lshift = (binaryfunc){magic_methods['__ilshift__'].name},\n"
        if "__irshift__" in magic_methods:
            number_magic_methods_def += f"     .nb_inplace_rshift = (binaryfunc){magic_methods['__irshift__'].name},\n"
        if "__iand__" in magic_methods:
            number_magic_methods_def += f"     .nb_inplace_and = (binaryfunc){magic_methods['__iand__'].name},\n"
        if "__ior__" in magic_methods:
            number_magic_methods_def += f"     .nb_inplace_or = (binaryfunc){magic_methods['__ior__'].name},\n"
        number_magic_methods_def += "};\n"

        seq_magic_method_name = self.scope.get_new_name(f"{expr.name}_sequence_methods", object_type="wrapper")

        seq_magic_methods_def = f"static PySequenceMethods {seq_magic_method_name} = {{\n"
        if "__len__" in magic_methods:
            seq_magic_methods_def += f"    .sq_length = (lenfunc){magic_methods['__len__'].name},\n"
        seq_magic_methods_def += "};\n"

        map_magic_method_name = self.scope.get_new_name(f"{expr.name}_mapping_methods", object_type="wrapper")
        map_magic_methods_def = f"static PyMappingMethods {map_magic_method_name} = {{\n"
        if "__len__" in magic_methods:
            map_magic_methods_def += f"    .mp_length = (lenfunc){magic_methods['__len__'].name},\n"
        if "__getitem__" in magic_methods:
            map_magic_methods_def += f"     .mp_subscript = (binaryfunc){magic_methods['__getitem__'].name},\n"
        map_magic_methods_def += "};\n"
        method_def_name = self.scope.get_new_name(f"{expr.name}_methods", object_type="wrapper")
        method_def = f"static PyMethodDef {method_def_name}[] = {{\n{method_def_funcs}{{ NULL, NULL, 0, NULL}}\n}};\n"

        property_def_name = self.scope.get_new_name(f"{expr.name}_properties", object_type="wrapper")
        property_def = f"static PyGetSetDef {property_def_name}[] = {{\n{property_definitions}}};\n"

        comparison_ops = {
            "__eq__": "Py_EQ",
            "__ne__": "Py_NE",
            "__lt__": "Py_LT",
            "__le__": "Py_LE",
            "__gt__": "Py_GT",
            "__ge__": "Py_GE",
        }
        richcompare_methods = {
            method_name: magic_methods[method_name] for method_name in comparison_ops if method_name in magic_methods
        }
        richcompare_def = ""
        richcompare_slot = ""
        if richcompare_methods:
            richcompare_name = self.scope.get_new_name(f"{expr.name}_richcompare", object_type="wrapper")
            cases = "".join(
                f"    case {comparison_ops[method_name]}:\n        return {method.name}(lhs, rhs);\n"
                for method_name, method in richcompare_methods.items()
            )
            richcompare_def = (
                f"static PyObject *{richcompare_name}(PyObject *lhs, PyObject *rhs, int op)\n"
                "{\n"
                "    switch (op) {\n"
                f"{cases}"
                "    default:\n"
                "        Py_INCREF(Py_NotImplemented);\n"
                "        return Py_NotImplemented;\n"
                "    }\n"
                "}\n"
            )
            richcompare_slot = f"    .tp_richcompare = {richcompare_name},\n"

        base_slot = ""
        if expr.original_class.superclasses:
            base_class = expr.original_class.superclasses[0]
            base_python_name = base_class.scope.get_python_name(base_class.name)
            wrapped_base = self.scope.find(base_python_name, "classes", raise_if_missing=True)
            base_slot = f"    .tp_base = &{wrapped_base.type_name},\n"

        type_code = (
            f"static PyTypeObject {type_name} = {{\n"
            "    PyVarObject_HEAD_INIT(NULL, 0)\n"
            f'    .tp_name = "{self._module_name}.{name}",\n'
            f"    .tp_as_number = &{number_magic_method_name},\n"
            f"    .tp_as_sequence = &{seq_magic_method_name},\n"
            f"    .tp_as_mapping = &{map_magic_method_name},\n"
            f"    .tp_doc = PyDoc_STR({class_docstring}),\n"
            f"    .tp_basicsize = sizeof(struct {struct_name}),\n"
            "    .tp_itemsize = 0,\n"
            "    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,\n"
            f"    .tp_new = {expr.new_func.name},\n"
            f"{base_slot}"
            f"{init_string}{del_string}"
            f"{richcompare_slot}"
            f"    .tp_methods = {method_def_name},\n"
            f"    .tp_getset = {property_def_name},\n"
            "};\n"
        )

        return "\n".join(
            (
                method_def,
                number_magic_methods_def,
                seq_magic_methods_def,
                map_magic_methods_def,
                property_def,
                richcompare_def,
                type_code,
                functions,
            )
        )

    def _visit_PyModInitFunc(self, expr):
        """Render the ``PyModInitFunc`` model node."""
        decs = "".join(self._visit(d) for d in expr.declarations)
        body = self._visit(expr.body)
        return "".join([f"PyMODINIT_FUNC {expr.name}(void)\n{{\n", decs, body, "}\n"])

    def _visit_Allocate(self, expr):
        """Render the ``Allocate`` model node."""
        variable = expr.variable
        if isinstance(variable.dtype, WrapperCustomDataType):
            cls_base = variable.cls_base.original_class
            class_def = self.scope.find(cls_base.scope.get_python_name(cls_base.name), "classes")

            type_name = class_def.type_name
            var_code = self._visit(ObjectAddress(variable))
            decl_type = self._get_declare_type(variable)
            return f"{var_code} = ({decl_type}){type_name}.tp_alloc(&{type_name}, 0);\n"
        return CCodePrinter._visit_Allocate(self, expr)

    def _visit_Deallocate(self, expr):
        """Render the ``Deallocate`` model node."""
        variable = expr.variable
        if isinstance(variable.dtype, WrapperCustomDataType):
            cls_base = variable.cls_base.original_class
            class_def = self.scope.find(cls_base.scope.get_python_name(cls_base.name), "classes")

            type_name = class_def.type_name
            var_code = self._visit(ObjectAddress(variable))
            return f"{type_name}.tp_free({var_code});\n"
        return CCodePrinter._visit_Deallocate(self, expr)

    def _visit_Declare(self, expr):
        """Render the ``Declare`` model node."""
        var = expr.variable
        if isinstance(var.dtype, BindCPointer):
            declaration_type = "void*"

            static = "static " if expr.static else ""
            external = "extern " if expr.external else ""

            variable = self._visit(expr.variable.name)

            init = f" = {self._visit(expr.value)}" if expr.value is not None else ""
            if var.rank == 0:
                return f"{static}{external}{declaration_type} {variable}{init};\n"

            size = var.shape[0]
            if isinstance(size, Literal):
                return f"{static}{external}{declaration_type} {variable}[{size}];\n"
            return f"{static}{external}{declaration_type}* {variable}{init};\n"
        return CCodePrinter._visit_Declare(self, expr)

    def _visit_IndexedElement(self, expr):
        """Render the ``IndexedElement`` model node."""
        if isinstance(expr.base.class_type, NumpyNDArrayType) and expr.base.class_type.raw:
            base = self._visit(expr.base.name)
            idxs = "".join(f"[{self._visit(a)}]" for a in expr.indices)
            return f"{base}{idxs}"
        return CCodePrinter._visit_IndexedElement(self, expr)

    def _visit_Cast(self, expr):
        """Render the ``Cast`` model node."""
        if expr.dtype is Py_ssize_t():
            return f"(Py_ssize_t){self._visit(expr.arg)}"
        return super()._visit_Cast(expr)

    def _visit_PyTuple_Pack(self, expr):
        """Render the ``PyTuple_Pack`` model node."""
        args = expr.args
        n = len(args)
        if n:
            args_code = ", ".join(self._visit(a) for a in args)
            return f"(*PyTuple_Pack( {n}, {args_code} ))"
        return f"(*PyTuple_Pack( {n} ))"

    def _visit_PyList_Clear(self, expr):
        """Render the ``PyList_Clear`` model node."""
        list_code = self._visit(ObjectAddress(expr.list_obj))
        if sys.version_info < (3, 13):
            return f"PyList_SetSlice({list_code}, 0, PY_SSIZE_T_MAX, NULL)"
        return f"PyList_Clear({list_code})"

    def _visit_PyArgumentError(self, expr):
        """Render the ``PyArgumentError`` model node."""
        args = ", ".join(
            [f'"{self._visit(expr.error_msg)}"']
            + [f"PyObject_Str((PyObject*)Py_TYPE({self._visit(a)}))" for a in expr.args]
        )
        return f"PyErr_SetObject({self._visit(expr.error_type)}, PyUnicode_FromFormat({args}));\n"

    def _visit_BindCModuleVariable(self, expr):
        """Render the ``BindCModuleVariable`` model node."""
        if self._is_c_pointer(expr):
            return f"(*{expr.name.lower()})"
        return expr.name.lower()

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _is_c_pointer(self, a):
        """
        Indicate whether the object is a pointer in C code.

        This function extends `CCodePrinter._is_c_pointer` to specify more objects
        which are always accessed via a C pointer.

        Parameters
        ----------
        a : model object
            The object whose storage we are enquiring about.

        Returns
        -------
        bool
            True if a C pointer, False otherwise.

        See Also
        --------
        CCodePrinter._is_c_pointer : The extended function.
        """
        if isinstance(a, FunctionAddress):
            return False
        if (
            isinstance(a.class_type, WrapperCustomDataType | BindCPointer | PyTuple_Pack)
            or (isinstance(a.class_type, NumpyNDArrayType) and a.class_type.raw)
        ) or isinstance(a, PyBuildValueNode | PyCapsule_New | PyCapsule_Import | PyModule_Create):
            return True
        return CCodePrinter._is_c_pointer(self, a)

    def _get_python_name(self, scope, obj):
        """
        Get the name of object as defined in the original python code.

        Get the name of the object as it was originally defined in the
        Python code being translated. This name may have changed before
        the printing stage in the case of name clashes or language interfaces.

        Parameters
        ----------
        scope : x2py.parser.scope.Scope
            The scope where the object was defined.

        obj : codegen model object
            The object whose name we wish to identify.

        Returns
        -------
        str
            The original name of the object.
        """
        if isinstance(obj, BindCFunctionDef):
            return scope.get_python_name(obj.original_function.name)
        if isinstance(obj, BindCModule):
            return obj.original_module.name
        return scope.get_python_name(obj.name)

    def _function_signature(self, expr, print_arg_names=True):
        """Handle function signature for the current generation context."""
        args = list(expr.arguments)
        if any(isinstance(a.var, FunctionAddress) and not a.var.decorators.get("x2py_callback_abi") for a in args):
            return ""
        return CCodePrinter._function_signature(self, expr, print_arg_names)

    def _get_declare_type(self, expr):
        """
        Get the string which describes the type in a declaration.

        This function extends `CCodePrinter._get_declare_type` to specify types
        which are only relevant in the C-Python interface.

        Parameters
        ----------
        expr : Variable
            The variable whose type should be described.

        Returns
        -------
        str
            The code describing the type.

        Raises
        ------
        X2pyCodegenError
            If the type is not supported in the C code or the rank is too large.

        See Also
        --------
        CCodePrinter._get_declare_type : The extended function.
        """
        if expr.dtype is BindCPointer():
            if isinstance(expr.class_type, FinalType):
                return "const void*"
            return "void*"
        if expr.dtype is Py_ssize_t():
            dtype = "Py_ssize_t*" if self._is_c_pointer(expr) else "Py_ssize_t"
            if isinstance(expr.class_type, FinalType):
                return f"const {dtype}"
            return dtype
        return CCodePrinter._get_declare_type(self, expr)

    @staticmethod
    def _callback_identifier(callback):
        """Handle callback identifier for the current generation context."""
        return str(callback.name).replace("-", "_")

    def _callback_context_names(self, callback):
        """Handle callback context names for the current generation context."""
        identifier = self._callback_identifier(callback)
        return (
            f"x2py_callback_context_{identifier}",
            f"x2py_callback_current_{identifier}",
            f"x2py_callback_abort_{identifier}",
        )

    @staticmethod
    def _callback_numpy_typenum(dtype):
        """Handle callback numpy typenum for the current generation context."""
        primitive = dtype.primitive_type
        precision = dtype.precision
        mapping = {
            (PrimitiveBooleanType(), -1): "NPY_BOOL",
            (PrimitiveIntegerType(), 1): "NPY_INT8",
            (PrimitiveIntegerType(), 2): "NPY_INT16",
            (PrimitiveIntegerType(), 4): "NPY_INT32",
            (PrimitiveIntegerType(), 8): "NPY_INT64",
            (PrimitiveFloatingPointType(), 4): "NPY_FLOAT32",
            (PrimitiveFloatingPointType(), 8): "NPY_FLOAT64",
            (PrimitiveComplexType(), 4): "NPY_COMPLEX64",
            (PrimitiveComplexType(), 8): "NPY_COMPLEX128",
        }
        try:
            return mapping[(primitive, precision)]
        except KeyError:
            raise TypeError(f"Unsupported callback NumPy dtype {dtype}") from None

    def _callback_scalar_to_python(self, var, value):
        """Handle callback scalar to python for the current generation context."""
        primitive = var.dtype.primitive_type
        if isinstance(primitive, PrimitiveBooleanType):
            return f"PyBool_FromLong(({value}) ? 1 : 0)"
        if isinstance(primitive, PrimitiveIntegerType):
            return f"PyLong_FromLongLong((long long)({value}))"
        if isinstance(primitive, PrimitiveFloatingPointType):
            return f"PyFloat_FromDouble((double)({value}))"
        if isinstance(primitive, PrimitiveComplexType):
            return f"PyComplex_FromDoubles((double)creal({value}), (double)cimag({value}))"
        raise TypeError(f"Unsupported callback scalar type {var.class_type}")

    def _callback_scalar_from_python(self, var, value):
        """Handle callback scalar from python for the current generation context."""
        primitive = var.dtype.primitive_type
        c_type = self._get_declare_type(var)
        if isinstance(primitive, PrimitiveBooleanType):
            return f"({c_type})PyObject_IsTrue({value})"
        if isinstance(primitive, PrimitiveIntegerType):
            return f"({c_type})PyLong_AsLongLong({value})"
        if isinstance(primitive, PrimitiveFloatingPointType):
            return f"({c_type})PyFloat_AsDouble({value})"
        if isinstance(primitive, PrimitiveComplexType):
            return f"({c_type})(PyComplex_RealAsDouble({value}) + PyComplex_ImagAsDouble({value}) * I)"
        raise TypeError(f"Unsupported callback scalar type {var.class_type}")

    def _callback_wrapped_class(self, native_var, callback):
        """Handle callback wrapped class for the current generation context."""
        wrapped = self.scope.find(native_var.dtype.name, "classes")
        if wrapped is None:
            raise TypeError(f"Callback derived type {native_var.dtype.name} has no generated Python wrapper")
        return wrapped

    def _callback_argument_code(self, callback, mapping, index, abort_name):
        """Handle callback argument code for the current generation context."""
        native = mapping["native"]
        abi = mapping["abi"]
        py_name = f"callback_arg_{index}"
        if mapping["kind"] == "scalar":
            expression = self._callback_scalar_to_python(native, str(abi[0].name))
            setup = f"PyObject *{py_name} = {expression};\n"
        elif mapping["kind"] == "array":
            data, *shape = abi
            dims_name = f"callback_dims_{index}"
            strides_name = f"callback_strides_{index}"
            dimensions = ", ".join(f"(npy_intp){item.name}" for item in shape)
            stride_lines = [f"{strides_name}[0] = (npy_intp)sizeof({self._c_type(native.dtype)});"]
            stride_lines.extend(
                f"{strides_name}[{i}] = {strides_name}[{i - 1}] * {dims_name}[{i - 1}];" for i in range(1, native.rank)
            )
            flags = "NPY_ARRAY_F_CONTIGUOUS | NPY_ARRAY_ALIGNED"
            if getattr(native, "intent", "in") != "in":
                flags += " | NPY_ARRAY_WRITEABLE"
            setup = (
                f"npy_intp {dims_name}[{native.rank}] = {{{dimensions}}};\n"
                f"npy_intp {strides_name}[{native.rank}];\n" + "\n".join(stride_lines) + "\n"
                f"PyObject *{py_name} = PyArray_New(&PyArray_Type, {native.rank}, {dims_name}, "
                f"{self._callback_numpy_typenum(native.dtype)}, {strides_name}, {data.name}, 0, {flags}, NULL);\n"
            )
        elif mapping["kind"] == "derived":
            wrapped = self._callback_wrapped_class(native, callback)
            setup = (
                f"struct {wrapped.struct_name} *{py_name}_value = "
                f"(struct {wrapped.struct_name} *){wrapped.type_name}.tp_alloc(&{wrapped.type_name}, 0);\n"
                f"PyObject *{py_name} = (PyObject *){py_name}_value;\n"
                f"if ({py_name} != NULL) {{\n"
                f"    {py_name}_value->instance = {abi[0].name};\n"
                f"    {py_name}_value->referenced_objects = PyList_New(0);\n"
                f"    {py_name}_value->is_alias = 1;\n"
                "}\n"
            )
        else:
            raise TypeError(f"Unsupported callback ABI argument kind {mapping['kind']}")
        return (
            setup
            + f'if ({py_name} == NULL) {abort_name}("failed to convert callback argument");\n'
            + f"PyTuple_SET_ITEM(callback_args, {index}, {py_name});\n"
        )

    def _callback_result_code(self, callback, result, context_name, abort_name):
        """Handle callback result code for the current generation context."""
        kind = result["kind"]
        native = result["native"]
        if kind == "none":
            return (
                "if (callback_result != Py_None) {\n"
                '    PyErr_SetString(PyExc_TypeError, "callback subroutine must return None");\n'
                f'    {abort_name}("invalid callback return value");\n'
                "}\n"
                "Py_DECREF(callback_result);\n"
                "PyGILState_Release(callback_gil);\n"
                "return;\n"
            )
        if kind == "scalar":
            c_type = self._get_declare_type(native)
            conversion = self._callback_scalar_from_python(native, "callback_result")
            return (
                f"{c_type} callback_value = {conversion};\n"
                f'if (PyErr_Occurred()) {abort_name}("invalid callback return value");\n'
                "Py_DECREF(callback_result);\n"
                "PyGILState_Release(callback_gil);\n"
                "return callback_value;\n"
            )
        if kind == "array":
            shape_checks = []
            for index, item in enumerate(native.alloc_shape):
                if item is not None:
                    shape_checks.append(
                        f"PyArray_DIM((PyArrayObject *)callback_result, {index}) != {self._visit(item)}"
                    )
            conditions = [
                "!PyArray_Check(callback_result)",
                f"PyArray_TYPE((PyArrayObject *)callback_result) != {self._callback_numpy_typenum(native.dtype)}",
                f"PyArray_NDIM((PyArrayObject *)callback_result) != {native.rank}",
                "!PyArray_CHKFLAGS((PyArrayObject *)callback_result, NPY_ARRAY_F_CONTIGUOUS | NPY_ARRAY_ALIGNED)",
                *shape_checks,
            ]
            condition = " ||\n    ".join(conditions)
            validation = (
                f"if ({condition}) {{\n"
                '    PyErr_SetString(PyExc_TypeError, "callback returned an incompatible array");\n'
                f'    {abort_name}("invalid callback return value");\n'
                "}\n"
            )
        elif kind == "derived":
            wrapped = self._callback_wrapped_class(native, callback)
            validation = (
                f"if (!PyObject_TypeCheck(callback_result, &{wrapped.type_name})) {{\n"
                f'    PyErr_SetString(PyExc_TypeError, "callback must return {native.dtype.name}");\n'
                f'    {abort_name}("invalid callback return value");\n'
                "}\n"
            )
        else:
            raise TypeError(f"Unsupported callback ABI result kind {kind}")

        pointer = (
            "PyArray_DATA((PyArrayObject *)callback_result)"
            if kind == "array"
            else f"((struct {self._callback_wrapped_class(native, callback).struct_name} *)callback_result)->instance"
        )
        return (
            validation
            + f"Py_XDECREF({context_name}->last_result);\n"
            + f"{context_name}->last_result = callback_result;\n"
            + f"void *callback_value = {pointer};\n"
            + "PyGILState_Release(callback_gil);\n"
            + "return callback_value;\n"
        )

    def _callback_support_code(self, callback):
        """Handle callback support code for the current generation context."""
        metadata = callback.decorators["x2py_callback_abi"]
        context_type, current_name, abort_name = self._callback_context_names(callback)
        signature = self._function_signature(callback)
        signature = signature.replace(f"(*{callback.name})", str(callback.name))
        argument_code = "".join(
            self._callback_argument_code(callback, mapping, index, abort_name)
            for index, mapping in enumerate(metadata["arguments"])
        )
        result_code = self._callback_result_code(callback, metadata["result"], "callback_context", abort_name)
        return (
            f"typedef struct {context_type} {{\n"
            "    PyObject *callable;\n"
            "    unsigned long thread_id;\n"
            f"    struct {context_type} *previous;\n"
            "    PyObject *last_result;\n"
            f"}} {context_type};\n"
            f"static _Thread_local {context_type} *{current_name} = NULL;\n"
            f"static void {abort_name}(const char *message)\n{{\n"
            "    if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, message);\n"
            "    PyErr_PrintEx(0);\n"
            "    abort();\n"
            "}\n"
            f"static {signature}\n{{\n"
            f"    {context_type} *callback_context = {current_name};\n"
            "    if (callback_context == NULL || callback_context->thread_id != PyThread_get_thread_ident()) {\n"
            "        PyGILState_STATE callback_thread_gil = PyGILState_Ensure();\n"
            '        PyErr_SetString(PyExc_RuntimeError, "callback invoked outside its entering Python thread");\n'
            f'        {abort_name}("callback thread violation");\n'
            "        PyGILState_Release(callback_thread_gil);\n"
            "    }\n"
            "    PyGILState_STATE callback_gil = PyGILState_Ensure();\n"
            f"    PyObject *callback_args = PyTuple_New({len(metadata['arguments'])});\n"
            f'    if (callback_args == NULL) {abort_name}("failed to allocate callback arguments");\n'
            + "".join(f"    {line}\n" for line in argument_code.splitlines())
            + "    PyObject *callback_result = PyObject_CallObject(callback_context->callable, callback_args);\n"
            "    Py_DECREF(callback_args);\n"
            f'    if (callback_result == NULL) {abort_name}("Python callback raised an exception");\n'
            + "".join(f"    {line}\n" for line in result_code.splitlines())
            + "}\n"
        )

    def _handle_is_operator(self, Op, expr):
        """
        Get the code to print an `is` or `is not` expression.

        Get the code to print an `is` or `is not` expression. These two operators
        function similarly so this helper function reduces code duplication.
        This function overrides CCodePrinter._handle_is_operator to add the
        handling of `Py_None`.

        Parameters
        ----------
        Op : str
            The C operator representing "is" or "is not".

        expr : Is/IsNot
            The expression being printed.

        Returns
        -------
        str
            The code describing the expression.

        Raises
        ------
        X2pyError : Raised if the comparison is poorly defined.
        """
        if expr.args[1] is Py_None:
            lhs = ObjectAddress(expr.args[0])
            rhs = ObjectAddress(expr.args[1])
            lhs = self._visit(lhs)
            rhs = self._visit(rhs)
            return f"{lhs} {Op} {rhs}"
        python_object_types = (PythonObjectType, PythonClassType, WrapperCustomDataType, NumpyArrayObjectType)
        if all(isinstance(arg.dtype, python_object_types) for arg in expr.args):
            lhs = self._visit(ObjectAddress(expr.args[0]))
            rhs = self._visit(ObjectAddress(expr.args[1]))
            return f"(PyObject *){lhs} {Op} (PyObject *){rhs}"
        return super()._handle_is_operator(Op, expr)

    # --------------------------------------------------------------------
    #                 _visit_ClassName functions
    # --------------------------------------------------------------------
