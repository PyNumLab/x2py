from __future__ import annotations

import ast
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
import re
from pathlib import Path

from fortran_parser.models import (
    FortranArgument,
    FortranBlockData,
    FortranDerivedType,
    FortranFile,
    FortranModule,
    FortranProject,
    FortranProgram,
    FortranProcedureSignature,
    FortranSubmodule,
    FortranUseMapping,
    FortranVariable,
)

from .models import (
    EXTERNAL_TYPE_REF_METADATA,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticOrigin,
    SemanticStorageContract,
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
    ("logical", "1"): "Bool",
    ("logical", "2"): "Bool",
    ("logical", "4"): "Bool",
    ("logical", "8"): "Bool",
    ("logical", "c_bool"): "Bool",
    ("character", None): "String",
    ("character", "1"): "String",
    ("character", "c_char"): "String",
}


@dataclass(frozen=True)
class _DerivedTypeContext:
    module: str | None = None
    uses: dict[str, list[FortranUseMapping]] | None = None
    local_types: frozenset[str] = frozenset()


def _normalize_compile_time_values(
    compile_time_values: dict[str, int | str] | None,
) -> dict[str, str]:
    """Normalize user-supplied compile-time values for text substitution.

    The semantic layer accepts values keyed either by a symbol name
    (``{"rk": 8}``) or by the exact unresolved expression kept by the parser
    (``{"selected_real_kind(12)": 8}``). Internally both keys and values are
    strings so that kind and shape expressions can be rewritten uniformly.

    Example:
        >>> _normalize_compile_time_values({"rk": 8})["rk"]
        '8'
    """
    return {
        str(key).strip().lower(): str(value) for key, value in (compile_time_values or {}).items() if str(key).strip()
    }


def _resolve_compile_time_text(text: str, compile_time_values: dict[str, str]) -> str:
    """Resolve known compile-time symbols inside one kind or shape expression.

    Exact expression keys win before identifier replacement, so compiler or
    implementation-specific calls can be supplied directly. Symbol keys are
    then substituted token by token.

    Example:
        >>> values = _normalize_compile_time_values({"selected_real_kind(12)": 8, "n": 32})
        >>> _resolve_compile_time_text("selected_real_kind(12)", values)
        '8'
        >>> _resolve_compile_time_text("1:n", values)
        '1:32'
    """
    raw = str(text)
    stripped = raw.strip()
    if not stripped or not compile_time_values:
        return raw

    exact = compile_time_values.get(stripped.lower())
    if exact is not None:
        return exact

    def replace_symbol(match: re.Match[str]) -> str:
        token = match.group(0)
        return compile_time_values.get(token.lower(), token)

    return re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\b", replace_symbol, raw)


class FortranToIRConverter:
    """Convert parsed Fortran models into semantic IR models.

    The converter is intentionally a small visitor: public compatibility methods
    delegate to explicit `visit_*` methods, and each visitor method converts one
    parser model type into the corresponding semantic model type.
    """

    def __init__(
        self,
        type_map: dict[tuple[str, str | None], str] | None = None,
        compile_time_values: dict[str, int | str] | None = None,
        wrapped_derived_types: Iterable[tuple[str, str]] | None = None,
    ):
        self.type_map = FORTRAN_TYPE_MAP if type_map is None else type_map
        self.compile_time_values = _normalize_compile_time_values(compile_time_values)
        self.wrapped_derived_types = {
            (str(module).lower(), str(name).lower()) for module, name in (wrapped_derived_types or [])
        }

    def visit(self, node, **context):
        """Dispatch one parsed Fortran model to the matching conversion method."""
        if isinstance(node, FortranProject):
            return self.visit_project(node)
        if isinstance(node, FortranFile):
            return self.visit_file(node)
        if isinstance(node, FortranModule):
            return self.visit_module(node)
        if isinstance(node, FortranProcedureSignature):
            return self.visit_procedure(
                node,
                visibility=context.get("visibility", "public"),
                derived_type_context=context.get("derived_type_context"),
            )
        if isinstance(node, FortranDerivedType):
            return self.visit_derived_type(
                node,
                procedure_lookup=context.get("procedure_lookup", {}),
                derived_type_context=context.get("derived_type_context"),
            )
        if isinstance(node, FortranArgument):
            return self.visit_argument(node, derived_type_context=context.get("derived_type_context"))
        if isinstance(node, FortranVariable):
            return self.visit_variable(node, derived_type_context=context.get("derived_type_context"))
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
        converter = self._with_additional_wrapped_types(self._wrapped_types_from_file(parsed_file))
        return converter.visit_module(self.first_module(parsed_file))

    def visit_project(self, project: FortranProject) -> list[SemanticModule]:
        converter = self._with_additional_wrapped_types(self._wrapped_types_from_project(project))
        return [module for parsed_file in project.files for module in converter.visit_file_modules(parsed_file)]

    def visit_variable(
        self,
        var: FortranVariable,
        *,
        derived_type_context: _DerivedTypeContext | None = None,
    ) -> SemanticType:
        semantic_name = self._semantic_type_name(var)
        derived_type_ref = self._derived_type_ref(var, derived_type_context)
        metadata = {}
        if derived_type_ref is not None:
            semantic_name, ref_metadata = derived_type_ref
            metadata[EXTERNAL_TYPE_REF_METADATA] = ref_metadata
        shape = [self._resolve_compile_time_text(dim) for dim in var.shape]
        storage = self._array_storage_contract(var, shape) if var.rank > 0 else None
        semantic_type = SemanticType(
            name=semantic_name,
            rank=var.rank,
            dtype=semantic_name,
            shape=list(storage.array.shape if storage is not None and storage.array is not None else shape),
            metadata=metadata,
            storage=storage,
            origin=self._variable_origin(var),
        )
        self._add_variable_constraints(semantic_type, var)
        return semantic_type

    def visit_argument(
        self,
        arg: FortranArgument | FortranVariable,
        *,
        intent: str | None = None,
        derived_type_context: _DerivedTypeContext | None = None,
    ) -> SemanticArgument:
        semantic_type = self.visit_variable(arg, derived_type_context=derived_type_context)
        resolved_intent = intent if intent is not None else getattr(arg, "intent", "in")
        resolved_intent = str(resolved_intent).lower().replace(" ", "")
        if resolved_intent == "unknown":
            resolved_intent = "inout"
        if semantic_type.rank > 0:
            self._apply_array_argument_contract(semantic_type, arg, resolved_intent)
        elif not getattr(arg, "pass_by_value", False):
            semantic_type.storage = self._reference_storage_contract(resolved_intent)
        self._apply_argument_ownership(semantic_type, resolved_intent)

        return SemanticArgument(
            name=arg.name,
            semantic_type=semantic_type,
            intent=resolved_intent,
            optional=getattr(arg, "optional", False),
            visibility=getattr(arg, "visibility", "public"),
            origin=self._argument_origin(arg),
        )

    def visit_data_member(
        self,
        var: FortranArgument | FortranVariable,
        *,
        intent: str = "in",
        derived_type_context: _DerivedTypeContext | None = None,
    ) -> SemanticArgument:
        semantic_type = self.visit_variable(var, derived_type_context=derived_type_context)
        if semantic_type.storage is not None and semantic_type.storage.array is not None:
            semantic_type.storage.array.allocatable = getattr(var, "allocatable", False)
            semantic_type.storage.array.pointer = getattr(var, "pointer", False)
        return SemanticArgument(
            name=var.name,
            semantic_type=semantic_type,
            intent=intent,
            optional=getattr(var, "optional", False),
            visibility=getattr(var, "visibility", "public"),
            origin=self._argument_origin(var),
        )

    def visit_procedure(
        self,
        proc: FortranProcedureSignature,
        visibility: str = "public",
        *,
        derived_type_context: _DerivedTypeContext | None = None,
    ) -> SemanticFunction:
        context = self._procedure_derived_type_context(proc, derived_type_context)
        arguments = [self.visit_argument(arg, derived_type_context=context) for arg in proc.arguments]
        return SemanticFunction(
            name=proc.name,
            native_name=proc.name,
            arguments=arguments,
            return_type=self.visit_variable(proc.result, derived_type_context=context) if proc.result else None,
            projection=self._procedure_projection(proc, arguments),
            visibility=visibility,
            origin=SemanticOrigin(
                source_language="fortran",
                native_name=proc.name,
                native_scope=proc.module,
                source_kind=proc.kind,
            ),
        )

    def visit_derived_type(
        self,
        dtype: FortranDerivedType,
        procedure_lookup: dict[str, SemanticFunction] | None = None,
        *,
        derived_type_context: _DerivedTypeContext | None = None,
    ) -> SemanticClass:
        lookup = procedure_lookup or {}
        context = derived_type_context or _DerivedTypeContext(
            module=dtype.module,
            local_types=frozenset({dtype.name.lower()}),
        )
        return SemanticClass(
            name=dtype.name,
            native_name=dtype.name,
            fields=[self.visit_data_member(field, intent="in", derived_type_context=context) for field in dtype.fields],
            methods=self._bound_methods(dtype, lookup),
            base_classes=self._base_classes(dtype),
            visibility=getattr(dtype, "visibility", "public"),
            origin=SemanticOrigin(
                source_language="fortran",
                native_name=dtype.name,
                native_scope=dtype.module,
                source_kind="derived_type",
            ),
        )

    def visit_module(self, module: FortranModule) -> SemanticModule:
        context = self._module_derived_type_context(module)
        semantic_functions = [
            self.visit_procedure(
                proc,
                visibility=self._symbol_visibility(module, proc.name),
                derived_type_context=context,
            )
            for proc in module.procedures
        ]
        procedure_lookup = {func.name: func for func in semantic_functions}

        semantic_classes = [
            self.visit_derived_type(
                dtype,
                procedure_lookup=procedure_lookup,
                derived_type_context=context,
            )
            for dtype in module.derived_types
        ]
        for semantic_cls in semantic_classes:
            semantic_cls.visibility = self._symbol_visibility(module, semantic_cls.name)

        return SemanticModule(
            name=module.name,
            functions=semantic_functions,
            classes=semantic_classes,
            variables=[
                self.visit_data_member(var, intent="in", derived_type_context=context)
                for var in getattr(module, "variables", [])
            ],
            imports=self._module_imports(module),
            origin=SemanticOrigin(
                source_language="fortran",
                native_name=module.name,
                native_scope=module.name,
                source_kind="module",
            ),
        )

    def visit_file_modules(
        self,
        parsed_file: FortranFile,
        *,
        standalone_module_name: str | None = None,
    ) -> list[SemanticModule]:
        converter = self._with_additional_wrapped_types(self._wrapped_types_from_file(parsed_file))
        modules = [converter.visit_module(module) for module in parsed_file.modules]
        if parsed_file.procedures:
            modules.append(
                converter.procedures_to_semantic_module(
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
        if isinstance(module, FortranFile):
            return self.visit_file(module)
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
                        items=[SemanticImportItem(source=item.source, target=item.target) for item in mappings],
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

    def project_to_semantic_modules(self, project: FortranProject) -> list[SemanticModule]:
        return self.visit_project(project)

    def _with_additional_wrapped_types(
        self,
        wrapped_types: Iterable[tuple[str, str]],
    ) -> FortranToIRConverter:
        merged = self.wrapped_derived_types | {
            (str(module).lower(), str(name).lower()) for module, name in wrapped_types
        }
        if merged == self.wrapped_derived_types:
            return self
        return FortranToIRConverter(
            type_map=self.type_map,
            compile_time_values=self.compile_time_values,
            wrapped_derived_types=merged,
        )

    @staticmethod
    def _wrapped_types_from_file(parsed_file: FortranFile) -> set[tuple[str, str]]:
        return {
            (dtype.module.lower(), dtype.name.lower())
            for module in parsed_file.modules
            for dtype in module.derived_types
            if dtype.module
        }

    @staticmethod
    def _wrapped_types_from_project(project: FortranProject) -> set[tuple[str, str]]:
        return {(dtype.module.lower(), dtype.name.lower()) for dtype in project.derived_types.values() if dtype.module}

    @staticmethod
    def _module_derived_type_context(module: FortranModule) -> _DerivedTypeContext:
        return _DerivedTypeContext(
            module=module.name,
            uses=module.uses,
            local_types=frozenset(dtype.name.lower() for dtype in module.derived_types),
        )

    @staticmethod
    def _procedure_derived_type_context(
        proc: FortranProcedureSignature,
        parent: _DerivedTypeContext | None,
    ) -> _DerivedTypeContext:
        uses = dict(parent.uses or {}) if parent is not None else {}
        uses.update(proc.uses)
        return _DerivedTypeContext(
            module=proc.module or (parent.module if parent is not None else None),
            uses=uses,
            local_types=parent.local_types if parent is not None else frozenset(),
        )

    def _derived_type_ref(
        self,
        var: FortranVariable,
        context: _DerivedTypeContext | None,
    ) -> tuple[str, dict[str, object]] | None:
        if var.base_type.lower() != "derived":
            return None
        local_name = str(var.kind)
        if not local_name:
            return None

        origin_module, source_name = self._resolve_derived_type_origin(local_name, context)
        local_type = bool(context is not None and context.module and local_name.lower() in context.local_types)
        if local_type or origin_module is None:
            return None
        wrapped = bool(origin_module and (origin_module.lower(), source_name.lower()) in self.wrapped_derived_types)
        return local_name, {
            "name": source_name,
            "local_name": local_name,
            "origin_module": origin_module,
            "wrapped": wrapped,
            "representation": "wrapped" if wrapped else "opaque",
        }

    def _resolve_derived_type_origin(
        self,
        local_name: str,
        context: _DerivedTypeContext | None,
    ) -> tuple[str | None, str]:
        lname = local_name.lower()
        if context is None:
            return None, local_name
        if lname in context.local_types:
            return context.module, local_name

        explicit: list[tuple[str, str]] = []
        wildcard_modules: list[str] = []
        for module_name, mappings in (context.uses or {}).items():
            if not mappings:
                wildcard_modules.append(module_name)
                continue
            for mapping in mappings:
                if mapping.local_name.lower() == lname:
                    explicit.append((module_name, mapping.source))

        if len(explicit) == 1:
            return explicit[0]
        if len(explicit) > 1:
            return None, local_name

        wrapped_wildcards = [
            module_name
            for module_name in wildcard_modules
            if (module_name.lower(), lname) in self.wrapped_derived_types
        ]
        if len(wrapped_wildcards) == 1:
            return wrapped_wildcards[0], local_name
        if len(wildcard_modules) == 1:
            return wildcard_modules[0], local_name
        return None, local_name

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

    def _semantic_kind_key(self, var: FortranVariable) -> str | None:
        if not var.kind:
            return None

        base_type = var.base_type.lower()
        kind = self._resolve_compile_time_text(str(var.kind)).strip().lower()
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

    def _resolve_compile_time_text(self, text: str) -> str:
        return _resolve_compile_time_text(text, self.compile_time_values)

    @staticmethod
    def _variable_origin(var: FortranVariable) -> SemanticOrigin:
        return SemanticOrigin(
            source_language="fortran",
            native_name=var.name,
            source_kind="variable",
            source_type=FortranToIRConverter._fortran_source_type(var),
            metadata=FortranToIRConverter._fortran_variable_metadata(var),
        )

    @staticmethod
    def _argument_origin(arg: FortranArgument | FortranVariable) -> SemanticOrigin:
        return SemanticOrigin(
            source_language="fortran",
            native_name=arg.name,
            native_scope=getattr(arg, "procedure", None),
            source_kind="argument" if isinstance(arg, FortranArgument) else "variable",
            source_type=FortranToIRConverter._fortran_source_type(arg),
            metadata=FortranToIRConverter._fortran_variable_metadata(arg),
        )

    @staticmethod
    def _fortran_source_type(var: FortranVariable) -> str:
        if var.kind:
            return f"{var.base_type}(kind={var.kind})"
        return var.base_type

    @staticmethod
    def _fortran_variable_metadata(var: FortranVariable) -> dict[str, object]:
        metadata: dict[str, object] = {
            "rank": var.rank,
            "shape": list(var.shape),
            "lower_bounds": list(getattr(var, "lbound", []) or []),
            "upper_bounds": list(getattr(var, "ubound", []) or []),
        }
        if isinstance(var, FortranArgument):
            metadata.update(
                {
                    "intent": var.intent,
                    "optional": var.optional,
                    "value": var.pass_by_value,
                    "allocatable": var.allocatable,
                    "pointer": var.pointer,
                    "contiguous": getattr(var, "contiguous", False),
                }
            )
        if getattr(var, "is_parameter", False):
            metadata["constant"] = True
        return metadata

    def _array_storage_contract(
        self,
        var: FortranVariable,
        shape: list[str],
    ) -> SemanticStorageContract:
        category = self._array_category(var, shape)
        axes = self._array_axes(shape, category, contiguous=getattr(var, "contiguous", False))
        rank = var.rank
        order = self._array_order(rank, category, contiguous=getattr(var, "contiguous", False))
        lower_bounds, upper_bounds = self._array_bound_metadata(shape)
        array = SemanticArrayContract(
            rank=rank,
            shape=list(axes),
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            source_shape=list(shape),
            category=category,
            order=order,
            axes=["strided" if self._is_strided_axis(axis) else "dense" for axis in axes],
            contiguous=self._array_contiguous(category, contiguous=getattr(var, "contiguous", False)),
            allocatable=getattr(var, "allocatable", False),
            pointer=getattr(var, "pointer", False),
        )
        return SemanticStorageContract(
            kind="array",
            mutable=False,
            array=array,
        )

    def _resolve_optional_compile_time_text(self, text: str | None) -> str | None:
        if text is None:
            return None
        return self._resolve_compile_time_text(text)

    def _array_bound_metadata(self, shape: list[str]) -> tuple[list[str | None], list[str | None]]:
        lower_bounds: list[str | None] = []
        upper_bounds: list[str | None] = []
        for dim in shape:
            token = dim.strip()
            if ":" not in token:
                lower_bounds.append(None)
                upper_bounds.append("*" if token == "*" else None)
                continue
            lower, upper = self._dimension_bounds(token)
            lower_bounds.append(None if lower in {None, "1"} else self._resolve_compile_time_text(lower))
            upper_bounds.append(self._resolve_optional_compile_time_text(upper))
        if all(value is None for value in lower_bounds):
            lower_bounds = []
        if all(value is None for value in upper_bounds):
            upper_bounds = []
        return lower_bounds, upper_bounds

    @staticmethod
    def _array_category(var: FortranVariable, shape: list[str]) -> str:
        cleaned = [dim.strip() for dim in shape]
        if cleaned == [".."]:
            return "assumed_rank"
        if cleaned and cleaned[-1] == "*":
            return "assumed_size"
        if any(dim.endswith(":*") for dim in cleaned):
            return "assumed_size"
        if isinstance(var, FortranArgument) and (getattr(var, "allocatable", False) or getattr(var, "pointer", False)):
            return (
                "deferred_shape"
                if any(FortranToIRConverter._has_omitted_upper_bound(dim) for dim in cleaned)
                else "explicit_shape"
            )
        if any(FortranToIRConverter._has_omitted_upper_bound(dim) for dim in cleaned):
            return "assumed_shape"
        return "explicit_shape"

    @classmethod
    def _array_axes(cls, shape: list[str], category: str, *, contiguous: bool) -> list[str]:
        if category == "assumed_rank":
            return ["..."]
        if category == "assumed_shape" and not contiguous:
            return ["::Strided" for _dim in shape]

        axes: list[str] = []
        for dim in shape:
            token = dim.strip()
            if token == "*":
                axes.append(":")
                continue
            if token.endswith(":*"):
                axes.append(":")
                continue
            lower, upper = cls._dimension_bounds(token)
            if lower in {None, "1"} and upper:
                axes.append(cls._canonical_dimension_expression(upper))
            elif lower is not None and upper is not None:
                axes.append(cls._canonical_dimension_expression(f"({upper}) - ({lower}) + 1"))
            elif ":" in token:
                axes.append(":")
            else:
                axes.append(cls._canonical_dimension_expression(token))
        return axes

    @staticmethod
    def _dimension_bounds(token: str) -> tuple[str | None, str | None]:
        if ":" not in token:
            return "1", token
        lower, upper = token.split(":", 1)
        return lower.strip() or None, upper.strip() or None

    @staticmethod
    def _has_omitted_upper_bound(token: str) -> bool:
        return ":" in token and token.split(":", 1)[1].strip() == ""

    @staticmethod
    def _canonical_dimension_expression(expression: str) -> str:
        try:
            return ast.unparse(ast.parse(expression, mode="eval").body)
        except SyntaxError:
            return expression

    @staticmethod
    def _array_order(rank: int, category: str, *, contiguous: bool) -> str | None:
        if rank <= 1:
            return None
        return "ORDER_F"

    @staticmethod
    def _array_contiguous(category: str, *, contiguous: bool) -> bool | None:
        if contiguous:
            return True
        if category in {"explicit_shape", "assumed_size", "deferred_shape"}:
            return True
        if category == "assumed_shape":
            return False
        return None

    @staticmethod
    def _is_strided_axis(axis: str) -> bool:
        return "Strided" in axis

    @staticmethod
    def _reference_storage_contract(intent: str) -> SemanticStorageContract:
        read_only = str(intent).lower() == "in"
        return SemanticStorageContract(
            kind="reference",
            read_only=read_only,
            mutable=not read_only,
            pointer_depth=1,
        )

    @staticmethod
    def _apply_array_argument_contract(
        semantic_type: SemanticType,
        arg: FortranArgument | FortranVariable,
        intent: str,
    ) -> None:
        if semantic_type.storage is None:
            return
        read_only = str(intent).lower() == "in"
        semantic_type.storage.read_only = read_only
        semantic_type.storage.mutable = not read_only
        if semantic_type.storage.array is not None:
            semantic_type.storage.array.allocatable = getattr(arg, "allocatable", False)
            semantic_type.storage.array.pointer = getattr(arg, "pointer", False)
            if getattr(arg, "contiguous", False):
                semantic_type.storage.array.contiguous = True

    @staticmethod
    def _add_variable_constraints(semantic_type: SemanticType, var: FortranVariable) -> None:
        if getattr(var, "is_parameter", False):
            semantic_type.constraints.append(SemanticConstraint("Constant"))

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
                    projection=proc.projection,
                    visibility=proc.visibility,
                    origin=proc.origin,
                )
            )
        return methods

    @staticmethod
    def _projected_procedure_arguments(proc: FortranProcedureSignature) -> list[FortranArgument]:
        args = list(proc.arguments)
        return [
            *[arg for arg in args if getattr(arg, "intent", "in") != "out" and not getattr(arg, "optional", False)],
            *[arg for arg in args if getattr(arg, "intent", "in") != "out" and getattr(arg, "optional", False)],
            *[arg for arg in args if getattr(arg, "intent", "in") == "out"],
        ]

    @staticmethod
    def _procedure_projection(
        proc: FortranProcedureSignature,
        arguments: list[SemanticArgument],
    ) -> list[ProjectionMapping]:
        by_name = {arg.name: arg for arg in arguments}

        projection: list[ProjectionMapping] = []
        for native_position, native_arg in enumerate(proc.arguments):
            arg = by_name[native_arg.name]
            intent = getattr(arg, "intent", "in")
            projection.append(
                ProjectionMapping(
                    python_name=arg.name,
                    native_name=native_arg.name,
                    native_position=native_position,
                    python_position=native_position,
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


def _requirement_unit_name(
    *,
    module: str | None = None,
    unit_name: str | None = None,
) -> str:
    if module and unit_name:
        return f"{module}.{unit_name}"
    return unit_name or module or "<source>"


def _iter_fortran_variable_contexts(
    node,
    *,
    module_name: str | None = None,
    unit_kind: str = "file",
    unit_name: str | None = None,
):
    """Yield parser variables with enough unit context for diagnostics.

    Example:
        ``list(_iter_fortran_variable_contexts(parsed_file))`` returns module
        parameters, procedure arguments/results/locals, and type fields with
        the unit that owns each symbol.
    """
    if isinstance(node, FortranFile):
        file_unit = node.filename or "<source>"
        for var in getattr(node, "variables", []):
            yield (
                var,
                {
                    "unit_kind": "file",
                    "unit": file_unit,
                    "module": None,
                    "symbol": var.name,
                    "role": "variable",
                },
            )
        for module in node.modules:
            yield from _iter_fortran_variable_contexts(module)
        for submodule in node.submodules:
            yield from _iter_fortran_variable_contexts(submodule)
        for program in node.programs:
            yield from _iter_fortran_variable_contexts(program)
        for block_data in node.block_data_units:
            yield from _iter_fortran_variable_contexts(block_data)
        for proc in node.procedures:
            yield from _iter_fortran_variable_contexts(proc)
        for dtype in node.derived_types:
            yield from _iter_fortran_variable_contexts(dtype)
        return

    if isinstance(node, FortranModule | FortranSubmodule):
        owner = node.name
        for var in node.variables:
            yield (
                var,
                {
                    "unit_kind": "module" if isinstance(node, FortranModule) else "submodule",
                    "unit": owner,
                    "module": owner,
                    "symbol": var.name,
                    "role": "variable",
                },
            )
        for proc in node.procedures:
            yield from _iter_fortran_variable_contexts(proc, module_name=owner)
        for dtype in node.derived_types:
            yield from _iter_fortran_variable_contexts(dtype, module_name=owner)
        return

    if isinstance(node, FortranProgram):
        owner = node.name or "<program>"
        for var in node.variables:
            yield (
                var,
                {
                    "unit_kind": "program",
                    "unit": owner,
                    "module": None,
                    "symbol": var.name,
                    "role": "variable",
                },
            )
        for proc in node.procedures:
            yield from _iter_fortran_variable_contexts(proc, unit_kind="program", unit_name=owner)
        return

    if isinstance(node, FortranBlockData):
        owner = node.name or "<block_data>"
        for var in node.variables:
            yield (
                var,
                {
                    "unit_kind": "block_data",
                    "unit": owner,
                    "module": None,
                    "symbol": var.name,
                    "role": "variable",
                },
            )
        return

    if isinstance(node, FortranProcedureSignature):
        proc_module = module_name or node.module
        owner = _requirement_unit_name(module=proc_module, unit_name=node.name)
        for arg in node.arguments:
            yield (
                arg,
                {
                    "unit_kind": "procedure",
                    "unit": owner,
                    "module": proc_module,
                    "procedure": node.name,
                    "symbol": arg.name,
                    "role": "argument",
                },
            )
        if node.result is not None:
            yield (
                node.result,
                {
                    "unit_kind": "procedure",
                    "unit": owner,
                    "module": proc_module,
                    "procedure": node.name,
                    "symbol": node.result.name,
                    "role": "result",
                },
            )
        for var in node.variables.values():
            yield (
                var,
                {
                    "unit_kind": "procedure",
                    "unit": owner,
                    "module": proc_module,
                    "procedure": node.name,
                    "symbol": var.name,
                    "role": "variable",
                },
            )
        return

    if isinstance(node, FortranDerivedType):
        owner = _requirement_unit_name(module=module_name or node.module, unit_name=node.name)
        for field in node.fields:
            yield (
                field,
                {
                    "unit_kind": "derived_type",
                    "unit": owner,
                    "module": module_name or node.module,
                    "type_owner": node.name,
                    "symbol": field.name,
                    "role": "field",
                },
            )


def _compile_time_requirement_message(code: str, symbol: str, expression: str) -> str:
    if code == "parameter_value":
        return f"Parameter '{symbol}' needs a compile-time value for expression '{expression}'."
    if code == "unsupported_kind":
        return f"Kind expression for '{symbol}' needs a supported compile-time value."
    return f"Compile-time value required for '{symbol}'."


def collect_semantic_compile_time_requirements(
    parsed,
    *,
    compile_time_values: dict[str, int | str] | None = None,
    type_map: dict[tuple[str, str | None], str] | None = None,
) -> list[dict[str, str | None]]:
    """Collect parser symbols that block semantic IR conversion or wrapping.

    This is the inspection half of the "unknown compile-time value" workflow:
    parse first, collect unresolved parameter/kind expressions, evaluate them
    externally when needed, then pass the resulting dictionary to
    ``FortranToIRConverter(..., compile_time_values=...)`` or the convenience
    wrappers below.

    Example:
        >>> from x2py import parse_fortran_file
        >>> parsed = parse_fortran_file("module m\ninteger, parameter :: rk = selected_real_kind(12)\nend module")
        >>> reqs = collect_semantic_compile_time_requirements(parsed)
        >>> reqs[0]["symbol"]
        'rk'
    """
    values = _normalize_compile_time_values(compile_time_values)
    converter = FortranToIRConverter(type_map=type_map, compile_time_values=values)
    requirements: list[dict[str, str | None]] = []
    seen: set[tuple[str | None, ...]] = set()

    def add_requirement(
        code: str, ctx: dict, *, expression: str, base_type: str | None = None, kind: str | None = None
    ) -> None:
        symbol = str(ctx.get("symbol") or "")
        item = {
            "code": code,
            "unit_kind": ctx.get("unit_kind"),
            "unit": ctx.get("unit"),
            "module": ctx.get("module"),
            "procedure": ctx.get("procedure"),
            "type_owner": ctx.get("type_owner"),
            "role": ctx.get("role"),
            "symbol": symbol,
            "base_type": base_type,
            "kind": kind,
            "expression": expression,
            "message": _compile_time_requirement_message(code, symbol, expression),
        }
        key = tuple(
            str(item.get(field) or "") for field in ("code", "unit", "symbol", "base_type", "kind", "expression")
        )
        if key in seen:
            return
        seen.add(key)
        requirements.append(item)

    for var, ctx in _iter_fortran_variable_contexts(parsed):
        expression = var.symbolic_value if var.symbolic_value is not None else var.value
        if var.is_parameter and var.value is None and expression:
            resolved = _resolve_compile_time_text(expression, values)
            supplied_by_symbol = values.get(var.name.lower())
            if supplied_by_symbol is None and resolved == expression:
                add_requirement("parameter_value", ctx, expression=expression)

        base_type = str(var.base_type or "").lower()
        if base_type not in {"integer", "real", "complex", "logical", "character"} or not var.kind:
            continue
        kind_key = converter._semantic_kind_key(var)
        if converter.type_map.get((base_type, kind_key)) is None:
            expression = _resolve_compile_time_text(str(var.kind), values)
            add_requirement(
                "unsupported_kind",
                ctx,
                expression=expression,
                base_type=base_type,
                kind=kind_key,
            )

    return requirements


def _resolve_semantic_value(value, compile_time_values: dict[str, str]):
    if isinstance(value, str):
        return _resolve_compile_time_text(value, compile_time_values)
    if isinstance(value, list):
        return [_resolve_semantic_value(item, compile_time_values) for item in value]
    if isinstance(value, tuple):
        return tuple(_resolve_semantic_value(item, compile_time_values) for item in value)
    if isinstance(value, dict):
        return {key: _resolve_semantic_value(item, compile_time_values) for key, item in value.items()}
    return value


def _resolve_semantic_type_compile_time_values(
    semantic_type: SemanticType | None,
    compile_time_values: dict[str, str],
) -> None:
    if semantic_type is None:
        return
    semantic_type.shape = [_resolve_compile_time_text(dim, compile_time_values) for dim in semantic_type.shape]
    for constraint in semantic_type.constraints:
        constraint.arguments = _resolve_semantic_value(constraint.arguments, compile_time_values)
    semantic_type.metadata = _resolve_semantic_value(semantic_type.metadata, compile_time_values)
    if semantic_type.storage is not None:
        semantic_type.storage.metadata = _resolve_semantic_value(
            semantic_type.storage.metadata,
            compile_time_values,
        )
        if semantic_type.storage.array is not None:
            array = semantic_type.storage.array
            array.shape = [_resolve_compile_time_text(dim, compile_time_values) for dim in array.shape]
            array.source_shape = [_resolve_compile_time_text(dim, compile_time_values) for dim in array.source_shape]
            array.lower_bounds = [
                None if dim is None else _resolve_compile_time_text(dim, compile_time_values)
                for dim in array.lower_bounds
            ]
            array.upper_bounds = [
                None if dim is None else _resolve_compile_time_text(dim, compile_time_values)
                for dim in array.upper_bounds
            ]
            array.metadata = _resolve_semantic_value(array.metadata, compile_time_values)


def _resolve_semantic_argument_compile_time_values(
    arg: SemanticArgument,
    compile_time_values: dict[str, str],
) -> None:
    _resolve_semantic_type_compile_time_values(arg.semantic_type, compile_time_values)
    arg.default_value = _resolve_semantic_value(arg.default_value, compile_time_values)
    arg.metadata = _resolve_semantic_value(arg.metadata, compile_time_values)


def _resolve_semantic_function_compile_time_values(
    func: SemanticFunction,
    compile_time_values: dict[str, str],
) -> None:
    for arg in func.arguments:
        _resolve_semantic_argument_compile_time_values(arg, compile_time_values)
    _resolve_semantic_type_compile_time_values(func.return_type, compile_time_values)
    for mapping in func.projection:
        mapping.value = _resolve_semantic_value(mapping.value, compile_time_values)
    func.metadata = _resolve_semantic_value(func.metadata, compile_time_values)


def _resolve_semantic_module_compile_time_values(
    module: SemanticModule,
    compile_time_values: dict[str, str],
) -> None:
    for var in module.variables:
        _resolve_semantic_argument_compile_time_values(var, compile_time_values)
    for func in module.functions:
        _resolve_semantic_function_compile_time_values(func, compile_time_values)
    for cls in module.classes:
        for field in cls.fields:
            _resolve_semantic_argument_compile_time_values(field, compile_time_values)
        for method in cls.methods:
            _resolve_semantic_function_compile_time_values(method, compile_time_values)
        cls.metadata = _resolve_semantic_value(cls.metadata, compile_time_values)
    module.metadata = _resolve_semantic_value(module.metadata, compile_time_values)


def resolve_semantic_compile_time_values(
    semantic_ir: SemanticModule | list[SemanticModule],
    compile_time_values: dict[str, int | str],
) -> SemanticModule | list[SemanticModule]:
    """Return a copy of semantic IR with known compile-time text resolved.

    Use this after semantic conversion when symbolic shape metadata should be
    specialized without mutating the original IR object.

    Example:
        >>> mod = SemanticModule(name="m", variables=[SemanticArgument("x", SemanticType("Float64", rank=1, shape=["1:n"]))])
        >>> resolve_semantic_compile_time_values(mod, {"n": 4}).variables[0].semantic_type.shape
        ['1:4']
    """
    values = _normalize_compile_time_values(compile_time_values)
    resolved = deepcopy(semantic_ir)
    modules = resolved if isinstance(resolved, list) else [resolved]
    for module in modules:
        _resolve_semantic_module_compile_time_values(module, values)
    return resolved


def _converter_for(
    compile_time_values: dict[str, int | str] | None = None,
    wrapped_derived_types: Iterable[tuple[str, str]] | None = None,
) -> FortranToIRConverter:
    if compile_time_values is None and wrapped_derived_types is None:
        return _DEFAULT_CONVERTER
    return FortranToIRConverter(
        compile_time_values=compile_time_values,
        wrapped_derived_types=wrapped_derived_types,
    )


_DEFAULT_CONVERTER = FortranToIRConverter()


def fortran_module_to_semantic_module(
    module,
    *,
    compile_time_values: dict[str, int | str] | None = None,
    wrapped_derived_types: Iterable[tuple[str, str]] | None = None,
) -> SemanticModule:
    return _converter_for(compile_time_values, wrapped_derived_types).module_to_semantic_module(module)


def fortran_file_to_semantic_modules(
    parsed_file: FortranFile,
    *,
    standalone_module_name: str | None = None,
    compile_time_values: dict[str, int | str] | None = None,
    wrapped_derived_types: Iterable[tuple[str, str]] | None = None,
) -> list[SemanticModule]:
    return _converter_for(compile_time_values, wrapped_derived_types).file_to_semantic_modules(
        parsed_file,
        standalone_module_name=standalone_module_name,
    )


def fortran_project_to_semantic_modules(
    project: FortranProject,
    *,
    compile_time_values: dict[str, int | str] | None = None,
) -> list[SemanticModule]:
    return _converter_for(compile_time_values).project_to_semantic_modules(project)


if __name__ == "__main__":
    pass
