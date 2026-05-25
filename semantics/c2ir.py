from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from c_parser.models import (
    CArray,
    CAtomic,
    CBool,
    CChar,
    CComposedType,
    CConst,
    CDouble,
    CDoubleComplex,
    CDiagnostic,
    CEnum,
    CFile,
    CFloat,
    CFloatComplex,
    CFunction,
    CFunctionType,
    CLong,
    CLongDouble,
    CLongDoubleComplex,
    CLongLong,
    CParameter,
    CPointer,
    CProject,
    CQualifier,
    CRestrict,
    CShort,
    CSignedChar,
    CStruct,
    CType,
    CTypedef,
    CUnion,
    CUnknownType,
    CUnsignedChar,
    CUnsignedInt,
    CUnsignedLong,
    CUnsignedLongLong,
    CUnsignedShort,
    CVariable,
    CVoid,
    CVolatile,
    CInt,
)

from .models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticModule,
    SemanticOrigin,
    SemanticStorageContract,
    SemanticType,
)


_IDENTIFIER_RE = re.compile(r"[^0-9A-Za-z_]+")
_INTEGER_LITERAL_RE = re.compile(r"[-+]?(?:0[xX][0-9A-Fa-f]+|\d+)(?:[uUlL]*)\Z")
_FLOAT_LITERAL_RE = re.compile(
    r"[-+]?(?:(?:\d+\.\d*)|(?:\.\d+)|(?:\d+[eE][-+]?\d+)|(?:\d+\.\d*[eE][-+]?\d+))(?:[fFlL]*)\Z"
)
_SIGNED_WIDTH_TYPES = {8: "Int8", 16: "Int16", 32: "Int32", 64: "Int64"}
_UNSIGNED_WIDTH_TYPES = {8: "UInt8", 16: "UInt16", 32: "UInt32", 64: "UInt64"}
_NUMERIC_SEMANTIC_TYPES = frozenset(
    {
        "Bool",
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "UInt8",
        "UInt16",
        "UInt32",
        "UInt64",
        "Float32",
        "Float64",
        "Complex64",
        "Complex128",
        "Any",
        "SizeT",
    }
)

_PRIMITIVE_TYPE_MAP: dict[type[CType], str | None] = {
    CVoid: None,
    CBool: "Bool",
    CChar: "Int8",
    CSignedChar: "Int8",
    CUnsignedChar: "UInt8",
    CShort: "Int16",
    CUnsignedShort: "UInt16",
    CInt: "Int32",
    CUnsignedInt: "UInt32",
    CLong: "Int64",
    CUnsignedLong: "UInt64",
    CLongLong: "Int64",
    CUnsignedLongLong: "UInt64",
    CFloat: "Float32",
    CDouble: "Float64",
    CFloatComplex: "Complex64",
    CDoubleComplex: "Complex128",
}

_STANDARD_TYPE_FALLBACKS = {
    "size_t": "SizeT",
    "uint8_t": "UInt8",
    "uint16_t": "UInt16",
    "uint32_t": "UInt32",
    "uint64_t": "UInt64",
    "int8_t": "Int8",
    "int16_t": "Int16",
    "int32_t": "Int32",
    "int64_t": "Int64",
}


class CToIRConverter:
    """Convert parsed C models into the shared semantic IR.

    The converter intentionally keeps C parser facts as provenance and blocker
    metadata instead of teaching the parser wrappability policy. The produced
    semantic IR can therefore be checked by the same readiness layer used for
    Fortran and edited ``.pyi`` files.
    """

    def __init__(
        self,
        *,
        standard_type_report: Any | None = None,
        primitive_type_map: dict[type[CType], str | None] | None = None,
    ):
        self.primitive_type_map = dict(_PRIMITIVE_TYPE_MAP)
        if primitive_type_map:
            self.primitive_type_map.update(primitive_type_map)
        self.standard_type_facts = self._standard_type_facts(standard_type_report)
        self.typedefs: dict[str, CTypedef] = {}
        self.structs: dict[str, CStruct] = {}
        self.unions: dict[str, CUnion] = {}
        self.enums: dict[str, CEnum] = {}
        self.opaque_standard_types: set[str] = set()

    def visit(self, node, **context):
        if isinstance(node, CProject):
            return self.visit_project(node)
        if isinstance(node, CFile):
            return self.visit_file(node, **context)
        if isinstance(node, CFunction):
            return self.visit_function(node)
        if isinstance(node, CParameter):
            return self.visit_parameter(node, position=context.get("position", 0))
        if isinstance(node, CStruct):
            return self.visit_struct(node)
        if isinstance(node, CUnion):
            return self.visit_union(node)
        if isinstance(node, CVariable):
            return self.visit_variable(node)
        if isinstance(node, CType):
            return self.visit_type(node)
        raise TypeError(f"Unsupported C parse object: {type(node)!r}")

    def visit_project(self, project: CProject) -> list[SemanticModule]:
        self.typedefs = dict(project.typedefs)
        self.structs = dict(project.structs)
        self.unions = dict(project.unions)
        self.enums = dict(project.enums)
        return [
            self.visit_file(
                c_file,
                typedefs=self.typedefs,
                structs=self.structs,
                unions=self.unions,
                enums=self.enums,
            )
            for _filename, c_file in sorted(project.files.items())
        ]

    def visit_file(
        self,
        c_file: CFile,
        *,
        typedefs: dict[str, CTypedef] | None = None,
        structs: dict[str, CStruct] | None = None,
        unions: dict[str, CUnion] | None = None,
        enums: dict[str, CEnum] | None = None,
    ) -> SemanticModule:
        previous = self.typedefs, self.structs, self.unions, self.enums
        self.typedefs = typedefs or {typedef.name: typedef for typedef in c_file.typedefs}
        self.structs = structs or {struct.name: struct for struct in c_file.structs if struct.name}
        self.unions = unions or {union.name: union for union in c_file.unions if union.name}
        self.enums = enums or {enum.name: enum for enum in c_file.enums if enum.name}
        try:
            self.opaque_standard_types = set()
            semantic_functions = [self.visit_function(function) for function in c_file.functions]
            semantic_variables = [
                *self._enum_constants(c_file.enums),
                *self._macro_constants(c_file),
                *[self.visit_variable(variable) for variable in c_file.variables],
            ]
            semantic_classes = [
                *[self.visit_struct(struct) for struct in c_file.structs],
                *[self.visit_union(union) for union in c_file.unions],
                *self._opaque_standard_type_classes(),
            ]
            module = SemanticModule(
                name=self._module_name(c_file),
                functions=semantic_functions,
                classes=semantic_classes,
                variables=semantic_variables,
                metadata=self._file_metadata(c_file),
                origin=SemanticOrigin(
                    source_language="c",
                    native_name=c_file.filename,
                    native_scope=c_file.filename,
                    source_kind="translation_unit",
                    metadata={
                        "preprocessing": c_file.preprocessing,
                        "parser_status": c_file.parser_status,
                    },
                ),
            )
            return module
        finally:
            self.typedefs, self.structs, self.unions, self.enums = previous

    def visit_function(self, function: CFunction) -> SemanticFunction:
        arguments = [
            self.visit_parameter(parameter, position=index, owner=function.name)
            for index, parameter in enumerate(function.parameters)
        ]
        metadata: dict[str, Any] = {
            "storage": list(function.storage),
            "specifiers": list(function.specifiers),
            "prototype_style": function.prototype_style,
            "is_definition": function.is_definition,
        }
        blockers = []
        if function.is_variadic:
            blockers.append(
                self._blocker(
                    "c_variadic_function",
                    "Variadic C functions require explicit semantic .pyi policy before wrapping.",
                    {"owner": function.name, "function": function.name},
                )
            )
        if function.prototype_style == "unspecified":
            blockers.append(
                self._blocker(
                    "c_unspecified_function_parameters",
                    "C functions declared without a prototype do not provide complete parameter types.",
                    {"owner": function.name, "function": function.name},
                )
            )
        if blockers:
            metadata["readiness_blockers"] = blockers

        return SemanticFunction(
            name=function.name,
            native_name=function.name,
            arguments=arguments,
            return_type=self._return_type(function.result_type, owner=f"{function.name}.return"),
            projection=[
                ProjectionMapping(
                    python_name=argument.name,
                    native_name=parameter.name or argument.name,
                    native_position=index,
                    python_position=index,
                    intent=argument.intent,
                )
                for index, (parameter, argument) in enumerate(zip(function.parameters, arguments))
            ],
            metadata=metadata,
            visibility="private" if "static" in function.storage else "public",
            origin=SemanticOrigin(
                source_language="c",
                native_name=function.name,
                source_kind="function",
                source_type=self._type_text(function.type),
                source_location=self._location_dict(function.source_location),
            ),
        )

    def visit_parameter(
        self,
        parameter: CParameter,
        *,
        position: int = 0,
        owner: str | None = None,
    ) -> SemanticArgument:
        name = parameter.name or f"arg{position}"
        source_type = parameter.declared_type or parameter.type
        semantic_type = self.visit_type(source_type, owner=f"{owner or '<function>'}.{name}")
        metadata: dict[str, Any] = {"native_position": position}
        blockers = []
        if parameter.callback_candidate:
            semantic_type = self._callback_placeholder(source_type)
        else:
            self._add_incomplete_by_value_blocker(semantic_type, owner=f"{owner}.{name}" if owner else name)
            if self._ambiguous_pointer_argument(semantic_type):
                blockers.append(
                    self._blocker(
                        "c_pointer_ownership_ambiguous",
                        "Mutable C pointer parameters need explicit ownership, scalar-reference, or array policy.",
                        {
                            "owner": f"{owner}.{name}" if owner else name,
                            "parameter": name,
                            "type": self._type_text(source_type),
                        },
                    )
                )
        intent = self._inferred_intent(semantic_type)
        if blockers:
            metadata["readiness_blockers"] = blockers

        return SemanticArgument(
            name=name,
            semantic_type=semantic_type,
            intent=intent,
            metadata=metadata,
            origin=SemanticOrigin(
                source_language="c",
                native_name=parameter.name,
                native_scope=owner,
                source_kind="parameter",
                source_type=self._type_text(source_type),
                source_location=self._location_dict(parameter.source_location),
            ),
        )

    def visit_variable(self, variable: CVariable) -> SemanticArgument:
        name = variable.name or "<anonymous>"
        semantic_type = self.visit_type(variable.type, owner=name)
        self._add_incomplete_by_value_blocker(semantic_type, owner=name)
        if variable.bit_width is not None:
            semantic_type.metadata.setdefault("readiness_blockers", []).append(
                self._blocker(
                    "c_bitfield_unsupported",
                    "C bitfields require explicit semantic policy before wrapping.",
                    {"owner": name, "field": name, "bit_width": variable.bit_width},
                )
            )
        if variable.callback_candidate:
            semantic_type = self._callback_placeholder(variable.type)
        return SemanticArgument(
            name=name,
            semantic_type=semantic_type,
            intent=self._inferred_intent(semantic_type),
            visibility="private" if "static" in variable.storage else "public",
            default_value=variable.initializer.source_text if variable.initializer is not None else None,
            origin=SemanticOrigin(
                source_language="c",
                native_name=variable.name,
                source_kind="variable",
                source_type=self._type_text(variable.type),
                source_location=self._location_dict(variable.source_location),
                metadata={"storage": list(variable.storage), "bit_width": variable.bit_width},
            ),
        )

    def visit_struct(self, struct: CStruct) -> SemanticClass:
        name = self._struct_name(struct)
        metadata: dict[str, Any] = {"c_kind": "struct", "incomplete": struct.is_incomplete}
        base_classes = ["Opaque"] if struct.is_incomplete else []
        return SemanticClass(
            name=name,
            native_name=struct.reference_name,
            fields=[self.visit_variable(member) for member in struct.members if member.name is not None],
            base_classes=base_classes,
            metadata=metadata,
            origin=SemanticOrigin(
                source_language="c",
                native_name=struct.reference_name,
                source_kind="struct",
                source_type=struct.reference_name,
                source_location=self._location_dict(struct.source_location),
            ),
        )

    def visit_union(self, union: CUnion) -> SemanticClass:
        return SemanticClass(
            name=self._union_name(union),
            native_name=union.reference_name,
            fields=[self.visit_variable(member) for member in union.members if member.name is not None],
            metadata={"c_kind": "union", "incomplete": union.is_incomplete},
            origin=SemanticOrigin(
                source_language="c",
                native_name=union.reference_name,
                source_kind="union",
                source_type=union.reference_name,
                source_location=self._location_dict(union.source_location),
            ),
        )

    def visit_type(self, type_: CType, *, owner: str | None = None) -> SemanticType:
        if isinstance(type_, CComposedType):
            return self._composed_type(type_, owner=owner)
        if isinstance(type_, CTypedef):
            return self._typedef_type(type_, owner=owner)
        if isinstance(type_, CStruct):
            return self._struct_type(type_, owner=owner)
        if isinstance(type_, CUnion):
            return self._union_type(type_, owner=owner)
        if isinstance(type_, CEnum):
            return self._enum_type(type_)
        if isinstance(type_, CFunctionType):
            return self._callback_placeholder(type_)
        if isinstance(type_, CUnknownType):
            return self._unresolved_type(type_.spelling, owner=owner, source_type=self._type_text(type_))
        if isinstance(type_, (CLongDouble, CLongDoubleComplex)):
            return self._unsupported_type(
                "c_long_double_unsupported",
                "C long double types are not mapped until target precision policy is explicit.",
                owner=owner,
                source_type=self._type_text(type_),
            )
        if isinstance(type_, CVoid):
            return SemanticType(
                name="Any",
                dtype="Any",
                metadata={"c_void_pointer_pointee": True},
                origin=self._type_origin(type_),
            )

        semantic_name = self.primitive_type_map.get(type(type_))
        if semantic_name is None:
            return self._unsupported_type(
                "c_unsupported_type",
                "This C type is not supported by the semantic converter.",
                owner=owner,
                source_type=self._type_text(type_),
            )

        metadata = self._type_metadata(type_)
        if isinstance(type_, CChar):
            metadata["c_char_policy"] = "implementation-defined signed 8-bit code unit"
        return SemanticType(
            name=semantic_name,
            dtype=semantic_name,
            metadata=metadata,
            origin=self._type_origin(type_),
        )

    def _return_type(self, type_: CType, *, owner: str) -> SemanticType | None:
        if isinstance(type_, CVoid):
            return None
        semantic_type = self.visit_type(type_, owner=owner)
        self._add_incomplete_by_value_blocker(semantic_type, owner=owner)
        return semantic_type

    def _composed_type(self, type_: CComposedType, *, owner: str | None) -> SemanticType:
        components = list(type_.components)
        if not components:
            return self._unsupported_type(
                "c_empty_composed_type",
                "C composed type is missing a base type.",
                owner=owner,
                source_type=self._type_text(type_),
            )
        if self._contains_function_type(type_):
            return self._callback_placeholder(type_)

        leading_arrays = self._leading_components(components, CArray)
        if leading_arrays:
            remaining = components[len(leading_arrays) :]
            if self._has_component(remaining[:-1], CPointer):
                return self._unsupported_type(
                    "c_array_of_pointer_unsupported",
                    "C arrays of pointers need explicit semantic policy.",
                    owner=owner,
                    source_type=self._type_text(type_),
                )
            if not remaining:
                return self._unsupported_type(
                    "c_array_missing_element_type",
                    "C array type is missing an element type.",
                    owner=owner,
                    source_type=self._type_text(type_),
                )
            element = self.visit_type(remaining[-1], owner=owner)
            return self._array_type(element, leading_arrays, source_type=type_, owner=owner)

        leading_pointers = self._leading_components(components, CPointer)
        if leading_pointers:
            remaining = components[len(leading_pointers) :]
            if not remaining:
                return self._unsupported_type(
                    "c_pointer_missing_pointee",
                    "C pointer type is missing a pointee type.",
                    owner=owner,
                    source_type=self._type_text(type_),
                )
            if self._has_component(remaining[:-1], CArray):
                element = self.visit_type(remaining[-1], owner=owner)
                arrays = [component for component in remaining[:-1] if isinstance(component, CArray)]
                semantic_type = self._array_type(element, arrays, source_type=type_, owner=owner)
                semantic_type.storage = semantic_type.storage or SemanticStorageContract(kind="array")
                semantic_type.storage.pointer_depth = len(leading_pointers)
                semantic_type.storage.metadata["c_pointer_to_array"] = True
                return semantic_type
            if len(remaining) != 1:
                return self._unsupported_type(
                    "c_unsupported_composed_type",
                    "This C pointer composition needs explicit semantic policy.",
                    owner=owner,
                    source_type=self._type_text(type_),
                )
            pointee = self.visit_type(remaining[0], owner=owner)
            return self._pointer_type(pointee, leading_pointers, pointee_type=remaining[0], source_type=type_)

        if len(components) == 1:
            return self.visit_type(components[0], owner=owner)
        return self._unsupported_type(
            "c_unsupported_composed_type",
            "This C declarator composition needs explicit semantic policy.",
            owner=owner,
            source_type=self._type_text(type_),
        )

    def _typedef_type(self, typedef: CTypedef, *, owner: str | None) -> SemanticType:
        resolved = self._resolve_typedef(typedef)
        if resolved is not None and resolved is not typedef:
            semantic_type = self.visit_type(resolved.type or resolved, owner=owner)
            semantic_type.metadata.setdefault("c_typedefs", []).append(typedef.name)
            return semantic_type
        if typedef.type is not None:
            semantic_type = self.visit_type(typedef.type, owner=owner)
            semantic_type.metadata.setdefault("c_typedefs", []).append(typedef.name)
            return semantic_type

        standard_type = self._standard_semantic_type(typedef.name)
        if standard_type is not None:
            standard_type.metadata.setdefault("c_typedefs", []).append(typedef.name)
            return standard_type

        return self._unresolved_type(
            typedef.name,
            owner=owner,
            source_type=typedef.name,
            code="c_unresolved_typedef",
            message="C typedef references must resolve to a concrete semantic type before wrapping.",
        )

    def _struct_type(self, struct: CStruct, *, owner: str | None) -> SemanticType:
        if struct.name and struct.name in self.structs:
            struct = self.structs[struct.name]
        name = self._struct_name(struct)
        return SemanticType(
            name=name,
            dtype=name,
            metadata={"c_kind": "struct", "incomplete": struct.is_incomplete},
            origin=self._type_origin(struct, native_name=struct.reference_name),
        )

    def _union_type(self, union: CUnion, *, owner: str | None) -> SemanticType:
        if union.name and union.name in self.unions:
            union = self.unions[union.name]
        name = self._union_name(union)
        semantic_type = SemanticType(
            name=name,
            dtype=name,
            metadata={"c_kind": "union", "incomplete": union.is_incomplete},
            origin=self._type_origin(union, native_name=union.reference_name),
        )
        semantic_type.metadata.setdefault("readiness_blockers", []).append(
            self._blocker(
                "c_union_unsupported",
                "C union arguments and returns require explicit semantic policy before wrapping.",
                {"owner": owner or name, "type": union.reference_name},
            )
        )
        return semantic_type

    def _enum_type(self, enum: CEnum) -> SemanticType:
        return SemanticType(
            name="Int32",
            dtype="Int32",
            metadata={"c_kind": "enum", "c_enum": enum.reference_name},
            origin=self._type_origin(enum, native_name=enum.reference_name),
        )

    def _pointer_type(
        self,
        pointee: SemanticType,
        pointer_components: list[CPointer],
        *,
        pointee_type: CType,
        source_type: CType,
    ) -> SemanticType:
        pointer_depth = len(pointer_components)
        read_only = self._has_qualifier(pointee_type, CConst)
        pointer_qualifiers = [
            [qualifier.spelling for qualifier in pointer.qualifiers]
            for pointer in pointer_components
        ]
        restrict = any(self._has_qualifier(pointer, CRestrict) for pointer in pointer_components)
        pointee.storage = SemanticStorageContract(
            kind="reference" if pointer_depth == 1 else "pointer",
            read_only=read_only,
            mutable=not read_only,
            pointer_depth=pointer_depth,
            ownership="borrowed",
            metadata={
                "c_pointer_qualifiers": pointer_qualifiers,
                "restrict": restrict,
                "source_type": self._type_text(source_type),
            },
        )
        pointee.ownership.mutable = not read_only
        pointee.ownership.aliasing = not restrict
        return pointee

    def _array_type(
        self,
        element: SemanticType,
        array_components: list[CArray],
        *,
        source_type: CType,
        owner: str | None,
    ) -> SemanticType:
        shape = [self._array_bound(component) for component in array_components]
        rank = len(array_components)
        read_only = self._has_qualifier(self._array_element_type(source_type), CConst)
        element.rank = rank
        element.shape = list(shape)
        element.storage = SemanticStorageContract(
            kind="array",
            read_only=read_only,
            mutable=not read_only,
            pointer_depth=1,
            ownership="borrowed",
            array=SemanticArrayContract(
                rank=rank,
                shape=list(shape),
                source_shape=[component.bound or ":" for component in array_components],
                category="c_array",
                order="ORDER_C" if rank > 1 else None,
                axes=["dense" for _component in array_components],
                contiguous=True,
                metadata={
                    "c_static_minimum": [component.is_static_minimum for component in array_components],
                    "c_variable_length": [component.is_variable_length for component in array_components],
                    "c_flexible": [component.is_flexible for component in array_components],
                },
            ),
            metadata={"source_type": self._type_text(source_type)},
        )
        if any(bound == ":" for bound in shape):
            element.metadata.setdefault("readiness_blockers", []).append(
                self._blocker(
                    "c_array_extent_ambiguous",
                    "C array parameters with unknown extents need explicit semantic shape policy.",
                    {"owner": owner or self._type_text(source_type), "type": self._type_text(source_type)},
                )
            )
        return element

    def _enum_constants(self, enums: list[CEnum]) -> list[SemanticArgument]:
        variables: list[SemanticArgument] = []
        for enum in enums:
            next_value: int | None = 0
            for enumerator in enum.constants:
                value = enumerator.value
                if value is None and next_value is not None:
                    value = str(next_value)
                literal = self._integer_literal_value(value)
                next_value = literal + 1 if literal is not None else None
                variables.append(
                    SemanticArgument(
                        name=enumerator.name,
                        semantic_type=SemanticType(
                            name="Int32",
                            dtype="Int32",
                            constraints=[SemanticConstraint("Constant")],
                            metadata={"c_enum": enum.reference_name},
                            origin=SemanticOrigin(
                                source_language="c",
                                native_name=enumerator.name,
                                native_scope=enum.reference_name,
                                source_kind="enum_constant",
                                source_type="enum",
                                source_location=self._location_dict(enumerator.source_location),
                            ),
                        ),
                        default_value=value,
                        origin=SemanticOrigin(
                            source_language="c",
                            native_name=enumerator.name,
                            native_scope=enum.reference_name,
                            source_kind="enum_constant",
                            source_location=self._location_dict(enumerator.source_location),
                        ),
                    )
                )
        return variables

    def _macro_constants(self, c_file: CFile) -> list[SemanticArgument]:
        variables: list[SemanticArgument] = []
        for macro in c_file.macros:
            if macro.function_like or macro.value is None:
                continue
            value = macro.value.strip()
            if _INTEGER_LITERAL_RE.fullmatch(value):
                semantic_name = "Int32"
            elif _FLOAT_LITERAL_RE.fullmatch(value):
                semantic_name = "Float64"
            else:
                continue
            variables.append(
                SemanticArgument(
                    name=macro.name,
                    semantic_type=SemanticType(
                        name=semantic_name,
                        dtype=semantic_name,
                        constraints=[SemanticConstraint("Constant")],
                    ),
                    default_value=value,
                    origin=SemanticOrigin(
                        source_language="c",
                        native_name=macro.name,
                        source_kind="macro",
                        source_location=self._location_dict(macro.source_location),
                    ),
                )
            )
        return variables

    def _file_metadata(self, c_file: CFile) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "source_language": "c",
            "counts": {
                "functions": len(c_file.functions),
                "structs": len(c_file.structs),
                "unions": len(c_file.unions),
                "enums": len(c_file.enums),
                "typedefs": len(c_file.typedefs),
                "macros": len(c_file.macros),
                "includes": len(c_file.includes),
                "diagnostics": len(c_file.diagnostics),
            },
            "preprocessing": c_file.preprocessing,
        }
        blockers = []
        for dependency in c_file.macro_dependencies:
            blockers.append(
                self._blocker(
                    "c_macro_dependent_declaration",
                    "Some C declarations depend on macros that were recorded but not expanded.",
                    {
                        "owner": c_file.filename or "<c-source>",
                        "macro": dependency.name,
                        "context": dependency.context,
                        "source": dependency.source_text,
                    },
                )
            )
        for diagnostic in c_file.diagnostics:
            blocker = self._diagnostic_blocker(diagnostic)
            if blocker is not None:
                blockers.append(blocker)
        if blockers:
            metadata["readiness_blockers"] = blockers
        return metadata

    def _diagnostic_blocker(self, diagnostic: CDiagnostic) -> dict[str, Any] | None:
        if diagnostic.code == "C_MACRO_DEPENDENT_DECLARATION":
            return None
        if diagnostic.severity != "error":
            return None
        return self._blocker(
            self._diagnostic_code(diagnostic.code),
            diagnostic.message,
            {
                "owner": diagnostic.unit_name or diagnostic.unit_kind or "<c-source>",
                "diagnostic_code": diagnostic.code,
                "unit_kind": diagnostic.unit_kind,
                "unit_name": diagnostic.unit_name,
            },
        )

    def _resolve_typedef(self, typedef: CTypedef, stack: tuple[str, ...] = ()) -> CTypedef | None:
        if typedef.type is not None:
            return typedef
        target = self.typedefs.get(typedef.name)
        if target is None or target.name in stack:
            return None
        if target.type is None:
            return self._resolve_typedef(target, (*stack, target.name))
        return target

    def _standard_semantic_type(self, name: str) -> SemanticType | None:
        fact = self.standard_type_facts.get(name)
        if fact is not None:
            if fact.get("available", True) and fact.get("kind") == "opaque_handle":
                semantic_name = self._identifier(name)
                self.opaque_standard_types.add(semantic_name)
                return SemanticType(
                    name=semantic_name,
                    dtype=semantic_name,
                    metadata={"c_standard_type": name, "c_standard_type_fact": dict(fact), "c_opaque_handle": True},
                )
            semantic_name = self._semantic_type_from_standard_fact(fact)
            if semantic_name is not None:
                return SemanticType(
                    name=semantic_name,
                    dtype=semantic_name,
                    metadata={"c_standard_type": name, "c_standard_type_fact": dict(fact)},
                )
        fallback = _STANDARD_TYPE_FALLBACKS.get(name)
        if fallback is None:
            return None
        return SemanticType(
            name=fallback,
            dtype=fallback,
            metadata={"c_standard_type": name, "c_standard_type_fallback": True},
        )

    def _opaque_standard_type_classes(self) -> list[SemanticClass]:
        return [
            SemanticClass(
                name=name,
                native_name=name,
                base_classes=["Opaque"],
                metadata={"c_kind": "opaque_standard_type"},
                origin=SemanticOrigin(
                    source_language="c",
                    native_name=name,
                    source_kind="standard_type",
                    source_type=name,
                ),
            )
            for name in sorted(self.opaque_standard_types)
        ]

    @staticmethod
    def _semantic_type_from_standard_fact(fact: dict[str, Any]) -> str | None:
        if not fact.get("available", True):
            return None
        if fact.get("kind") == "opaque_handle":
            return None
        bits = int(fact.get("bits") or 0)
        if fact.get("kind") == "integer":
            if fact.get("signed") is False:
                return _UNSIGNED_WIDTH_TYPES.get(bits)
            if fact.get("signed") is True:
                return _SIGNED_WIDTH_TYPES.get(bits)
        if fact.get("kind") == "real":
            return {32: "Float32", 64: "Float64"}.get(bits)
        return None

    @staticmethod
    def _standard_type_facts(report: Any | None) -> dict[str, dict[str, Any]]:
        if report is None:
            return {}
        if hasattr(report, "types"):
            types = getattr(report, "types")
        elif isinstance(report, dict) and isinstance(report.get("types"), dict):
            types = report["types"]
        elif isinstance(report, dict):
            types = report
        else:
            return {}
        return {
            str(name): dict(fact)
            for name, fact in types.items()
            if isinstance(fact, dict)
        }

    def _unresolved_type(
        self,
        name: str,
        *,
        owner: str | None,
        source_type: str,
        code: str = "c_unresolved_type",
        message: str = "C type references must resolve before wrapping.",
    ) -> SemanticType:
        return SemanticType(
            name=name,
            dtype=name,
            metadata={
                "readiness_blockers": [
                    self._blocker(code, message, {"owner": owner or name, "type": source_type})
                ]
            },
            origin=SemanticOrigin(source_language="c", source_kind="type", source_type=source_type),
        )

    def _unsupported_type(
        self,
        code: str,
        message: str,
        *,
        owner: str | None,
        source_type: str,
    ) -> SemanticType:
        return SemanticType(
            name="CUnsupported",
            dtype="CUnsupported",
            metadata={
                "readiness_blockers": [
                    self._blocker(code, message, {"owner": owner or source_type, "type": source_type})
                ]
            },
            origin=SemanticOrigin(source_language="c", source_kind="unsupported_type", source_type=source_type),
        )

    def _callback_placeholder(self, type_: CType) -> SemanticType:
        return SemanticType(
            name="CFunctionPointer",
            dtype="CFunctionPointer",
            metadata={"source_type": self._type_text(type_)},
            origin=SemanticOrigin(
                source_language="c",
                source_kind="function_pointer",
                source_type=self._type_text(type_),
            ),
        )

    @staticmethod
    def _blocker(code: str, message: str, item: dict[str, Any]) -> dict[str, Any]:
        return {"code": code, "message": message, "items": [item]}

    @staticmethod
    def _diagnostic_code(code: str) -> str:
        return f"c_{code.lower()}"

    @staticmethod
    def _module_name(c_file: CFile) -> str:
        if c_file.filename:
            stem = Path(c_file.filename).stem
        else:
            stem = "c_module"
        return CToIRConverter._identifier(stem or "c_module")

    @staticmethod
    def _identifier(name: str) -> str:
        text = _IDENTIFIER_RE.sub("_", str(name)).strip("_")
        if not text:
            text = "anonymous"
        if text[:1].isdigit():
            text = f"_{text}"
        return text

    def _struct_name(self, struct: CStruct) -> str:
        if struct.name:
            return self._identifier(struct.name)
        alias = self._typedef_alias_for_type(struct)
        return self._identifier(alias or struct.anonymous_id or "anonymous_struct")

    def _union_name(self, union: CUnion) -> str:
        if union.name:
            return self._identifier(union.name)
        alias = self._typedef_alias_for_type(union)
        return self._identifier(alias or union.anonymous_id or "anonymous_union")

    def _typedef_alias_for_type(self, target: CType) -> str | None:
        for typedef in self.typedefs.values():
            if typedef.type is target:
                return typedef.name
        return None

    @staticmethod
    def _leading_components(components: list[CType], cls: type) -> list:
        out = []
        for component in components:
            if not isinstance(component, cls):
                break
            out.append(component)
        return out

    @staticmethod
    def _has_component(components: list[CType], cls: type) -> bool:
        return any(isinstance(component, cls) for component in components)

    @staticmethod
    def _contains_function_type(type_: CComposedType) -> bool:
        return any(isinstance(component, CFunctionType) for component in type_.components)

    @staticmethod
    def _array_bound(array: CArray) -> str:
        if array.bound:
            return array.bound
        return ":"

    @staticmethod
    def _array_element_type(source_type: CType) -> CType:
        if isinstance(source_type, CComposedType) and source_type.components:
            return source_type.components[-1]
        return source_type

    @staticmethod
    def _has_qualifier(type_: CType, qualifier_type: type[CQualifier]) -> bool:
        return any(isinstance(qualifier, qualifier_type) for qualifier in getattr(type_, "qualifiers", []))

    @staticmethod
    def _inferred_intent(semantic_type: SemanticType) -> str:
        storage = semantic_type.storage
        if storage is None:
            return "in"
        if storage.kind in {"array", "reference", "pointer"} and not storage.read_only:
            return "inout"
        return "in"

    @staticmethod
    def _ambiguous_pointer_argument(semantic_type: SemanticType) -> bool:
        storage = semantic_type.storage
        if storage is None or storage.kind not in {"reference", "pointer"}:
            return False
        if storage.read_only:
            return False
        return semantic_type.name in _NUMERIC_SEMANTIC_TYPES

    def _add_incomplete_by_value_blocker(self, semantic_type: SemanticType, *, owner: str) -> None:
        storage = semantic_type.storage
        if storage is not None and storage.kind in {"reference", "pointer", "array"}:
            return
        if semantic_type.metadata.get("c_kind") != "struct":
            return
        if not semantic_type.metadata.get("incomplete"):
            return
        semantic_type.metadata.setdefault("readiness_blockers", []).append(
            self._blocker(
                "c_incomplete_struct_by_value",
                "Incomplete C structs can only be wrapped through explicit pointer or opaque-handle policy.",
                {"owner": owner, "type": semantic_type.name},
            )
        )

    @staticmethod
    def _integer_literal_value(value: str | None) -> int | None:
        if value is None:
            return None
        cleaned = re.sub(r"[uUlL]+\Z", "", value.strip())
        try:
            return int(cleaned, 0)
        except ValueError:
            return None

    @staticmethod
    def _type_text(type_: CType) -> str:
        source_text = getattr(type_, "source_text", "")
        if source_text:
            return source_text
        if isinstance(type_, (CStruct, CUnion, CEnum, CTypedef)):
            return type_.reference_name
        return type(type_).__name__

    @staticmethod
    def _type_metadata(type_: CType) -> dict[str, Any]:
        qualifiers = [qualifier.spelling for qualifier in getattr(type_, "qualifiers", [])]
        metadata: dict[str, Any] = {"c_type": type(type_).__name__}
        if qualifiers:
            metadata["qualifiers"] = qualifiers
        if any(isinstance(qualifier, CVolatile) for qualifier in getattr(type_, "qualifiers", [])):
            metadata.setdefault("readiness_blockers", []).append(
                CToIRConverter._blocker(
                    "c_volatile_unsupported",
                    "Volatile C types require explicit semantic policy before wrapping.",
                    {"owner": CToIRConverter._type_text(type_), "type": CToIRConverter._type_text(type_)},
                )
            )
        if any(isinstance(qualifier, CAtomic) for qualifier in getattr(type_, "qualifiers", [])):
            metadata.setdefault("readiness_blockers", []).append(
                CToIRConverter._blocker(
                    "c_atomic_unsupported",
                    "Atomic C types require explicit semantic policy before wrapping.",
                    {"owner": CToIRConverter._type_text(type_), "type": CToIRConverter._type_text(type_)},
                )
            )
        return metadata

    @staticmethod
    def _type_origin(type_: CType, *, native_name: str | None = None) -> SemanticOrigin:
        return SemanticOrigin(
            source_language="c",
            native_name=native_name,
            source_kind="type",
            source_type=CToIRConverter._type_text(type_),
            metadata=CToIRConverter._type_metadata(type_),
        )

    @staticmethod
    def _location_dict(location) -> dict[str, Any]:
        if location is None:
            return {}
        return {
            key: value
            for key, value in {
                "filename": location.filename,
                "line": location.line,
                "column": location.column,
                "source_line": location.source_line,
            }.items()
            if value is not None
        }


def c_type_to_semantic_type(
    type_: CType,
    *,
    standard_type_report: Any | None = None,
) -> SemanticType:
    return CToIRConverter(standard_type_report=standard_type_report).visit_type(type_)


def c_parameter_to_semantic_argument(
    parameter: CParameter,
    *,
    position: int = 0,
    standard_type_report: Any | None = None,
) -> SemanticArgument:
    return CToIRConverter(standard_type_report=standard_type_report).visit_parameter(
        parameter,
        position=position,
    )


def c_function_to_semantic_function(
    function: CFunction,
    *,
    standard_type_report: Any | None = None,
) -> SemanticFunction:
    return CToIRConverter(standard_type_report=standard_type_report).visit_function(function)


def c_struct_to_semantic_class(
    struct: CStruct,
    *,
    standard_type_report: Any | None = None,
) -> SemanticClass:
    return CToIRConverter(standard_type_report=standard_type_report).visit_struct(struct)


def c_file_to_semantic_module(
    parsed_file: CFile,
    *,
    standard_type_report: Any | None = None,
) -> SemanticModule:
    return CToIRConverter(standard_type_report=standard_type_report).visit_file(parsed_file)


def c_file_to_semantic_modules(
    parsed_file: CFile,
    *,
    standard_type_report: Any | None = None,
) -> list[SemanticModule]:
    return [c_file_to_semantic_module(parsed_file, standard_type_report=standard_type_report)]


def c_project_to_semantic_modules(
    project: CProject,
    *,
    standard_type_report: Any | None = None,
) -> list[SemanticModule]:
    return CToIRConverter(standard_type_report=standard_type_report).visit_project(project)


__all__ = (
    "CToIRConverter",
    "c_file_to_semantic_module",
    "c_file_to_semantic_modules",
    "c_function_to_semantic_function",
    "c_parameter_to_semantic_argument",
    "c_project_to_semantic_modules",
    "c_struct_to_semantic_class",
    "c_type_to_semantic_type",
)
