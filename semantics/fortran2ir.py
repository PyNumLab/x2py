from __future__ import annotations

import re
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
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticType,
    ProjectionMapping,
)


FORTRAN_TYPE_MAP = {
    ("integer", None): "Int32",
    ("integer", "1"): "Int8",
    ("integer", "2"): "Int16",
    ("integer", "4"): "Int32",
    ("integer", "8"): "Int64",
    ("integer", "int8"): "Int8",
    ("integer", "int16"): "Int16",
    ("integer", "int32"): "Int32",
    ("integer", "int64"): "Int64",
    ("integer", "c_signed_char"): "Int8",
    ("integer", "c_short"): "Int16",
    ("integer", "c_int"): "Int32",
    ("integer", "c_long_long"): "Int64",
    ("integer", "c_int8_t"): "Int8",
    ("integer", "c_int16_t"): "Int16",
    ("integer", "c_int32_t"): "Int32",
    ("integer", "c_int64_t"): "Int64",
    ("real", None): "Float64",
    ("real", "4"): "Float32",
    ("real", "8"): "Float64",
    ("real", "16"): "Float128",
    ("real", "real32"): "Float32",
    ("real", "real64"): "Float64",
    ("real", "real128"): "Float128",
    ("real", "c_float"): "Float32",
    ("real", "c_double"): "Float64",
    ("complex", None): "Complex128",
    ("complex", "4"): "Complex64",
    ("complex", "8"): "Complex128",
    ("complex", "16"): "Complex256",
    ("complex", "real32"): "Complex64",
    ("complex", "real64"): "Complex128",
    ("complex", "real128"): "Complex256",
    ("complex", "c_float_complex"): "Complex64",
    ("complex", "c_double_complex"): "Complex128",
    ("logical", None): "Bool",
    ("logical", "c_bool"): "Bool",
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
        arguments = [self.visit_argument(arg) for arg in self._projected_procedure_arguments(proc)]
        return SemanticFunction(
            name=proc.name,
            native_name=proc.name,
            arguments=arguments,
            return_type=self.visit_variable(proc.result) if proc.result else None,
            projection=self._procedure_projection(proc, arguments),
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
            imports=self._module_imports(module),
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

    @staticmethod
    def _module_imports(module: FortranModule) -> list[str | SemanticImport]:
        imports: list[str | SemanticImport] = []
        for module_name, mappings in module.uses.items():
            if not mappings:
                imports.append(module_name)
            else:
                imports.append(
                    SemanticImport(
                        module=module_name,
                        items=[
                            SemanticImportItem(source=item.source, target=item.target)
                            for item in mappings
                        ],
                    )
                )
        return imports

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
        base_type = var.base_type.lower()
        if base_type == "unknown":
            raise ValueError(f"Unknown Fortran datatype for variable '{var.name}'")

        if base_type == "derived":
            if not var.kind:
                raise ValueError(f"Derived type variable '{var.name}' is missing concrete type name")
            return str(var.kind)
        if base_type == "procedure":
            return "Procedure"

        kind = self._semantic_kind_key(var)
        semantic_type = self.type_map.get((base_type, kind))
        if semantic_type is None:
            type_text = base_type if kind is None else f"{base_type}(kind={kind})"
            raise ValueError(f"Unsupported Fortran semantic type for variable '{var.name}': {type_text}")
        return semantic_type

    @staticmethod
    def _semantic_kind_key(var: FortranVariable) -> str | None:
        if not var.kind:
            return None

        base_type = var.base_type.lower()
        kind = str(var.kind).strip().lower()
        if base_type == "character":
            return None
        if base_type == "logical":
            return "c_bool" if kind == "c_bool" else None
        literal_kind = FortranToIRConverter._literal_kind_key(kind)
        if literal_kind is not None:
            return literal_kind
        return kind

    @staticmethod
    def _literal_kind_key(kind: str) -> str | None:
        match = re.fullmatch(r"kind\(\s*[-+]?\d+(?:\.\d*)?([edq])[-+]?\d*\s*\)", kind)
        if match is None:
            return None
        exponent_marker = match.group(1)
        if exponent_marker == "e":
            return "4"
        if exponent_marker == "d":
            return "8"
        if exponent_marker == "q":
            return "16"
        return None

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
        semantic_type.constraints.append(SemanticConstraint(name="ORDER_F"))

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
    def _procedure_projection(
        proc: FortranProcedureSignature,
        arguments: list[SemanticArgument],
    ) -> list[ProjectionMapping]:
        by_name = {arg.name: arg for arg in arguments}
        call_positions = {
            arg.name: index
            for index, arg in enumerate(arg for arg in arguments if getattr(arg, "intent", "in") != "out")
        }
        result_offset = 1 if proc.result is not None else 0
        result_positions = {
            arg.name: result_offset + index
            for index, arg in enumerate(arg for arg in arguments if getattr(arg, "intent", "in") in {"out", "inout"})
        }

        projection: list[ProjectionMapping] = []
        for native_position, native_arg in enumerate(proc.arguments):
            arg = by_name[native_arg.name]
            intent = getattr(arg, "intent", "in")
            projection.append(
                ProjectionMapping(
                    python_name=arg.name if intent != "out" else None,
                    native_name=native_arg.name,
                    native_position=native_position,
                    python_position=call_positions.get(arg.name),
                    result_position=result_positions.get(arg.name),
                    intent=intent,
                )
            )
        return projection

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
