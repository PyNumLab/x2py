# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CLogicalRecord:
    """A comment-stripped logical C source record with original line mapping."""

    text: str
    filename: str | None = None
    original_start_line: int = 1
    original_end_line: int = 1
    original_source_lines: tuple[str, ...] = field(default_factory=tuple)

    @property
    def source_line(self) -> str | None:
        return self.original_source_lines[0] if self.original_source_lines else None


@dataclass(frozen=True)
class NormalizedCSource:
    filename: str | None
    records: list[CLogicalRecord]


@dataclass(frozen=True)
class CToken:
    text: str
    kind: str
    filename: str | None = None
    line: int = 1
    column: int = 1
    source_line: str | None = None


_TWO_CHAR_OPERATORS = {
    "++",
    "--",
    "->",
    "==",
    "!=",
    "<=",
    ">=",
    "&&",
    "||",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "&=",
    "|=",
    "^=",
    "<<",
    ">>",
}


def strip_c_comments(source: str) -> str:
    """Remove C comments while preserving line and column accounting."""
    out: list[str] = []
    i = 0
    state = "normal"
    quote = ""

    while i < len(source):
        char = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""

        if state == "line_comment":
            if char == "\n":
                out.append(char)
                state = "normal"
            else:
                out.append(" ")
            i += 1
            continue

        if state == "block_comment":
            if char == "*" and nxt == "/":
                out.extend((" ", " "))
                i += 2
                state = "normal"
                continue
            out.append("\n" if char == "\n" else " ")
            i += 1
            continue

        if state in {"string", "char"}:
            out.append(char)
            if char == "\\" and nxt:
                out.append(nxt)
                i += 2
                continue
            if char == quote:
                state = "normal"
                quote = ""
            i += 1
            continue

        if char == "/" and nxt == "/":
            out.extend((" ", " "))
            i += 2
            state = "line_comment"
            continue
        if char == "/" and nxt == "*":
            out.extend((" ", " "))
            i += 2
            state = "block_comment"
            continue
        if char in {'"', "'"}:
            state = "string" if char == '"' else "char"
            quote = char
            out.append(char)
            i += 1
            continue

        out.append(char)
        i += 1

    return "".join(out)


def normalize_c_source(source: str, filename: str | None = None) -> NormalizedCSource:
    """Fold C logical records after safe comment removal."""
    stripped = strip_c_comments(source)
    stripped_lines = stripped.splitlines()
    original_lines = source.splitlines()

    records: list[CLogicalRecord] = []
    pending_text: str | None = None
    pending_start_line = 1
    pending_source_lines: list[str] = []

    for index, stripped_line in enumerate(stripped_lines, start=1):
        original_line = original_lines[index - 1] if index - 1 < len(original_lines) else ""
        line = stripped_line.rstrip()
        continued = line.endswith("\\")
        part = line[:-1].rstrip() if continued else line

        if pending_text is None:
            pending_text = part
            pending_start_line = index
            pending_source_lines = [original_line]
        else:
            pending_text = f"{pending_text} {part.lstrip()}"
            pending_source_lines.append(original_line)

        if continued:
            continue

        if pending_text.strip():
            records.append(
                CLogicalRecord(
                    text=pending_text.strip(),
                    filename=filename,
                    original_start_line=pending_start_line,
                    original_end_line=index,
                    original_source_lines=tuple(pending_source_lines),
                )
            )
        pending_text = None
        pending_source_lines = []

    if pending_text is not None and pending_text.strip():
        records.append(
            CLogicalRecord(
                text=pending_text.strip(),
                filename=filename,
                original_start_line=pending_start_line,
                original_end_line=len(stripped_lines),
                original_source_lines=tuple(pending_source_lines),
            )
        )

    return NormalizedCSource(filename=filename, records=records)


def _source_line(lines: list[str], line_number: int) -> str | None:
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return None


def lex_c_source(source: str, filename: str | None = None) -> list[CToken]:
    """Tokenize a small C lexical subset for parser staging tests."""
    stripped = strip_c_comments(source)
    source_lines = source.splitlines()
    tokens: list[CToken] = []
    i = 0
    line = 1
    column = 1

    while i < len(stripped):
        char = stripped[i]
        nxt = stripped[i + 1] if i + 1 < len(stripped) else ""

        if char == "\n":
            line += 1
            column = 1
            i += 1
            continue
        if char.isspace():
            column += 1
            i += 1
            continue

        start_line = line
        start_column = column
        source_line = _source_line(source_lines, start_line)

        if char in {'"', "'"}:
            quote = char
            text = [char]
            i += 1
            column += 1
            while i < len(stripped):
                current = stripped[i]
                text.append(current)
                i += 1
                column += 1
                if current == "\\" and i < len(stripped):
                    text.append(stripped[i])
                    i += 1
                    column += 1
                    continue
                if current == quote:
                    break
            tokens.append(
                CToken(
                    text="".join(text),
                    kind="string" if quote == '"' else "char",
                    filename=filename,
                    line=start_line,
                    column=start_column,
                    source_line=source_line,
                )
            )
            continue

        if char.isalpha() or char == "_":
            start = i
            while i < len(stripped) and (stripped[i].isalnum() or stripped[i] == "_"):
                i += 1
                column += 1
            tokens.append(
                CToken(
                    text=stripped[start:i],
                    kind="identifier",
                    filename=filename,
                    line=start_line,
                    column=start_column,
                    source_line=source_line,
                )
            )
            continue

        if char.isdigit():
            start = i
            while i < len(stripped) and (stripped[i].isalnum() or stripped[i] in "._"):
                i += 1
                column += 1
            tokens.append(
                CToken(
                    text=stripped[start:i],
                    kind="number",
                    filename=filename,
                    line=start_line,
                    column=start_column,
                    source_line=source_line,
                )
            )
            continue

        text = char + nxt if char + nxt in _TWO_CHAR_OPERATORS else char
        i += len(text)
        column += len(text)
        tokens.append(
            CToken(
                text=text,
                kind="punctuation",
                filename=filename,
                line=start_line,
                column=start_column,
                source_line=source_line,
            )
        )

    return tokens


__all__ = (
    "CLogicalRecord",
    "CToken",
    "NormalizedCSource",
    "lex_c_source",
    "normalize_c_source",
    "strip_c_comments",
)
