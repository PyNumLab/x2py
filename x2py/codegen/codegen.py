"""Code generation facade for printing codegen AST modules."""

from __future__ import annotations

import os

from x2py.codegen.models.core import FunctionDef, FunctionOverloadSet, ModuleHeader
from x2py.codegen.printers.codegen import _extension_registry, _header_extension_registry, printer_registry


class Codegen:
    """Coordinate code printing for a generated module or program."""

    def __init__(self, name, ast, scope):
        self._name = name
        self._scope = scope
        self._ast = ast
        self._printer = None
        self._language = None
        self._stmts = {
            "imports": [],
            "body": [],
            "routines": [],
            "classes": [],
            "modules": [],
            "variables": [],
            "overload_sets": [],
        }
        self._collect_statements()
        self._is_program = self.ast.program is not None

    @property
    def name(self):
        return self._name

    @property
    def scope(self):
        return self._scope

    @property
    def imports(self):
        return self._stmts["imports"]

    @property
    def variables(self):
        return self._stmts["variables"]

    @property
    def body(self):
        return self._stmts["body"]

    @property
    def routines(self):
        return self._stmts["routines"]

    @property
    def classes(self):
        return self._stmts["classes"]

    @property
    def overload_sets(self):
        return self._stmts["overload_sets"]

    @property
    def modules(self):
        return self._stmts["modules"]

    @property
    def is_program(self):
        return self._is_program

    @property
    def ast(self):
        return self._ast

    @property
    def language(self):
        return self._language

    def set_printer(self, **settings):
        language = settings.pop("language", "fortran")
        if language not in {"fortran", "c", "c++", "python"}:
            raise ValueError(f"{language} language is not available")
        self._language = language
        self._printer = printer_registry[language](self.name, **settings)

    def get_printer_imports(self):
        return self._printer.get_additional_imports()

    def _collect_statements(self):
        funcs = []
        overload_sets = []
        for item in self.scope.functions.values():
            if isinstance(item, FunctionDef) and not item.is_header:
                funcs.append(item)
            elif isinstance(item, FunctionOverloadSet):
                overload_sets.append(item)

        self._stmts["imports"] = list(self.scope.imports["imports"].values())
        self._stmts["variables"] = list(self.scope.variables.values())
        self._stmts["routines"] = funcs
        self._stmts["classes"] = list(self.scope.classes.values())
        self._stmts["overload_sets"] = overload_sets
        self._stmts["body"] = self.ast

    def doprint(self, **settings):
        if not self._printer:
            self.set_printer(**settings)
        return self._printer.doprint(self.ast)

    def export(self, **settings):
        self.set_printer(**settings)
        ext = _extension_registry[self._language]
        header_ext = _header_extension_registry[self._language]

        filename = self.name
        header_filename = f"{filename}.{header_ext}"
        filename = f"{filename}.{ext}"

        if header_ext is not None:
            code = self._printer.doprint(ModuleHeader(self.ast))
            with open(header_filename, "w", encoding="utf-8") as f:
                for line in code:
                    f.write(line)

        code = self._printer.doprint(self.ast)
        with open(filename, "w", encoding="utf-8") as f:
            for line in code:
                f.write(line)

        prog_filename = None
        if self.is_program and self.language != "python":
            folder = os.path.dirname(filename)
            fname = os.path.basename(filename)
            prog_filename = os.path.join(folder, "prog_" + fname)
            code = self._printer.doprint(self.ast.program)
            with open(prog_filename, "w", encoding="utf-8") as f:
                for line in code:
                    f.write(line)

        return filename, prog_filename
