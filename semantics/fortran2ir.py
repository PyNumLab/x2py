from __future__ import annotations

from .models import *
from fortran_parser.models import *


FORTRAN_TYPE_MAP = {
    ("integer", None): "Int32",
    ("real", None): "Float64",
    ("real", "4"): "Float32",
    ("real", "8"): "Float64",
    ("logical", None): "Bool",
    ("character", None): "String",
}


class FortranToIRConverter:
    """Convert parsed Fortran models into the semantic IR.

    The converter keeps the transformation logic together so callers can use a
    configurable object instead of coordinating several standalone conversion
    functions.  Module-level functions below delegate to a default converter for
    backwards compatibility.
    """

    def __init__(self, type_map: dict[tuple[str, str | None], str] | None = None):
        self.type_map = FORTRAN_TYPE_MAP if type_map is None else type_map

    def first_module(self, parsed):
        """Accept a FortranModule, FortranFile, or legacy signature list in tests."""
        if hasattr(parsed, "procedures") and hasattr(parsed, "derived_types") and hasattr(parsed, "uses"):
            return parsed
        if hasattr(parsed, "modules"):
            if not parsed.modules:
                raise ValueError("Expected at least one Fortran module in parsed file")
            return parsed.modules[0]
        if isinstance(parsed, list):
            module_name = next((getattr(sig, "module", None) for sig in parsed if getattr(sig, "module", None)), None)
            return FortranModule(name=module_name or "", procedures=[sig for sig in parsed if not getattr(sig, "in_interface", False)])
        raise TypeError(f"Unsupported Fortran parse object: {type(parsed)!r}")

    def variable_to_semantic_type(self, var) -> SemanticType:
        kind = str(var.kind).lower() if var.kind is not None else None
        if var.base_type.lower() == "derived":
            if not var.kind:
                raise ValueError(f"Derived type variable '{var.name}' is missing concrete type name")
            semantic_name = str(var.kind)
        else:
            semantic_name = self.type_map.get(
                (var.base_type.lower(), kind),
                "Unknown"
            )

        semantic_type = SemanticType(
            name=semantic_name,
            rank=var.rank,
            dtype=semantic_name,
            shape=list(var.shape),
        )

        if var.rank > 0:
            semantic_type.constraints.append(
                SemanticConstraint(
                    name="Shape",
                    arguments=list(var.shape),
                )
            )
            semantic_type.constraints.append(
                SemanticConstraint(
                    name="FortranContiguous"
                )
            )

        if getattr(var, "is_parameter", False):
            semantic_type.constraints.append(
                SemanticConstraint("Constant")
            )

        return semantic_type

    def argument_to_semantic_argument(self, arg) -> SemanticArgument:
        semantic_type = self.variable_to_semantic_type(arg)

        if arg.allocatable:
            semantic_type.constraints.append(
                SemanticConstraint("Allocatable")
            )

        if arg.pointer:
            semantic_type.constraints.append(
                SemanticConstraint("Pointer")
            )

        intent = getattr(arg, "intent", "in")
        ownership = semantic_type.ownership
        ownership.mutable = str(intent).lower() != "in"

        return SemanticArgument(
            name=arg.name,
            semantic_type=semantic_type,
            intent=intent,
            optional=getattr(arg, "optional", False),
            visibility=getattr(arg, "visibility", "public"),
        )

    def procedure_to_semantic_function(self, proc, visibility: str = "public") -> SemanticFunction:
        semantic_args = [
            self.argument_to_semantic_argument(a)
            for a in proc.arguments
        ]

        return_type = None
        if proc.result:
            return_type = self.variable_to_semantic_type(proc.result)

        return SemanticFunction(
            name=proc.name,
            native_name=proc.name,
            arguments=semantic_args,
            return_type=return_type,
            visibility=visibility,
        )

    def derived_type_to_semantic_class(
        self,
        dtype,
        procedure_lookup: dict[str, SemanticFunction]
    ) -> SemanticClass:
        fields = [
            self.argument_to_semantic_argument(f)
            for f in dtype.fields
        ]

        methods = []
        for method_name in dtype.methods:
            if method_name in procedure_lookup:
                proc = procedure_lookup[method_name]
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

        bases = []
        if dtype.extends:
            if isinstance(dtype.extends, str):
                bases.append(dtype.extends)
            else:
                bases.append(dtype.extends.name)

        return SemanticClass(
            name=dtype.name,
            native_name=dtype.name,
            fields=fields,
            methods=methods,
            base_classes=bases,
            visibility=getattr(dtype, "visibility", "public"),
        )

    def _symbol_visibility(self, module, symbol_name: str) -> str:
        lname = symbol_name.lower()
        public_set = {s.lower() for s in getattr(module, "public_symbols", [])}
        private_set = {s.lower() for s in getattr(module, "private_symbols", [])}
        if lname in private_set:
            return "private"
        if lname in public_set:
            return "public"
        return getattr(module, "default_visibility", "public")

    def module_to_semantic_module(self, module) -> SemanticModule:
        module = self.first_module(module)

        semantic_functions = []
        for proc in module.procedures:
            semantic_functions.append(
                self.procedure_to_semantic_function(
                    proc,
                    visibility=self._symbol_visibility(module, proc.name),
                )
            )

        procedure_lookup = {
            f.name: f
            for f in semantic_functions
        }

        semantic_classes = [
            self.derived_type_to_semantic_class(dtype, procedure_lookup)
            for dtype in module.derived_types
        ]
        semantic_variables = [
            self.argument_to_semantic_argument(var)
            for var in getattr(module, "variables", [])
        ]

        for semantic_cls in semantic_classes:
            semantic_cls.visibility = self._symbol_visibility(module, semantic_cls.name)

        return SemanticModule(
            name=module.name,
            functions=semantic_functions,
            classes=semantic_classes,
            variables=semantic_variables,
            imports=list(module.uses.keys()),
        )


_DEFAULT_CONVERTER = FortranToIRConverter()


def fortran_module_to_semantic_module(module) -> SemanticModule:
    return _DEFAULT_CONVERTER.module_to_semantic_module(module)


if __name__ == "__main__":
    pass
