# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path

from .lexer import (
    CTopLevelSegment,
    split_top_level_c_source,
    strip_c_comments,
    top_level_partition,
    top_level_split,
)
from .models import (
    CArray,
    CFile,
    CFunction,
    CGlobal,
    CParameter,
    CParseError,
    CPointer,
    CProject,
    CSourceLocation,
    CTypeRef,
    CTypedef,
)
from .preprocessor import collect_preprocessor_metadata


_C_SOURCE_SUFFIXES = {".c", ".h"}
_IDENTIFIER_RE = re.compile(r"[A-Za-z_]\w*")
_POINTER_TAIL_RE = re.compile(r"((?:\s*\*\s*(?:(?:const|restrict|volatile|_Atomic)\s*)*)+)$")
_ARRAY_RE = re.compile(r"\[([^\]]*)\]")
_STORAGE_CLASSES = {"typedef", "extern", "static", "register", "_Thread_local"}
_TYPE_QUALIFIERS = {"const", "restrict", "volatile", "_Atomic"}
_FUNCTION_SPECIFIERS = {"inline", "_Noreturn"}
_TAG_KINDS = {"struct", "union", "enum"}
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
_TYPE_ONLY_WORDS = _PRIMITIVE_WORDS | _TYPE_QUALIFIERS | _TAG_KINDS


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

    The implemented subset covers raw preprocessing metadata plus simple
    top-level declarations, typedefs, and function prototypes/definitions.
    """

    def _source_location(self, segment: CTopLevelSegment) -> CSourceLocation:
        return CSourceLocation(
            filename=segment.filename,
            line=segment.original_start_line,
            column=segment.original_start_column,
            source_line=segment.original_source_line,
        )

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

    def _split_pointer_tail(self, prefix: str) -> tuple[str, str]:
        match = _POINTER_TAIL_RE.search(prefix)
        if not match:
            return prefix.strip(), ""
        return prefix[: match.start()].strip(), match.group(1).strip()

    def _specifier_words(self, spec_text: str) -> list[str]:
        return _IDENTIFIER_RE.findall(spec_text)

    def _parse_specifiers(self, spec_text: str) -> tuple[CTypeRef, list[str]]:
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

        typeref = CTypeRef(
            qualifiers=qualifiers,
            storage_class=storage,
            source_text=spec_text.strip(),
        )
        if type_words and type_words[0] in _TAG_KINDS:
            typeref.tag_kind = type_words[0]
            if len(type_words) > 1:
                typeref.tag_name = type_words[1]
            typeref.base = " ".join(type_words[:2])
        elif type_words:
            base = " ".join(type_words)
            typeref.base = base
            if len(type_words) == 1 and type_words[0] not in _PRIMITIVE_WORDS:
                typeref.typedef_name = type_words[0]
            if "signed" in type_words:
                typeref.sign = "signed"
            elif "unsigned" in type_words:
                typeref.sign = "unsigned"
            widths = [word for word in type_words if word in {"char", "short", "int", "long"}]
            if widths:
                typeref.width = " ".join(widths)
        else:
            typeref.base = "unknown"

        return typeref, function_specifiers

    def _parse_pointers(self, pointer_text: str) -> list[CPointer]:
        pointers: list[CPointer] = []
        current: CPointer | None = None
        for token in re.findall(r"\*|const|restrict|volatile|_Atomic", pointer_text):
            if token == "*":
                current = CPointer()
                pointers.append(current)
            elif current is not None:
                current.qualifiers.append(token)
        return pointers

    def _parse_arrays(self, declarator_tail: str) -> list[CArray]:
        arrays: list[CArray] = []
        for match in _ARRAY_RE.finditer(declarator_tail):
            content = " ".join(match.group(1).strip().split())
            is_static = False
            size = content or None
            if content.startswith("static "):
                is_static = True
                size = content[len("static ") :].strip() or None
            arrays.append(CArray(size=size, static=is_static))
        return arrays

    def _build_type(
        self,
        spec_text: str,
        declarator_fragment: str = "",
    ) -> tuple[CTypeRef, list[str]]:
        spec_without_pointer, spec_pointer = self._split_pointer_tail(spec_text)
        typeref, function_specifiers = self._parse_specifiers(spec_without_pointer)
        typeref.pointers = self._parse_pointers(f"{spec_pointer} {declarator_fragment}")
        typeref.arrays = self._parse_arrays(declarator_fragment)
        source_parts = [spec_text.strip(), declarator_fragment.strip()]
        typeref.source_text = " ".join(part for part in source_parts if part).strip()
        return typeref, function_specifiers

    def _split_first_declarator(self, first_declarator: str) -> tuple[str, str]:
        declaration, _initializer = top_level_partition(first_declarator, "=")
        name_match = self._last_identifier(declaration)
        if name_match is None:
            return declaration.strip(), ""

        prefix = declaration[: name_match.start()]
        suffix = declaration[name_match.end() :]
        spec_text, pointer_tail = self._split_pointer_tail(prefix)
        declarator = f"{pointer_tail} {name_match.group(0)}{suffix}".strip()
        return spec_text, declarator

    def _declarator_name(self, declarator: str) -> tuple[str | None, str]:
        declaration, _initializer = top_level_partition(declarator, "=")
        name_match = self._last_identifier(declaration)
        if name_match is None:
            return None, declaration.strip()
        return name_match.group(0), declaration.strip()

    def _looks_like_type_only_parameter(self, text: str) -> bool:
        stripped = text.strip()
        name_match = self._last_identifier(stripped)
        if name_match is None:
            return True
        words = self._specifier_words(stripped)
        last = name_match.group(0)
        if last in _TYPE_ONLY_WORDS:
            return True
        if len(words) >= 2 and words[-2] in _TAG_KINDS:
            return True
        return False

    def _parse_parameter(self, text: str) -> CParameter | None:
        stripped = text.strip()
        if not stripped or stripped == "void":
            return None
        if self._looks_like_type_only_parameter(stripped):
            typeref, _function_specifiers = self._build_type(stripped)
            return CParameter(name=None, type=typeref)

        spec_text, declarator = self._split_first_declarator(stripped)
        if not spec_text:
            return None
        name, declaration = self._declarator_name(declarator)
        typeref, _function_specifiers = self._build_type(spec_text, declaration)
        return CParameter(name=name, type=typeref)

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
        if text.startswith(("typedef ", "struct ", "union ", "enum ")):
            return None

        parameter_bounds = self._find_parameter_list(text)
        if parameter_bounds is None:
            return None

        open_index, close_index = parameter_bounds
        before_parameters = text[:open_index].strip()
        parameters_text = text[open_index + 1 : close_index]
        name_match = self._last_identifier(before_parameters)
        if name_match is None:
            return None

        name = name_match.group(0)
        return_spec = before_parameters[: name_match.start()].strip()
        return_declarator = before_parameters[name_match.end() :].strip()
        if not return_spec:
            return None
        if "(" in return_spec or ")" in return_spec:
            return None
        if self._is_knr_definition(segment, parameters_text):
            raise CParseError(
                "K&R style function definitions are not supported",
                filename=segment.filename,
                line_number=segment.original_start_line,
                column=segment.original_start_column,
                source_line=segment.original_source_line,
                code="CPARSE002",
            )

        return_type, function_specifiers = self._build_type(return_spec, return_declarator)
        parameters, variadic = self._parse_parameters(parameters_text)
        return CFunction(
            name=name,
            return_type=return_type,
            parameters=parameters,
            storage=list(return_type.storage_class),
            specifiers=function_specifiers,
            variadic=variadic,
            is_definition=segment.terminator == "block",
            prototype_style=self._prototype_style(parameters_text),
            source_location=self._source_location(segment),
            start=self._source_location(segment),
            end=self._end_location(segment) if segment.terminator == "block" else None,
        )

    def _parse_declaration(self, segment: CTopLevelSegment) -> tuple[list[CTypedef], list[CGlobal]]:
        text = segment.text.strip()
        if not text or text.startswith(("struct ", "union ", "enum ")):
            return [], []
        if "(" in text or ")" in text:
            return [], []

        declarator_texts = top_level_split(text, ",")
        if not declarator_texts:
            return [], []

        spec_text, first_declarator = self._split_first_declarator(declarator_texts[0])
        if not spec_text or not first_declarator:
            return [], []

        typedefs: list[CTypedef] = []
        globals_: list[CGlobal] = []
        all_declarators = [first_declarator, *declarator_texts[1:]]

        for declarator in all_declarators:
            name, declaration = self._declarator_name(declarator)
            if not name:
                continue
            typeref, _function_specifiers = self._build_type(spec_text, declaration)
            location = self._source_location(segment)
            if "typedef" in typeref.storage_class:
                typedefs.append(CTypedef(name=name, type=typeref, source_location=location))
            else:
                globals_.append(CGlobal(name=name, type=typeref, source_location=location))

        return typedefs, globals_

    def _parse_translation_unit(
        self,
        source: str,
        filename: str | None,
    ) -> tuple[list[CFunction], list[CTypedef], list[CGlobal]]:
        self._raise_for_unsupported_old_style_definitions(source, filename)

        functions: list[CFunction] = []
        typedefs: list[CTypedef] = []
        globals_: list[CGlobal] = []

        for segment in split_top_level_c_source(source, filename=filename):
            function = self._parse_function(segment)
            if function is not None:
                functions.append(function)
                continue
            if segment.terminator != ";":
                continue
            parsed_typedefs, parsed_globals = self._parse_declaration(segment)
            typedefs.extend(parsed_typedefs)
            globals_.extend(parsed_globals)

        return functions, typedefs, globals_

    def _build_project(self, parsed_files: dict[str, CFile]) -> CProject:
        project = CProject(files=parsed_files)
        for file in parsed_files.values():
            for function in file.functions:
                project.functions[function.name] = function
            for typedef in file.typedefs:
                project.typedefs[typedef.name] = typedef
            for global_ in file.globals:
                project.globals[global_.name] = global_
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
            functions, typedefs, globals_ = self._parse_translation_unit(source, filename)
            parsed.functions = functions
            parsed.typedefs = typedefs
            parsed.globals = globals_
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
