"""Source printers for isolated scalar backend nodes."""

from __future__ import annotations

from x2py.wrapper_codegen.nodes import (
    ApiReference,
    CDeclaration,
    CExpressionStatement,
    CFunction,
    CFunctionPrototype,
    CHeader,
    CInclude,
    CModule,
    CParameter,
    CReturn,
    FortranAssignment,
    FortranCall,
    FortranDeclaration,
    FortranFunction,
    FortranModule,
    FortranParameter,
    FortranUse,
)
from x2py.wrapper_codegen.visitor import ClassVisitor


class CSourcePrinter(ClassVisitor):
    """Print isolated C source and header nodes."""

    def doprint(self, node: object) -> str:
        """Render one isolated C backend node."""
        return self.visit(node)

    def _visit_CModule(self, node: CModule) -> str:
        """Render a complete C source module."""
        parts = [self.visit(include) for include in node.includes]
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

    def _visit_CFunction(self, node: CFunction) -> str:
        """Render one C function definition."""
        prefix = f"{node.storage} " if node.storage else ""
        body = "\n".join(f"    {self.visit(statement)}" for statement in node.body)
        return f"{prefix}{self._signature(node.return_type, node.name, node.parameters)} {{\n{body}\n}}"

    def _visit_CFunctionPrototype(self, node: CFunctionPrototype) -> str:
        """Render one C function prototype."""
        return f"{self._signature(node.return_type, node.name, node.parameters)};"

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

    def _visit_CReturn(self, node: CReturn) -> str:
        """Render one C return statement."""
        if node.expression is None:
            return "return;"
        return f"return {node.expression.text};"

    def _visit_ApiReference(self, node: ApiReference) -> str:
        """Render one C API symbol reference."""
        return node.name

    def _signature(self, return_type: str, name: str, parameters: tuple[CParameter, ...]) -> str:
        """Render a C function signature."""
        rendered = ", ".join(self.visit(parameter) for parameter in parameters) or "void"
        return f"{return_type} {name}({rendered})"


class FortranSourcePrinter(ClassVisitor):
    """Print isolated Fortran source nodes."""

    def doprint(self, node: object) -> str:
        """Render one isolated Fortran backend node."""
        return self.visit(node)

    def _visit_FortranModule(self, node: FortranModule) -> str:
        """Render a complete Fortran module."""
        lines = [f"module {node.name}"]
        lines.extend(f"  {self.visit(use)}" for use in node.uses)
        lines.extend(["  implicit none", "contains"])
        lines.extend(self._indented(self.visit(procedure)) for procedure in node.procedures)
        lines.append(f"end module {node.name}")
        return "\n".join(lines)

    def _visit_FortranUse(self, node: FortranUse) -> str:
        """Render one Fortran use statement."""
        if node.only:
            return f"use {node.module}, only: {', '.join(node.only)}"
        return f"use {node.module}"

    def _visit_FortranFunction(self, node: FortranFunction) -> str:
        """Render one Fortran function."""
        signature = self._function_signature(node)
        lines = [signature]
        lines.extend(f"  {self.visit(parameter)}" for parameter in node.parameters)
        if node.result_name is not None and node.result_type is not None:
            lines.append(f"  {node.result_type} :: {node.result_name}")
        lines.extend(f"  {self.visit(declaration)}" for declaration in node.declarations)
        lines.extend(f"  {self.visit(statement)}" for statement in node.body)
        lines.append(f"end function {node.name}")
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

    def _visit_FortranCall(self, node: FortranCall) -> str:
        """Render one Fortran call statement."""
        return f"call {node.function_name}({', '.join(argument.text for argument in node.arguments)})"

    def _function_signature(self, node: FortranFunction) -> str:
        """Render a Fortran function signature."""
        args = ", ".join(parameter.name for parameter in node.parameters)
        suffix = f" result({node.result_name})" if node.result_name is not None else ""
        bind = f' bind(c, name="{node.bind_name}")' if node.bind_name is not None else ""
        return f"function {node.name}({args}){suffix}{bind}"

    def _declaration(self, type_name: str, name: str, attributes: tuple[str, ...]) -> str:
        """Render a Fortran declaration."""
        suffix = f", {', '.join(attributes)}" if attributes else ""
        return f"{type_name}{suffix} :: {name}"

    def _indented(self, text: str) -> str:
        """Indent a rendered procedure inside a module body."""
        return "\n".join(f"  {line}" for line in text.splitlines())
