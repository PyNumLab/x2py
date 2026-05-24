# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
import re
from collections.abc import Mapping, Sequence
from pathlib import Path

from .lexer import (
    CTopLevelSegment,
    split_top_level_c_source,
    strip_c_comments,
    top_level_partition,
    top_level_split,
    top_level_split_with_offsets,
)
from .models import (
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
    CEnumerator,
    CFile,
    CFloat,
    CFloatComplex,
    CFunction,
    CFunctionType,
    CParameter,
    CParseError,
    CPointer,
    CProject,
    CRestrict,
    CSourceLocation,
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
    CInitializer,
    CLong,
    CLongDouble,
    CLongDoubleComplex,
    CLongLong,
)
from .preprocessor import collect_preprocessor_metadata


_C_SOURCE_SUFFIXES = {".c", ".h"}
_IDENTIFIER_RE = re.compile(r"[A-Za-z_]\w*")
_STORAGE_CLASSES = {"typedef", "extern", "static", "register", "_Thread_local"}
_TYPE_QUALIFIERS = {"const", "restrict", "volatile", "_Atomic"}
_FUNCTION_SPECIFIERS = {"inline", "_Noreturn"}
_TAG_KINDS = {"struct", "union", "enum"}
_UNSUPPORTED_DECLARATION_MARKERS = (
    "__attribute__",
    "__declspec",
    "[[",
    "_Alignas",
    "alignas",
    "_Atomic(",
)
_PRIMITIVE_WORDS = {
    "void",
    "char",
    "short",
    "int",
    "long",
    "float",
    "double",
    "signed",
    "unsigned",
    "_Bool",
    "_Complex",
}
_QUALIFIER_CLASSES = {
    "const": CConst,
    "volatile": CVolatile,
    "restrict": CRestrict,
    "_Atomic": CAtomic,
}
_PRIMITIVE_TYPES = {
    "void": CVoid,
    "_Bool": CBool,
    "char": CChar,
    "signed char": CSignedChar,
    "unsigned char": CUnsignedChar,
    "short": CShort,
    "short int": CShort,
    "signed short": CShort,
    "signed short int": CShort,
    "unsigned short": CUnsignedShort,
    "unsigned short int": CUnsignedShort,
    "int": CInt,
    "signed": CInt,
    "signed int": CInt,
    "unsigned": CUnsignedInt,
    "unsigned int": CUnsignedInt,
    "long": CLong,
    "long int": CLong,
    "signed long": CLong,
    "signed long int": CLong,
    "unsigned long": CUnsignedLong,
    "unsigned long int": CUnsignedLong,
    "long long": CLongLong,
    "long long int": CLongLong,
    "signed long long": CLongLong,
    "signed long long int": CLongLong,
    "unsigned long long": CUnsignedLongLong,
    "unsigned long long int": CUnsignedLongLong,
    "float": CFloat,
    "double": CDouble,
    "long double": CLongDouble,
    "float _Complex": CFloatComplex,
    "_Complex": CDoubleComplex,
    "double _Complex": CDoubleComplex,
    "long double _Complex": CLongDoubleComplex,
}
_PRIMITIVE_TYPE_SIGNATURES = {
    tuple(sorted(spelling.split())): type_class
    for spelling, type_class in _PRIMITIVE_TYPES.items()
}


@dataclass
class _PointerOp:
    qualifiers: list[str]


@dataclass
class _ArrayOp:
    size: str | None = None
    static: bool = False
    qualifiers: list[str] | None = None
    variable_length: bool = False


@dataclass
class _FunctionOp:
    parameters: list[CParameter]
    variadic: bool = False
    prototype_style: str | None = None


@dataclass
class _ParsedDeclarator:
    name: str | None
    operations: list[_PointerOp | _ArrayOp | _FunctionOp]
    source_text: str = ""


class _UnsupportedDeclaratorSyntax(ValueError):
    pass


class _InvalidSpecifierSequence(ValueError):
    pass


def _looks_like_existing_source_path(value: object) -> bool:
    if isinstance(value, Path):
        return value.is_file()
    if not isinstance(value, str) or not value or "\n" in value:
        return False
    try:
        return Path(value).is_file()
    except OSError:
        return False


def _collect_c_paths(path: Path) -> list[Path]:
    return sorted(
        p
        for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in _C_SOURCE_SUFFIXES
    )


class CParser:
    """C parser entrypoint for the currently implemented C subset.

    The implemented subset covers raw preprocessing metadata, recursive
    declarators, aggregate declarations, typedefs, and function signatures.
    """

    def _source_location_at(self, segment: CTopLevelSegment, offset: int) -> CSourceLocation:
        prefix = segment.text[:offset]
        line_offset = prefix.count("\n")
        line = segment.original_start_line + line_offset
        if line_offset:
            column = len(prefix.rsplit("\n", 1)[-1]) + 1
        else:
            column = segment.original_start_column + len(prefix)
        source_line = segment.original_source_line
        if line_offset and line_offset < len(segment.original_source_lines):
            source_line = segment.original_source_lines[line_offset]
        return CSourceLocation(
            filename=segment.filename,
            line=line,
            column=column,
            source_line=source_line,
        )

    def _source_location(self, segment: CTopLevelSegment) -> CSourceLocation:
        return self._source_location_at(segment, 0)

    def _has_unsupported_declaration_marker(self, text: str) -> bool:
        return any(marker in text for marker in _UNSUPPORTED_DECLARATION_MARKERS)

    def _end_location(self, segment: CTopLevelSegment) -> CSourceLocation:
        return CSourceLocation(
            filename=segment.filename,
            line=segment.original_end_line,
            column=segment.original_end_column,
            source_line=segment.original_end_source_line,
        )

    def _last_identifier(self, text: str) -> re.Match[str] | None:
        bracket_depth = 0
        allowed_spans: list[tuple[int, int]] = []
        span_start = 0
        for index, char in enumerate(text):
            if char == "[":
                if bracket_depth == 0 and span_start < index:
                    allowed_spans.append((span_start, index))
                bracket_depth += 1
            elif char == "]" and bracket_depth:
                bracket_depth -= 1
                if bracket_depth == 0:
                    span_start = index + 1
        if bracket_depth == 0 and span_start < len(text):
            allowed_spans.append((span_start, len(text)))

        matches: list[re.Match[str]] = []
        for start, end in allowed_spans:
            matches.extend(_IDENTIFIER_RE.finditer(text, start, end))
        return matches[-1] if matches else None

    def _specifier_words(self, spec_text: str) -> list[str]:
        return _IDENTIFIER_RE.findall(spec_text)

    def _qualifiers(self, spellings: list[str]) -> list:
        return [_QUALIFIER_CLASSES[spelling]() for spelling in spellings]

    def _invalid_specifier_error(
        self,
        segment: CTopLevelSegment,
        message: str,
        *,
        offset: int = 0,
    ) -> CParseError:
        location = self._source_location_at(segment, offset)
        return CParseError(
            message,
            filename=location.filename,
            line_number=location.line,
            column=location.column,
            source_line=location.source_line,
            code="CPARSE003",
        )

    def _parse_specifiers(self, spec_text: str) -> tuple[CType, list[str], list[str]]:
        words = self._specifier_words(spec_text)
        storage: list[str] = []
        qualifiers: list[str] = []
        function_specifiers: list[str] = []
        type_words: list[str] = []

        for word in words:
            if word in _STORAGE_CLASSES:
                storage.append(word)
            elif word in _TYPE_QUALIFIERS:
                qualifiers.append(word)
            elif word in _FUNCTION_SPECIFIERS:
                function_specifiers.append(word)
            else:
                type_words.append(word)

        if type_words and type_words[0] in _TAG_KINDS:
            tag_name = type_words[1] if len(type_words) > 1 else None
            tag_type = {"struct": CStruct, "union": CUnion, "enum": CEnum}[type_words[0]]
            tag_kwargs = {
                "name": tag_name,
                "qualifiers": self._qualifiers(qualifiers),
                "source_text": " ".join([*qualifiers, *type_words]),
            }
            if tag_type in {CStruct, CUnion}:
                tag_kwargs["is_incomplete"] = True
            type_: CType = tag_type(**tag_kwargs)
        elif type_words:
            spelling = " ".join(type_words)
            primitive = _PRIMITIVE_TYPE_SIGNATURES.get(tuple(sorted(type_words)))
            if primitive is not None:
                type_ = primitive(
                    qualifiers=self._qualifiers(qualifiers),
                    source_text=" ".join([*qualifiers, *type_words]),
                )
            elif len(type_words) == 1 and type_words[0] not in _PRIMITIVE_WORDS:
                type_ = CTypedef(
                    name=type_words[0],
                    qualifiers=self._qualifiers(qualifiers),
                    source_text=" ".join([*qualifiers, *type_words]),
                )
            else:
                raise _InvalidSpecifierSequence(
                    f"Invalid type specifier sequence {spelling!r}."
                )
        else:
            type_ = CUnknownType(
                qualifiers=self._qualifiers(qualifiers),
                source_text=spec_text.strip(),
            )

        return type_, storage, function_specifiers

    def _skip_whitespace(self, text: str, index: int) -> int:
        while index < len(text) and text[index].isspace():
            index += 1
        return index

    def _read_identifier(self, text: str, index: int) -> tuple[str, int] | None:
        if index >= len(text):
            return None
        first = text[index]
        if not (first == "_" or first.isalpha()):
            return None
        end = index + 1
        while end < len(text) and (text[end] == "_" or text[end].isalnum()):
            end += 1
        return text[index:end], end

    def _find_matching_delimiter(
        self,
        text: str,
        open_index: int,
        open_char: str,
        close_char: str,
    ) -> int | None:
        depth = 0
        state = "normal"
        quote = ""
        escaped = False
        for index in range(open_index, len(text)):
            char = text[index]
            if state in {"string", "char"}:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    state = "normal"
                    quote = ""
                continue
            if char in {'"', "'"}:
                state = "string" if char == '"' else "char"
                quote = char
                escaped = False
                continue
            if char == open_char:
                depth += 1
            elif char == close_char:
                depth -= 1
                if depth == 0:
                    return index
        return None

    def _split_declaration_specifiers(self, text: str) -> tuple[str, str]:
        index = 0
        spec_end = 0
        consumed_type = False
        consumed_typedef_name = False

        while True:
            index = self._skip_whitespace(text, index)
            identifier = self._read_identifier(text, index)
            if identifier is None:
                break
            word, end = identifier

            if word in _STORAGE_CLASSES or word in _TYPE_QUALIFIERS or word in _FUNCTION_SPECIFIERS:
                index = end
                spec_end = end
                continue

            if word in _PRIMITIVE_WORDS:
                consumed_type = True
                index = end
                spec_end = end
                continue

            if word in _TAG_KINDS:
                consumed_type = True
                index = self._skip_whitespace(text, end)
                tag_identifier = self._read_identifier(text, index)
                if tag_identifier is not None:
                    _tag_name, index = tag_identifier
                spec_end = index
                continue

            if not consumed_type and not consumed_typedef_name:
                consumed_type = True
                consumed_typedef_name = True
                index = end
                spec_end = end
                continue

            break

        return text[:spec_end].strip(), text[spec_end:].strip()

    def _parse_pointer_ops(
        self,
        text: str,
        index: int,
    ) -> tuple[list[_PointerOp], int]:
        pointers: list[_PointerOp] = []
        index = self._skip_whitespace(text, index)
        while index < len(text) and text[index] == "*":
            index += 1
            qualifiers: list[str] = []
            while True:
                index = self._skip_whitespace(text, index)
                identifier = self._read_identifier(text, index)
                if identifier is None:
                    break
                word, end = identifier
                if word not in _TYPE_QUALIFIERS:
                    break
                qualifiers.append(word)
                index = end
            pointers.append(_PointerOp(qualifiers=qualifiers))
            index = self._skip_whitespace(text, index)
        return pointers, index

    def _parse_array_op(self, content: str) -> _ArrayOp:
        words = content.strip().split()
        qualifiers: list[str] = []
        is_static = False
        remaining: list[str] = []
        for word in words:
            if word == "static":
                is_static = True
            elif word in _TYPE_QUALIFIERS:
                qualifiers.append(word)
            else:
                remaining.append(word)
        normalized = " ".join(remaining)
        variable_length = normalized == "*"
        return _ArrayOp(
            size=None if variable_length else normalized or None,
            static=is_static,
            qualifiers=qualifiers,
            variable_length=variable_length,
        )

    def _parse_declarator_suffixes(
        self,
        text: str,
        index: int,
    ) -> tuple[list[_ArrayOp | _FunctionOp], int]:
        operations: list[_ArrayOp | _FunctionOp] = []
        while True:
            index = self._skip_whitespace(text, index)
            if index >= len(text):
                return operations, index

            if text[index] == "[":
                close_index = self._find_matching_delimiter(text, index, "[", "]")
                if close_index is None:
                    return operations, index
                operations.append(self._parse_array_op(text[index + 1 : close_index]))
                index = close_index + 1
                continue

            if text[index] == "(":
                close_index = self._find_matching_delimiter(text, index, "(", ")")
                if close_index is None:
                    return operations, index
                parameters_text = text[index + 1 : close_index]
                parameters, variadic = self._parse_parameters(parameters_text)
                operations.append(
                    _FunctionOp(
                        parameters=parameters,
                        variadic=variadic,
                        prototype_style=self._prototype_style(parameters_text),
                    )
                )
                index = close_index + 1
                continue

            return operations, index

    def _parse_direct_declarator_at(
        self,
        text: str,
        index: int,
    ) -> tuple[str | None, list[_PointerOp | _ArrayOp | _FunctionOp], int]:
        index = self._skip_whitespace(text, index)
        if index < len(text) and text[index] == "(":
            close_index = self._find_matching_delimiter(text, index, "(", ")")
            if close_index is None:
                return None, [], index
            inner = self._parse_declarator(text[index + 1 : close_index])
            suffixes, index = self._parse_declarator_suffixes(text, close_index + 1)
            return inner.name, [*reversed(suffixes), *inner.operations], index

        identifier = self._read_identifier(text, index)
        if identifier is None:
            suffixes, index = self._parse_declarator_suffixes(text, index)
            return None, list(reversed(suffixes)), index

        name, index = identifier
        suffixes, index = self._parse_declarator_suffixes(text, index)
        return name, list(reversed(suffixes)), index

    def _parse_declarator_at(
        self,
        text: str,
        index: int,
    ) -> tuple[str | None, list[_PointerOp | _ArrayOp | _FunctionOp], int]:
        pointers, index = self._parse_pointer_ops(text, index)
        name, direct_operations, index = self._parse_direct_declarator_at(text, index)
        return name, [*pointers, *direct_operations], index

    def _parse_declarator(self, text: str) -> _ParsedDeclarator:
        stripped = text.strip()
        if not stripped:
            return _ParsedDeclarator(name=None, operations=[], source_text="")
        name, operations, index = self._parse_declarator_at(stripped, 0)
        remainder = stripped[self._skip_whitespace(stripped, index) :].strip()
        if remainder:
            raise _UnsupportedDeclaratorSyntax(
                f"Unsupported declarator syntax after parsed type layers: {remainder!r}."
            )
        return _ParsedDeclarator(name=name, operations=operations, source_text=stripped)

    def _prepend_component(self, component: CType, current: CType) -> CComposedType:
        if isinstance(current, CComposedType):
            return CComposedType(
                components=[component, *current.components],
                source_text=current.source_text,
            )
        return CComposedType(components=[component, current], source_text=current.source_text)

    def _apply_pointer_operation(self, current: CType, operation: _PointerOp) -> CType:
        return self._prepend_component(
            CPointer(qualifiers=self._qualifiers(operation.qualifiers)),
            current,
        )

    def _apply_array_operation(self, current: CType, operation: _ArrayOp) -> CType:
        array = CArray(
            bound=operation.size,
            is_static_minimum=operation.static,
            qualifiers=self._qualifiers(operation.qualifiers or []),
            is_variable_length=operation.variable_length,
        )
        return self._prepend_component(array, current)

    def _apply_function_operation(self, current: CType, operation: _FunctionOp) -> CType:
        return CFunctionType(
            result_type=current,
            parameter_types=[parameter.type for parameter in operation.parameters],
            is_variadic=operation.variadic,
            prototype_style=operation.prototype_style,
            source_text=current.source_text,
        )

    def _apply_declarator_operations(
        self,
        base_type: CType,
        operations: list[_PointerOp | _ArrayOp | _FunctionOp],
    ) -> CType:
        current = base_type
        for operation in operations:
            if isinstance(operation, _PointerOp):
                current = self._apply_pointer_operation(current, operation)
            elif isinstance(operation, _ArrayOp):
                current = self._apply_array_operation(current, operation)
            else:
                current = self._apply_function_operation(current, operation)
        return current

    def _build_declared_type(
        self,
        spec_text: str,
        declarator_fragment: str = "",
    ) -> tuple[str | None, CType, list[str], list[str], _FunctionOp | None]:
        base_type, storage, function_specifiers = self._parse_specifiers(spec_text)
        parsed = self._parse_declarator(declarator_fragment)
        type_ = self._apply_declarator_operations(base_type, parsed.operations)
        source_parts = [spec_text.strip(), declarator_fragment.strip()]
        type_.source_text = " ".join(part for part in source_parts if part).strip()
        direct_function = (
            parsed.operations[-1]
            if parsed.operations and isinstance(parsed.operations[-1], _FunctionOp)
            else None
        )
        return parsed.name, type_, storage, function_specifiers, direct_function

    def _build_type(
        self,
        spec_text: str,
        declarator_fragment: str = "",
    ) -> tuple[CType, list[str]]:
        _name, type_, _storage, function_specifiers, _direct_function = self._build_declared_type(
            spec_text,
            declarator_fragment,
        )
        return type_, function_specifiers

    def _parse_parameter(self, text: str) -> CParameter | None:
        stripped = text.strip()
        if not stripped or stripped == "void":
            return None
        spec_text, declarator = self._split_declaration_specifiers(stripped)
        if not spec_text:
            return None
        name, type_, _storage, _function_specifiers, _direct_function = self._build_declared_type(
            spec_text,
            declarator,
        )
        return CParameter(
            name=name,
            type=type_,
            declared_type=type_,
        )

    def _find_parameter_list(self, text: str) -> tuple[int, int] | None:
        close_index = len(text) - 1
        while close_index >= 0 and text[close_index].isspace():
            close_index -= 1
        if close_index < 0 or text[close_index] != ")":
            return None

        depth = 0
        state = "normal"
        quote = ""
        escaped = False
        for index in range(close_index, -1, -1):
            char = text[index]
            if state in {"string", "char"}:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    state = "normal"
                    quote = ""
                continue
            if char in {'"', "'"}:
                state = "string" if char == '"' else "char"
                quote = char
                escaped = False
                continue
            if char == ")":
                depth += 1
            elif char == "(":
                depth -= 1
                if depth == 0:
                    return index, close_index
        return None

    def _parse_parameters(self, parameters_text: str) -> tuple[list[CParameter], bool]:
        stripped = parameters_text.strip()
        if not stripped or stripped == "void":
            return [], False

        parameters: list[CParameter] = []
        variadic = False
        for item in top_level_split(stripped, ","):
            if item == "...":
                variadic = True
                continue
            parameter = self._parse_parameter(item)
            if parameter is not None:
                parameters.append(parameter)
        return parameters, variadic

    def _is_knr_definition(self, segment: CTopLevelSegment, parameters_text: str) -> bool:
        if segment.terminator != "block":
            return False
        stripped = parameters_text.strip()
        if not stripped or stripped == "void" or "..." in stripped:
            return False
        for item in top_level_split(stripped, ","):
            if not re.fullmatch(r"[A-Za-z_]\w*", item.strip()):
                return False
        return True

    def _raise_for_unsupported_old_style_definitions(
        self,
        source: str,
        filename: str | None,
    ) -> None:
        source_lines = source.splitlines()
        stripped_lines = strip_c_comments(source).splitlines()

        for index, line in enumerate(stripped_lines):
            text = line.strip()
            parameter_bounds = self._find_parameter_list(text)
            if parameter_bounds is None:
                continue
            open_index, close_index = parameter_bounds
            before_parameters = text[:open_index].strip()
            name_match = self._last_identifier(before_parameters)
            if name_match is None:
                continue
            return_spec = before_parameters[: name_match.start()].strip()
            if not return_spec or "(" in return_spec or ")" in return_spec:
                continue

            parameters_text = text[open_index + 1 : close_index].strip()
            if not parameters_text or parameters_text == "void":
                continue

            parameters = [part.strip() for part in parameters_text.split(",")]
            if not parameters or not all(re.fullmatch(r"[A-Za-z_]\w*", part) for part in parameters):
                continue

            saw_old_style_declaration = False
            for follow in stripped_lines[index + 1 :]:
                stripped = follow.strip()
                if not stripped:
                    continue
                if stripped.startswith("{"):
                    source_line = source_lines[index] if index < len(source_lines) else line
                    raise CParseError(
                        "K&R style function definitions are not supported",
                        filename=filename,
                        line_number=index + 1,
                        column=max(line.find(name_match.group(0)) + 1, 1),
                        source_line=source_line,
                        code="CPARSE002",
                    )
                if stripped.endswith(";"):
                    saw_old_style_declaration = True
                    continue
                break

            if saw_old_style_declaration:
                source_line = source_lines[index] if index < len(source_lines) else line
                raise CParseError(
                    "K&R style function definitions are not supported",
                    filename=filename,
                    line_number=index + 1,
                    column=max(line.find(name_match.group(0)) + 1, 1),
                    source_line=source_line,
                    code="CPARSE002",
                )

    def _prototype_style(self, parameters_text: str) -> str:
        return "unspecified" if not parameters_text.strip() else "prototype"

    def _parse_function(self, segment: CTopLevelSegment) -> CFunction | None:
        text = segment.text.strip()
        if text.startswith(("typedef ", "_Static_assert")) or self._has_unsupported_declaration_marker(text):
            return None

        spec_text, declarator = self._split_declaration_specifiers(text)
        if not spec_text or not declarator:
            return None
        try:
            name, function_type, storage, function_specifiers, direct_function = self._build_declared_type(
                spec_text,
                declarator,
            )
        except _InvalidSpecifierSequence as error:
            raise self._invalid_specifier_error(segment, str(error)) from None
        if name is None or not isinstance(function_type, CFunctionType) or direct_function is None:
            return None
        parameter_bounds = self._find_parameter_list(text)
        if parameter_bounds is not None:
            open_index, close_index = parameter_bounds
            parameters_text = text[open_index + 1 : close_index]
            if "(" not in text[:open_index] and self._is_knr_definition(segment, parameters_text):
                raise CParseError(
                    "K&R style function definitions are not supported",
                    filename=segment.filename,
                    line_number=segment.original_start_line,
                    column=segment.original_start_column,
                    source_line=segment.original_source_line,
                    code="CPARSE002",
                )
        return self._function_from_type(
            name,
            function_type,
            direct_function.parameters,
            storage,
            function_specifiers,
            segment,
        )

    def _function_from_type(
        self,
        name: str,
        function_type: CFunctionType,
        parameters: list[CParameter],
        storage: list[str],
        function_specifiers: list[str],
        segment: CTopLevelSegment,
    ) -> CFunction:
        return CFunction(
            name=name,
            result_type=function_type.result_type,
            parameters=list(parameters),
            storage=list(storage),
            specifiers=function_specifiers,
            is_variadic=function_type.is_variadic,
            is_definition=segment.terminator == "block",
            prototype_style=function_type.prototype_style,
            source_location=self._source_location(segment),
            start=self._source_location(segment),
            end=self._end_location(segment) if segment.terminator == "block" else None,
        )

    def _anonymous_tag_id(self, kind: str, segment: CTopLevelSegment) -> str:
        filename = segment.filename or "<source>"
        return f"{kind}@{filename}:{segment.original_start_line}:{segment.original_start_column}"

    def _tag_definition_header(self, text: str) -> tuple[str, list[str], str | None] | None:
        words = self._specifier_words(text)
        for index, word in enumerate(words):
            if word not in _TAG_KINDS:
                continue
            prefix = words[:index]
            suffix = words[index + 1 :]
            if any(item not in _STORAGE_CLASSES | _TYPE_QUALIFIERS for item in prefix):
                return None
            if len(suffix) > 1:
                return None
            return word, prefix, suffix[0] if suffix else None
        return None

    def _forward_tag(self, segment: CTopLevelSegment) -> CStruct | CUnion | None:
        words = self._specifier_words(segment.text.strip())
        if len(words) != 2 or words[0] not in {"struct", "union"}:
            return None
        if words[0] == "struct":
            return CStruct(
                name=words[1],
                is_incomplete=True,
                source_location=self._source_location(segment),
            )
        return CUnion(
            name=words[1],
            is_incomplete=True,
            source_location=self._source_location(segment),
        )

    def _use_aggregate_definition(
        self,
        type_: CType,
        aggregate: CStruct | CUnion | CEnum,
    ) -> CType:
        if isinstance(type_, CComposedType):
            terminal = type_.components[-1]
            if isinstance(terminal, (CStruct, CUnion, CEnum)) and not terminal.qualifiers:
                type_.components[-1] = aggregate
            return type_
        if isinstance(type_, (CStruct, CUnion, CEnum)) and not type_.qualifiers:
            return aggregate
        return type_

    def _declarations_from_declarators(
        self,
        spec_text: str,
        declarator_list: str,
        segment: CTopLevelSegment,
        *,
        resolved: CStruct | CUnion | CEnum | None = None,
    ) -> tuple[list[CFunction], list[CTypedef], list[CVariable], list[CDiagnostic]]:
        functions: list[CFunction] = []
        typedefs: list[CTypedef] = []
        variables: list[CVariable] = []
        diagnostics: list[CDiagnostic] = []

        for declarator in top_level_split(declarator_list, ","):
            declaration, initializer = top_level_partition(declarator, "=")
            try:
                name, type_, storage, function_specifiers, direct_function = self._build_declared_type(
                    spec_text,
                    declaration,
                )
            except _InvalidSpecifierSequence as error:
                raise self._invalid_specifier_error(segment, str(error)) from None
            except _UnsupportedDeclaratorSyntax as error:
                diagnostics.append(self._declarator_diagnostic(segment, str(error)))
                continue
            if not name:
                continue
            if resolved is not None:
                type_ = self._use_aggregate_definition(type_, resolved)
            location = self._source_location(segment)
            if "typedef" in storage:
                typedefs.append(CTypedef(name=name, type=type_, source_location=location))
            elif isinstance(type_, CFunctionType) and direct_function is not None:
                functions.append(
                    self._function_from_type(
                        name,
                        type_,
                        direct_function.parameters,
                        storage,
                        function_specifiers,
                        segment,
                    )
                )
            else:
                variables.append(
                    CVariable(
                        name=name,
                        type=type_,
                        storage=storage,
                        initializer=CInitializer(initializer) if initializer is not None else None,
                        source_location=location,
                    )
                )

        return functions, typedefs, variables, diagnostics

    def _declarator_diagnostic(self, segment: CTopLevelSegment, message: str) -> CDiagnostic:
        return CDiagnostic(
            code="C_UNSUPPORTED_DECLARATOR",
            message=message,
            severity="warning",
            location=self._source_location(segment),
            unit_kind="declarator",
            unit_name=None,
        )

    def _field_diagnostic(
        self,
        segment: CTopLevelSegment,
        owner_kind: str,
        message: str,
        *,
        offset: int = 0,
    ) -> CDiagnostic:
        return CDiagnostic(
            code="C_UNSUPPORTED_FIELD_DECLARATION",
            message=message,
            severity="warning",
            location=self._source_location_at(segment, offset),
            unit_kind=f"{owner_kind}_field",
            unit_name=None,
        )

    def _incomplete_array_component(self, type_: CType) -> CArray | None:
        components = type_.components if isinstance(type_, CComposedType) else [type_]
        if not components or not isinstance(components[0], CArray):
            return None
        array = components[0]
        if array.bound is None and not array.is_variable_length:
            return array
        return None

    def _validate_flexible_members(
        self,
        members: list[CVariable],
        owner_kind: str,
    ) -> list[CDiagnostic]:
        diagnostics: list[CDiagnostic] = []
        named_members = sum(member.name is not None for member in members)
        for index, member in enumerate(members):
            array = self._incomplete_array_component(member.type)
            if array is None:
                continue
            if owner_kind == "struct" and index == len(members) - 1 and named_members > 1:
                array.is_flexible = True
                continue
            if owner_kind == "union":
                message = "A union member cannot be a flexible array member."
            elif index != len(members) - 1:
                message = "A flexible array member must be the final member of a struct."
            else:
                message = "A flexible array member requires a preceding named struct member."
            diagnostics.append(
                CDiagnostic(
                    code="C_INVALID_FLEXIBLE_ARRAY_MEMBER",
                    message=message,
                    severity="error",
                    location=member.source_location,
                    unit_kind=f"{owner_kind}_field",
                    unit_name=member.name,
                )
            )
        return diagnostics

    def _parse_fields(
        self,
        body: str,
        segment: CTopLevelSegment,
        owner_kind: str,
        *,
        body_offset: int,
    ) -> tuple[list[CVariable], list[CDiagnostic]]:
        members: list[CVariable] = []
        diagnostics: list[CDiagnostic] = []
        for text, field_offset in top_level_split_with_offsets(body, ";"):
            member_offset = body_offset + field_offset
            member_location = self._source_location_at(segment, member_offset)
            if self._has_unsupported_declaration_marker(text):
                diagnostics.append(
                    self._field_diagnostic(
                        segment,
                        owner_kind,
                        "Declaration attributes and alignment specifiers are not supported in fields yet.",
                        offset=member_offset,
                    )
                )
                continue
            if "{" in text or "}" in text:
                diagnostics.append(
                    self._field_diagnostic(
                        segment,
                        owner_kind,
                        "Nested aggregate field definitions are not supported yet.",
                        offset=member_offset,
                    )
                )
                continue
            spec_text, declarator_list = self._split_declaration_specifiers(text)
            if not spec_text or not declarator_list:
                diagnostics.append(
                    self._field_diagnostic(
                        segment,
                        owner_kind,
                        "Unsupported field declaration.",
                        offset=member_offset,
                    )
                )
                continue
            for declarator in top_level_split(declarator_list, ","):
                declaration, _initializer = top_level_partition(declarator, "=")
                declaration, bit_width = top_level_partition(declaration, ":")
                try:
                    name, type_, _storage, _function_specifiers, _direct_function = self._build_declared_type(
                        spec_text,
                        declaration,
                    )
                except _InvalidSpecifierSequence as error:
                    raise self._invalid_specifier_error(segment, str(error), offset=member_offset) from None
                except _UnsupportedDeclaratorSyntax as error:
                    diagnostics.append(
                        self._field_diagnostic(segment, owner_kind, str(error), offset=member_offset)
                    )
                    continue
                if name is None and bit_width is None:
                    diagnostics.append(
                        self._field_diagnostic(
                            segment,
                            owner_kind,
                            "Unnamed field type is not supported.",
                            offset=member_offset,
                        )
                    )
                    continue
                members.append(
                    CVariable(
                        name=name,
                        type=type_,
                        source_location=member_location,
                        bit_width=bit_width,
                    )
                )
        diagnostics.extend(self._validate_flexible_members(members, owner_kind))
        return members, diagnostics

    def _parse_enumerators(self, body: str, segment: CTopLevelSegment) -> list[CEnumerator]:
        constants: list[CEnumerator] = []
        for item in top_level_split(body, ","):
            name_text, value = top_level_partition(item, "=")
            identifier = self._read_identifier(name_text.strip(), 0)
            if identifier is None:
                continue
            name, end = identifier
            if name_text[end:].strip():
                continue
            constants.append(
                CEnumerator(
                    name=name,
                    value=value,
                    source_location=self._source_location(segment),
                )
            )
        return constants

    def _parse_tag_definition(
        self,
        segment: CTopLevelSegment,
    ) -> tuple[
        CStruct | CUnion | CEnum,
        list[CFunction],
        list[CTypedef],
        list[CVariable],
        list[CDiagnostic],
    ] | None:
        text = segment.text.strip()
        if self._has_unsupported_declaration_marker(text):
            return None
        open_index = text.find("{")
        if open_index < 0:
            return None
        close_index = self._find_matching_delimiter(text, open_index, "{", "}")
        if close_index is None:
            return None

        header = self._tag_definition_header(text[:open_index].strip())
        if header is None:
            return None
        kind, prefix, tag_name = header
        body = text[open_index + 1 : close_index]
        declarators = text[close_index + 1 :].strip()
        location = self._source_location(segment)
        anonymous_id = None if tag_name else self._anonymous_tag_id(kind, segment)
        diagnostics: list[CDiagnostic] = []

        if kind == "enum":
            aggregate: CStruct | CUnion | CEnum = CEnum(
                name=tag_name,
                constants=self._parse_enumerators(body, segment),
                anonymous_id=anonymous_id,
                source_location=location,
            )
        else:
            members, diagnostics = self._parse_fields(
                body,
                segment,
                kind,
                body_offset=open_index + 1,
            )
            if kind == "struct":
                aggregate = CStruct(
                    name=tag_name,
                    members=members,
                    anonymous_id=anonymous_id,
                    source_location=location,
                )
            else:
                aggregate = CUnion(
                    name=tag_name,
                    members=members,
                    anonymous_id=anonymous_id,
                    source_location=location,
                )

        functions: list[CFunction] = []
        typedefs: list[CTypedef] = []
        variables: list[CVariable] = []
        if declarators:
            spec_text = " ".join([*prefix, kind, *([tag_name] if tag_name else [])])
            functions, typedefs, variables, declarator_diagnostics = self._declarations_from_declarators(
                spec_text,
                declarators,
                segment,
                resolved=aggregate,
            )
            diagnostics.extend(declarator_diagnostics)
        elif "typedef" in prefix:
            diagnostics.append(
                CDiagnostic(
                    code="C_UNSUPPORTED_DECLARATION",
                    message="Typedef aggregate definition has no alias declarator.",
                    severity="warning",
                    location=location,
                    unit_kind=f"{kind}_typedef",
                    unit_name=tag_name,
                )
            )

        return aggregate, functions, typedefs, variables, diagnostics

    def _parse_declaration(
        self,
        segment: CTopLevelSegment,
    ) -> tuple[list[CFunction], list[CTypedef], list[CVariable], list[CDiagnostic]]:
        text = segment.text.strip()
        if (
            not text
            or "{" in text
            or "}" in text
            or text.startswith("_Static_assert")
            or self._has_unsupported_declaration_marker(text)
        ):
            return [], [], [], []

        spec_text, declarator_list = self._split_declaration_specifiers(text)
        if not spec_text or not declarator_list:
            return [], [], [], []

        return self._declarations_from_declarators(spec_text, declarator_list, segment)

    def _unsupported_declaration_diagnostic(self, segment: CTopLevelSegment) -> CDiagnostic | None:
        text = segment.text.strip()
        if not text:
            return None

        kind = "unsupported_declaration"
        message = "Unsupported C declaration form."

        if text.startswith("struct "):
            kind = "struct_definition"
            message = "Struct definitions are not supported yet."
        elif text.startswith("union "):
            kind = "union_definition"
            message = "Union definitions are not supported yet."
        elif text.startswith("enum "):
            kind = "enum_definition"
            message = "Enum definitions are not supported yet."
        elif text.startswith("_Static_assert"):
            kind = "static_assert"
            message = "Static assertions are recorded but not evaluated."
        elif "__attribute__" in text or "__declspec" in text or "[[" in text:
            kind = "attribute_declaration"
            message = "Compiler-specific declaration attributes are not supported yet."
        elif "_Alignas" in text or "alignas" in text:
            kind = "alignment_declaration"
            message = "Declaration alignment specifiers are not supported yet."
        elif "_Atomic(" in text:
            kind = "atomic_type_declaration"
            message = "_Atomic(type) declarations are not supported yet."

        return CDiagnostic(
            code="C_UNSUPPORTED_DECLARATION",
            message=message,
            severity="warning",
            location=self._source_location(segment),
            unit_kind=kind,
            unit_name=None,
        )

    def _parse_translation_unit(
        self,
        source: str,
        filename: str | None,
    ) -> tuple[
        list[CFunction],
        list[CStruct],
        list[CUnion],
        list[CEnum],
        list[CTypedef],
        list[CVariable],
        list[CDiagnostic],
    ]:
        self._raise_for_unsupported_old_style_definitions(source, filename)

        functions: list[CFunction] = []
        structs: list[CStruct] = []
        unions: list[CUnion] = []
        enums: list[CEnum] = []
        typedefs: list[CTypedef] = []
        variables: list[CVariable] = []
        diagnostics: list[CDiagnostic] = []

        for segment in split_top_level_c_source(source, filename=filename):
            tag_definition = self._parse_tag_definition(segment)
            if tag_definition is not None:
                aggregate, parsed_functions, parsed_typedefs, parsed_variables, parsed_diagnostics = tag_definition
                if isinstance(aggregate, CStruct):
                    structs.append(aggregate)
                elif isinstance(aggregate, CUnion):
                    unions.append(aggregate)
                else:
                    enums.append(aggregate)
                functions.extend(parsed_functions)
                typedefs.extend(parsed_typedefs)
                variables.extend(parsed_variables)
                diagnostics.extend(parsed_diagnostics)
                continue
            if segment.terminator != ";":
                try:
                    function = self._parse_function(segment)
                except _UnsupportedDeclaratorSyntax as error:
                    diagnostics.append(self._declarator_diagnostic(segment, str(error)))
                    continue
                if function is not None:
                    functions.append(function)
                    continue
                unsupported = self._unsupported_declaration_diagnostic(segment)
                if unsupported is not None:
                    diagnostics.append(unsupported)
                continue
            forward_tag = self._forward_tag(segment)
            if isinstance(forward_tag, CStruct):
                structs.append(forward_tag)
                continue
            if isinstance(forward_tag, CUnion):
                unions.append(forward_tag)
                continue
            parsed_functions, parsed_typedefs, parsed_variables, declarator_diagnostics = self._parse_declaration(
                segment
            )
            functions.extend(parsed_functions)
            typedefs.extend(parsed_typedefs)
            variables.extend(parsed_variables)
            diagnostics.extend(declarator_diagnostics)
            if (
                not parsed_functions
                and not parsed_typedefs
                and not parsed_variables
                and not declarator_diagnostics
            ):
                unsupported = self._unsupported_declaration_diagnostic(segment)
                if unsupported is not None:
                    diagnostics.append(unsupported)

        return functions, structs, unions, enums, typedefs, variables, diagnostics

    def _build_project(self, parsed_files: dict[str, CFile]) -> CProject:
        project = CProject(files=parsed_files)
        for file in parsed_files.values():
            for function in file.functions:
                project.functions[function.name] = function
            for struct in file.structs:
                if struct.name is not None:
                    project.structs[struct.name] = struct
            for union in file.unions:
                if union.name is not None:
                    project.unions[union.name] = union
            for enum in file.enums:
                if enum.name is not None:
                    project.enums[enum.name] = enum
            for typedef in file.typedefs:
                project.typedefs[typedef.name] = typedef
            for variable in file.variables:
                project.variables[variable.name] = variable
            for macro in file.macros:
                project.macros[macro.name] = macro
            for include in file.includes:
                project.includes[f"{file.filename or ''}:{include.target}"] = include
        return project

    def visit_file(
        self,
        source_or_path: str | Path,
        filename: str | None = None,
        *,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        include_dirs: Sequence[str | Path] | None = None,
        preprocessing: str = "raw",
        encoding: str = "utf-8",
    ) -> CFile:
        del macro_defines
        if _looks_like_existing_source_path(source_or_path):
            path = Path(source_or_path)
            if filename is None:
                filename = str(path)
            source = path.read_text(encoding=encoding)
        else:
            source = str(source_or_path)

        parsed = CFile(filename=filename, parser_status="partial", preprocessing=preprocessing)
        if preprocessing == "raw":
            metadata = collect_preprocessor_metadata(
                source,
                filename=filename,
                include_dirs=include_dirs,
            )
            parsed.includes = metadata.includes
            parsed.macros = metadata.macros
            parsed.diagnostics = metadata.diagnostics
            functions, structs, unions, enums, typedefs, variables, parser_diagnostics = self._parse_translation_unit(
                source,
                filename,
            )
            parsed.functions = functions
            parsed.structs = structs
            parsed.unions = unions
            parsed.enums = enums
            parsed.typedefs = typedefs
            parsed.variables = variables
            parsed.diagnostics.extend(parser_diagnostics)
        return parsed

    def visit_project(
        self,
        files: Mapping[str, str] | Sequence[str | Path] | str | Path,
        *,
        include_dirs: Sequence[str | Path] | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        preprocessing: str = "raw",
        encoding: str = "utf-8",
    ) -> CProject:
        if isinstance(files, Mapping):
            parsed_files = {
                name: self.visit_file(
                    source,
                    filename=name,
                    include_dirs=include_dirs,
                    macro_defines=macro_defines,
                    preprocessing=preprocessing,
                    encoding=encoding,
                )
                for name, source in files.items()
            }
            return self._build_project(parsed_files)

        paths: list[Path] = []
        root: Path | None = None
        if isinstance(files, (str, Path)):
            path = Path(files)
            if path.is_dir():
                root = path
                paths = _collect_c_paths(path)
            else:
                paths = [path]
        else:
            paths = [Path(p) for p in files]

        parsed_files: dict[str, CFile] = {}
        for path in sorted(paths):
            key = path.name if root is not None else str(path)
            if root is not None:
                key = str(path.relative_to(root))
            parsed_files[key] = self.visit_file(
                path,
                filename=key,
                include_dirs=include_dirs,
                macro_defines=macro_defines,
                preprocessing=preprocessing,
                encoding=encoding,
            )
        return self._build_project(parsed_files)


_DEFAULT_PARSER = CParser()


def parse_c_file(
    source_or_path: str | Path,
    filename: str | None = None,
    *,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    include_dirs: Sequence[str | Path] | None = None,
    preprocessing: str = "raw",
    encoding: str = "utf-8",
) -> CFile:
    return _DEFAULT_PARSER.visit_file(
        source_or_path,
        filename=filename,
        macro_defines=macro_defines,
        include_dirs=include_dirs,
        preprocessing=preprocessing,
        encoding=encoding,
    )


def parse_c_project(
    files: Mapping[str, str] | Sequence[str | Path] | str | Path,
    *,
    include_dirs: Sequence[str | Path] | None = None,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    preprocessing: str = "raw",
    encoding: str = "utf-8",
) -> CProject:
    return _DEFAULT_PARSER.visit_project(
        files,
        include_dirs=include_dirs,
        macro_defines=macro_defines,
        preprocessing=preprocessing,
        encoding=encoding,
    )
