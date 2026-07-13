"""Source printers for direct wrapper-plan backend nodes."""

from __future__ import annotations

from x2py.wrapper_codegen.nodes import (
    CAllowThreadsBegin,
    CAllowThreadsEnd,
    CDeclaration,
    CExpressionStatement,
    CFunction,
    CFunctionPrototype,
    CHeader,
    CIf,
    CInclude,
    CMacroDefinition,
    CMethodDefEntry,
    CMethodDefTable,
    CModuleDef,
    CModule,
    CModulePropertyEntry,
    CModulePropertySupport,
    CParameter,
    CReturn,
    FortranAssignment,
    FortranCall,
    FortranDeclaration,
    FortranFunction,
    FortranIf,
    FortranInterface,
    FortranInterfaceProcedure,
    FortranModule,
    FortranParameter,
    FortranPointerAssignment,
    FortranUse,
)
from x2py.stage_values import StageRecord
from x2py.wrapper_codegen.visitor import ClassVisitor


class CSourcePrinter(ClassVisitor):
    """Print isolated C source and header nodes."""

    def doprint(self, node: object) -> str:
        """Render one isolated C backend node."""
        if isinstance(node, StageRecord):
            node.freeze()
        return self.visit(node)

    def _visit_CModule(self, node: CModule) -> str:
        """Render a complete C source module."""
        parts = [self.visit(define) for define in node.defines]
        parts.extend(self.visit(include) for include in node.includes)
        parts.extend(self.visit(declaration) for declaration in node.declarations)
        parts.extend(self.visit(function) for function in node.functions)
        return "\n\n".join(part for part in parts if part)

    def _visit_CHeader(self, node: CHeader) -> str:
        """Render a complete C header module."""
        lines = [f"#ifndef {node.guard}", f"#define {node.guard}"]
        lines.extend(self.visit(include) for include in node.includes)
        lines.extend(self.visit(prototype) for prototype in node.prototypes)
        lines.append(f"#endif /* {node.guard} */")
        return "\n".join(lines)

    def _visit_CInclude(self, node: CInclude) -> str:
        """Render one C include directive."""
        if node.system:
            return f"#include <{node.header}>"
        return f'#include "{node.header}"'

    def _visit_CMacroDefinition(self, node: CMacroDefinition) -> str:
        """Render one C preprocessor macro definition."""
        if node.value is None:
            return f"#define {node.name}"
        return f"#define {node.name} {node.value}"

    def _visit_CFunction(self, node: CFunction) -> str:
        """Render one C function definition."""
        prefix = f"{node.storage} " if node.storage else ""
        body = "\n".join(self._indented(self.visit(statement)) for statement in node.body)
        return f"{prefix}{self._signature(node.return_type, node.name, node.parameters)} {{\n{body}\n}}"

    def _visit_CFunctionPrototype(self, node: CFunctionPrototype) -> str:
        """Render one C function prototype."""
        prefix = f"{node.storage} " if node.storage else ""
        return f"{prefix}{self._signature(node.return_type, node.name, node.parameters)};"

    def _visit_CMethodDefTable(self, node: CMethodDefTable) -> str:
        """Render one CPython method table."""
        lines = [f"static PyMethodDef {node.name}[] = {{"]
        lines.extend(f"    {self.visit(entry)}," for entry in node.entries)
        lines.extend(("    {NULL, NULL, 0, NULL}", "};"))
        return "\n".join(lines)

    def _visit_CMethodDefEntry(self, node: CMethodDefEntry) -> str:
        """Render one CPython method table entry."""
        return (
            f"{{{self._c_string_literal(node.python_name)}, "
            f"(PyCFunction){node.wrapper_name}, {node.flags}, {self._c_string_literal(node.docstring)}}}"
        )

    def _visit_CModuleDef(self, node: CModuleDef) -> str:
        """Render one CPython module definition."""
        return "\n".join(
            (
                f"static struct PyModuleDef {node.name} = {{",
                "    PyModuleDef_HEAD_INIT,",
                f"    {self._c_string_literal(node.module_name)},",
                f"    {self._c_string_literal(node.docstring)},",
                f"    {node.state_size},",
                f"    {node.methods_name},",
                "};",
            )
        )

    def _visit_CModulePropertySupport(self, node: CModulePropertySupport) -> str:
        """Render module get/set routing through a generated heap subtype."""
        return "\n\n".join(
            (
                self._module_getattro_source(node),
                self._module_setattro_source(node),
                self._module_property_type_source(node),
            )
        )

    def _module_getattro_source(self, node: CModulePropertySupport) -> str:
        lines = [f"static PyObject *{node.name}_getattro(PyObject *self, PyObject *name)", "{"]
        lines.append("    if (PyUnicode_Check(name)) {")
        for entry in node.entries:
            lines.extend(self._module_getter_entry_source(entry))
        lines.extend(("    }", "    return PyModule_Type.tp_getattro(self, name);", "}"))
        return "\n".join(lines)

    def _module_getter_entry_source(self, node: CModulePropertyEntry) -> tuple[str, ...]:
        name = self._c_string_literal(node.python_name)
        return (
            "        {",
            f"            int comparison = PyUnicode_CompareWithASCIIString(name, {name});",
            "            if (comparison == -1 && PyErr_Occurred()) return NULL;",
            f"            if (comparison == 0) return {node.getter_name}();",
            "        }",
        )

    def _module_setattro_source(self, node: CModulePropertySupport) -> str:
        lines = [f"static int {node.name}_setattro(PyObject *self, PyObject *name, PyObject *value)", "{"]
        lines.append("    if (PyUnicode_Check(name)) {")
        for entry in node.entries:
            lines.extend(self._module_setter_entry_source(entry))
        lines.extend(("    }", "    return PyModule_Type.tp_setattro(self, name, value);", "}"))
        return "\n".join(lines)

    def _module_setter_entry_source(self, node: CModulePropertyEntry) -> tuple[str, ...]:
        name = self._c_string_literal(node.python_name)
        lines = [
            "        {",
            f"            int comparison = PyUnicode_CompareWithASCIIString(name, {name});",
            "            if (comparison == -1 && PyErr_Occurred()) return -1;",
            "            if (comparison == 0) {",
        ]
        if node.reject_replacement:
            lines.extend(
                (
                    f'                PyErr_SetString(PyExc_AttributeError, "module variable {node.python_name} is read-only");',
                    "                return -1;",
                )
            )
        else:
            lines.extend(
                (
                    "                if (value == NULL) {",
                    f'                    PyErr_SetString(PyExc_AttributeError, "module variable {node.python_name} cannot be deleted");',
                    "                    return -1;",
                    "                }",
                    f"                return {node.setter_name}(value);",
                )
            )
        lines.extend(("            }", "        }"))
        return tuple(lines)

    def _module_property_type_source(self, node: CModulePropertySupport) -> str:
        return "\n".join(
            (
                f"static PyType_Slot {node.name}_slots[] = {{",
                f"    {{Py_tp_getattro, (void *){node.name}_getattro}},",
                f"    {{Py_tp_setattro, (void *){node.name}_setattro}},",
                "    {0, NULL}",
                "};",
                f"static PyType_Spec {node.name}_spec = {{",
                f"    {self._c_string_literal(f'{node.module_name}.__x2py_module_type')},",
                "    0,",
                "    0,",
                "    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,",
                f"    {node.name}_slots",
                "};",
                f"static int {node.name}(PyObject *module)",
                "{",
                "    PyObject *bases = PyTuple_Pack(1, (PyObject *)&PyModule_Type);",
                "    if (bases == NULL) return -1;",
                f"    PyObject *module_type = PyType_FromSpecWithBases(&{node.name}_spec, bases);",
                "    Py_DECREF(bases);",
                "    if (module_type == NULL) return -1;",
                '    int status = PyObject_SetAttrString(module, "__class__", module_type);',
                "    Py_DECREF(module_type);",
                "    return status;",
                "}",
            )
        )

    def _visit_CParameter(self, node: CParameter) -> str:
        """Render one C parameter."""
        return f"{node.type_name} {node.name}"

    def _visit_CDeclaration(self, node: CDeclaration) -> str:
        """Render one C declaration."""
        if node.initializer is None:
            return f"{node.type_name} {node.name};"
        return f"{node.type_name} {node.name} = {node.initializer.text};"

    def _visit_CExpressionStatement(self, node: CExpressionStatement) -> str:
        """Render one C expression statement."""
        return f"{node.expression.text};"

    def _visit_CAllowThreadsBegin(self, _node: CAllowThreadsBegin) -> str:
        """Render the opening CPython thread-release macro without a semicolon."""
        return "Py_BEGIN_ALLOW_THREADS"

    def _visit_CAllowThreadsEnd(self, _node: CAllowThreadsEnd) -> str:
        """Render the closing CPython thread-release macro without a semicolon."""
        return "Py_END_ALLOW_THREADS"

    def _visit_CIf(self, node: CIf) -> str:
        """Render one C conditional statement."""
        lines = [f"if ({node.condition.text}) {{"]
        lines.extend(self._indented(self.visit(statement)) for statement in node.body)
        if node.else_body:
            lines.append("} else {")
            lines.extend(self._indented(self.visit(statement)) for statement in node.else_body)
        lines.append("}")
        return "\n".join(lines)

    def _visit_CReturn(self, node: CReturn) -> str:
        """Render one C return statement."""
        if node.expression is None:
            return "return;"
        return f"return {node.expression.text};"

    def _signature(self, return_type: str, name: str, parameters: tuple[CParameter, ...]) -> str:
        """Render a C function signature."""
        rendered = ", ".join(self.visit(parameter) for parameter in parameters) or "void"
        return f"{return_type} {name}({rendered})"

    def _c_string_literal(self, value: str) -> str:
        """Render a minimal escaped C string literal."""
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'

    def _indented(self, text: str) -> str:
        return "\n".join(f"    {line}" for line in text.splitlines())


class FortranSourcePrinter(ClassVisitor):
    """Print isolated Fortran source nodes."""

    def doprint(self, node: object) -> str:
        """Render one isolated Fortran backend node."""
        if isinstance(node, StageRecord):
            node.freeze()
        return self.visit(node)

    def _visit_FortranModule(self, node: FortranModule) -> str:
        """Render a complete Fortran module."""
        lines = [f"module {node.name}"]
        lines.extend(self._indented(self.visit(use)) for use in node.uses)
        lines.append("  implicit none")
        lines.extend(self._indented(self.visit(interface)) for interface in node.interfaces)
        lines.append("contains")
        lines.extend(self._indented(self.visit(procedure)) for procedure in node.procedures)
        lines.append(f"end module {node.name}")
        return "\n".join(lines)

    def _visit_FortranUse(self, node: FortranUse) -> str:
        """Render one Fortran use statement."""
        if node.only:
            rendered = f"use {node.module}, only: {', '.join(node.only)}"
            if len(rendered) <= 100:
                return rendered
            lines = [f"use {node.module}, only: &"]
            for index, name in enumerate(node.only):
                continuation = ", &" if index < len(node.only) - 1 else ""
                lines.append(f"  {name}{continuation}")
            return "\n".join(lines)
        return f"use {node.module}"

    def _visit_FortranFunction(self, node: FortranFunction) -> str:
        """Render one Fortran function."""
        signature = self._function_signature(node)
        lines = [signature]
        lines.extend(self._indented(self.visit(parameter)) for parameter in node.parameters)
        if node.result_name is not None and node.result_type is not None:
            lines.append(self._indented(f"{node.result_type} :: {node.result_name}"))
        lines.extend(self._indented(self.visit(declaration)) for declaration in node.declarations)
        lines.extend(self._indented(self.visit(statement)) for statement in node.body)
        lines.append(f"end {'subroutine' if node.is_subroutine else 'function'} {node.name}")
        return "\n".join(lines)

    def _visit_FortranParameter(self, node: FortranParameter) -> str:
        """Render one Fortran parameter declaration."""
        return self._declaration(node.type_name, node.name, node.attributes)

    def _visit_FortranDeclaration(self, node: FortranDeclaration) -> str:
        """Render one Fortran declaration."""
        return self._declaration(node.type_name, node.name, node.attributes)

    def _visit_FortranAssignment(self, node: FortranAssignment) -> str:
        """Render one Fortran assignment."""
        return f"{node.target} = {node.expression.text}"

    def _visit_FortranPointerAssignment(self, node: FortranPointerAssignment) -> str:
        """Render one Fortran pointer association."""
        return f"{node.target} => {node.expression.text}"

    def _visit_FortranCall(self, node: FortranCall) -> str:
        """Render one Fortran call statement."""
        return f"call {node.function_name}({', '.join(argument.text for argument in node.arguments)})"

    def _visit_FortranIf(self, node: FortranIf) -> str:
        """Render one Fortran conditional statement."""
        lines = [f"if ({node.condition.text}) then"]
        lines.extend(self._indented(self.visit(statement)) for statement in node.body)
        if node.else_body:
            lines.append("else")
            lines.extend(self._indented(self.visit(statement)) for statement in node.else_body)
        lines.append("end if")
        return "\n".join(lines)

    def _visit_FortranInterface(self, node: FortranInterface) -> str:
        """Render one explicit interface block."""
        lines = ["interface"]
        lines.extend(self._indented(self.visit(procedure)) for procedure in node.procedures)
        lines.append("end interface")
        return "\n".join(lines)

    def _visit_FortranInterfaceProcedure(self, node: FortranInterfaceProcedure) -> str:
        """Render one native procedure declaration inside an interface."""
        arguments = ", ".join(parameter.name for parameter in node.parameters)
        kind = "subroutine" if node.is_subroutine else "function"
        suffix = f" result({node.result_name})" if node.result_name is not None else ""
        binding = f' bind(c, name="{node.bind_name}")' if node.bind_name is not None else ""
        lines = [f"{kind} {node.name}({arguments}){binding}{suffix}"]
        if node.imports:
            lines.append(self._indented(f"import :: {', '.join(node.imports)}"))
        lines.extend(self._indented(self.visit(parameter)) for parameter in node.parameters)
        if node.result_name is not None and node.result_type is not None:
            lines.append(self._indented(f"{node.result_type} :: {node.result_name}"))
        lines.append(f"end {kind} {node.name}")
        return "\n".join(lines)

    def _function_signature(self, node: FortranFunction) -> str:
        """Render a Fortran function signature."""
        args = ", ".join(parameter.name for parameter in node.parameters)
        suffix = f" result({node.result_name})" if node.result_name is not None else ""
        bind = f' bind(c, name="{node.bind_name}")' if node.bind_name is not None else ""
        kind = "subroutine" if node.is_subroutine else "function"
        return f"{kind} {node.name}({args}){suffix}{bind}"

    def _declaration(self, type_name: str, name: str, attributes: tuple[str, ...]) -> str:
        """Render a Fortran declaration."""
        suffix = f", {', '.join(attributes)}" if attributes else ""
        return f"{type_name}{suffix} :: {name}"

    def _indented(self, text: str) -> str:
        """Indent a rendered procedure inside a module body."""
        return "\n".join(f"  {line}" for line in text.splitlines())
