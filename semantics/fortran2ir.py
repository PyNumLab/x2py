from __future__ import annotations

from pathlib import Path

from fortran_parser.models import (
    FortranArgument,
    FortranDerivedType,
    FortranFile,
    FortranModule,
    FortranProcedureSignature,
    FortranVariable,
)

from .models import (
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticMethod,
    SemanticModule,
    SemanticType,
)


FORTRAN_TYPE_MAP = {
    ("integer", None): "Int32",
    ("real", None): "Float64",
    ("real", "4"): "Float32",
    ("real", "8"): "Float64",
    ("logical", None): "Bool",
    ("character", None): "String",
}


class FortranToIRConverter:
    """Convert parsed Fortran models into semantic IR models.

    The converter is intentionally a small visitor: public compatibility methods
    delegate to explicit `visit_*` methods, and each visitor method converts one
    parser model type into the corresponding semantic model type.
    """

    def __init__(self, type_map: dict[tuple[str, str | None], str] | None = None):
        self.type_map = FORTRAN_TYPE_MAP if type_map is None else type_map

    def visit(self, node, **context):
        """Dispatch one parsed Fortran model to the matching conversion method."""
        if isinstance(node, FortranFile):
            return self.visit_file(node)
        if isinstance(node, FortranModule):
            return self.visit_module(node)
        if isinstance(node, FortranProcedureSignature):
            return self.visit_procedure(node, visibility=context.get("visibility", "public"))
        if isinstance(node, FortranDerivedType):
            return self.visit_derived_type(
                node,
                procedure_lookup=context.get("procedure_lookup", {}),
            )
        if isinstance(node, FortranArgument):
            return self.visit_argument(node)
        if isinstance(node, FortranVariable):
            return self.visit_variable(node)
        raise TypeError(f"Unsupported Fortran parse object: {type(node)!r}")

    def first_module(self, parsed):
        """Accept a FortranModule, FortranFile, or legacy signature list in tests."""
        if isinstance(parsed, FortranModule):
            return parsed
        if isinstance(parsed, FortranFile):
            if not parsed.modules:
                raise ValueError("Expected at least one Fortran module in parsed file")
            return parsed.modules[0]
        if isinstance(parsed, list):
            module_name = next((getattr(sig, "module", None) for sig in parsed if getattr(sig, "module", None)), None)
            procedures = [sig for sig in parsed if not getattr(sig, "in_interface", False)]
            return FortranModule(name=module_name or "", procedures=procedures)
        raise TypeError(f"Unsupported Fortran parse object: {type(parsed)!r}")

    def visit_file(self, parsed_file: FortranFile) -> SemanticModule:
        return self.visit_module(self.first_module(parsed_file))

    def visit_variable(self, var: FortranVariable) -> SemanticType:
        semantic_name = self._semantic_type_name(var)
        semantic_type = SemanticType(
            name=semantic_name,
            rank=var.rank,
            dtype=semantic_name,
            shape=list(var.shape),
        )
        self._add_shape_constraints(semantic_type)
        self._add_variable_constraints(semantic_type, var)
        return semantic_type

    def visit_argument(
        self,
        arg: FortranArgument | FortranVariable,
        *,
        intent: str | None = None,
    ) -> SemanticArgument:
        semantic_type = self.visit_variable(arg)
        self._add_argument_constraints(semantic_type, arg)
        resolved_intent = intent if intent is not None else getattr(arg, "intent", "in")
        resolved_intent = str(resolved_intent).lower().replace(" ", "")
        if resolved_intent == "unknown":
            resolved_intent = "inout"
        self._apply_argument_ownership(semantic_type, resolved_intent)

        return SemanticArgument(
            name=arg.name,
            semantic_type=semantic_type,
            intent=resolved_intent,
            optional=getattr(arg, "optional", False),
            visibility=getattr(arg, "visibility", "public"),
        )

    def visit_procedure(
        self,
        proc: FortranProcedureSignature,
        visibility: str = "public",
    ) -> SemanticFunction:
        return SemanticFunction(
            name=proc.name,
            native_name=proc.name,
            arguments=[self.visit_argument(arg) for arg in self._projected_procedure_arguments(proc)],
            return_type=self.visit_variable(proc.result) if proc.result else None,
            visibility=visibility,
        )

    def visit_derived_type(
        self,
        dtype: FortranDerivedType,
        procedure_lookup: dict[str, SemanticFunction] | None = None,
    ) -> SemanticClass:
        lookup = procedure_lookup or {}
        return SemanticClass(
            name=dtype.name,
            native_name=dtype.name,
            fields=[self.visit_argument(field, intent="in") for field in dtype.fields],
            methods=self._bound_methods(dtype, lookup),
            base_classes=self._base_classes(dtype),
            visibility=getattr(dtype, "visibility", "public"),
        )

    def visit_module(self, module: FortranModule) -> SemanticModule:
        semantic_functions = [
            self.visit_procedure(
                proc,
                visibility=self._symbol_visibility(module, proc.name),
            )
            for proc in module.procedures
        ]
        procedure_lookup = {func.name: func for func in semantic_functions}

        semantic_classes = [
            self.visit_derived_type(dtype, procedure_lookup=procedure_lookup)
            for dtype in module.derived_types
        ]
        for semantic_cls in semantic_classes:
            semantic_cls.visibility = self._symbol_visibility(module, semantic_cls.name)

        return SemanticModule(
            name=module.name,
            functions=semantic_functions,
            classes=semantic_classes,
            variables=[self.visit_argument(var, intent="in") for var in getattr(module, "variables", [])],
            imports=list(module.uses.keys()),
        )

    def visit_file_modules(
        self,
        parsed_file: FortranFile,
        *,
        standalone_module_name: str | None = None,
    ) -> list[SemanticModule]:
        modules = [self.visit_module(module) for module in parsed_file.modules]
        if parsed_file.procedures:
            modules.append(
                self.procedures_to_semantic_module(
                    parsed_file.procedures,
                    name=standalone_module_name or self._standalone_module_name(parsed_file),
                )
            )
        return modules

    def procedures_to_semantic_module(
        self,
        procedures: list[FortranProcedureSignature],
        *,
        name: str,
    ) -> SemanticModule:
        return SemanticModule(
            name=name,
            functions=[self.visit_procedure(proc) for proc in procedures],
        )

    def variable_to_semantic_type(self, var) -> SemanticType:
        return self.visit_variable(var)

    def argument_to_semantic_argument(self, arg) -> SemanticArgument:
        return self.visit_argument(arg)

    def procedure_to_semantic_function(self, proc, visibility: str = "public") -> SemanticFunction:
        return self.visit_procedure(proc, visibility=visibility)

    def derived_type_to_semantic_class(
        self,
        dtype,
        procedure_lookup: dict[str, SemanticFunction],
    ) -> SemanticClass:
        return self.visit_derived_type(dtype, procedure_lookup=procedure_lookup)

    def module_to_semantic_module(self, module) -> SemanticModule:
        return self.visit_module(self.first_module(module))

    def file_to_semantic_modules(
        self,
        parsed_file: FortranFile,
        *,
        standalone_module_name: str | None = None,
    ) -> list[SemanticModule]:
        return self.visit_file_modules(
            parsed_file,
            standalone_module_name=standalone_module_name,
        )

    def _semantic_type_name(self, var: FortranVariable) -> str:
        if var.base_type.lower() == "derived":
            if not var.kind:
                raise ValueError(f"Derived type variable '{var.name}' is missing concrete type name")
            return str(var.kind)

        kind = str(var.kind).lower() if var.kind is not None else None
        return self.type_map.get((var.base_type.lower(), kind), "Unknown")

    @staticmethod
    def _add_shape_constraints(semantic_type: SemanticType) -> None:
        if semantic_type.rank <= 0:
            return
        semantic_type.constraints.append(
            SemanticConstraint(
                name="Shape",
                arguments=list(semantic_type.shape),
            )
        )
        semantic_type.constraints.append(SemanticConstraint(name="FortranContiguous"))

    @staticmethod
    def _add_variable_constraints(semantic_type: SemanticType, var: FortranVariable) -> None:
        if getattr(var, "is_parameter", False):
            semantic_type.constraints.append(SemanticConstraint("Constant"))

    @staticmethod
    def _add_argument_constraints(semantic_type: SemanticType, arg: FortranArgument | FortranVariable) -> None:
        if getattr(arg, "allocatable", False):
            semantic_type.constraints.append(SemanticConstraint("Allocatable"))
        if getattr(arg, "pointer", False):
            semantic_type.constraints.append(SemanticConstraint("Pointer"))

    @staticmethod
    def _apply_argument_ownership(semantic_type: SemanticType, intent: str) -> None:
        semantic_type.ownership.mutable = str(intent).lower() != "in"

    def _bound_methods(
        self,
        dtype: FortranDerivedType,
        procedure_lookup: dict[str, SemanticFunction],
    ) -> list[SemanticMethod]:
        methods: list[SemanticMethod] = []
        for method_name in dtype.methods:
            proc = procedure_lookup.get(method_name)
            if proc is None:
                continue
            methods.append(
                SemanticMethod(
                    name=proc.name,
                    native_name=proc.native_name,
                    arguments=proc.arguments,
                    return_type=proc.return_type,
                    contracts=proc.contracts,
                    visibility=proc.visibility,
                )
            )
        return methods

    @staticmethod
    def _projected_procedure_arguments(proc: FortranProcedureSignature) -> list[FortranArgument]:
        args = list(proc.arguments)
        return [
            *[
                arg
                for arg in args
                if getattr(arg, "intent", "in") != "out" and not getattr(arg, "optional", False)
            ],
            *[
                arg
                for arg in args
                if getattr(arg, "intent", "in") != "out" and getattr(arg, "optional", False)
            ],
            *[arg for arg in args if getattr(arg, "intent", "in") == "out"],
        ]

    @staticmethod
    def _base_classes(dtype: FortranDerivedType) -> list[str]:
        if not dtype.extends:
            return []
        if isinstance(dtype.extends, str):
            return [dtype.extends]
        return [dtype.extends.name]

    @staticmethod
    def _standalone_module_name(parsed_file: FortranFile) -> str:
        if parsed_file.filename:
            return Path(parsed_file.filename).stem
        return "standalone"

    @staticmethod
    def _symbol_visibility(module: FortranModule, symbol_name: str) -> str:
        lname = symbol_name.lower()
        public_set = {s.lower() for s in getattr(module, "public_symbols", [])}
        private_set = {s.lower() for s in getattr(module, "private_symbols", [])}
        if lname in private_set:
            return "private"
        if lname in public_set:
            return "public"
        return getattr(module, "default_visibility", "public")


_DEFAULT_CONVERTER = FortranToIRConverter()


def fortran_module_to_semantic_module(module) -> SemanticModule:
    return _DEFAULT_CONVERTER.module_to_semantic_module(module)


def fortran_file_to_semantic_modules(
    parsed_file: FortranFile,
    *,
    standalone_module_name: str | None = None,
) -> list[SemanticModule]:
    return _DEFAULT_CONVERTER.file_to_semantic_modules(
        parsed_file,
        standalone_module_name=standalone_module_name,
    )


if __name__ == "__main__":
    pass
