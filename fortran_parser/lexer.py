# -*- coding: utf-8 -*-
from __future__ import annotations

from .utils import detect_source_form


def strip_comment(line: str, form: str) -> str:
    if form == "fixed" and line and line[0] in ("c", "C", "*", "!"):
        return ""
    in_string = False
    quote = ""
    out = []
    for c in line:
        if c in ('"', "'"):
            if in_string and c == quote:
                in_string = False
                quote = ""
            elif not in_string:
                in_string = True
                quote = c
            out.append(c)
            continue
        if c == "!" and not in_string:
            break
        out.append(c)
    return "".join(out)


def preprocess_lines(code: str, filename: str | None = None) -> list[tuple[str, int, str]]:
    form = detect_source_form(code, filename)
    raw_lines = code.splitlines()
    raw = [(strip_comment(l.rstrip("\n"), form), i + 1, l.rstrip("\n")) for i, l in enumerate(raw_lines)]

    folded: list[tuple[str, int, str]] = []
    pending = ""
    pending_lineno = 0
    pending_raw = ""
    continuing = False
    for stripped_line, lineno, original_line in raw:
        if form == "fixed":
            cont = len(stripped_line) >= 6 and stripped_line[5:6].strip() != ""
            text = stripped_line[6:] if len(stripped_line) > 6 else ""
            if not text.strip() and not continuing:
                continue
            if cont and pending:
                pending += " " + text.strip()
                continuing = False
                continue
            if pending:
                folded.append((pending, pending_lineno, pending_raw))
            pending = text.strip()
            pending_lineno = lineno
            pending_raw = original_line
            continuing = False
            continue

        line = stripped_line.rstrip()
        if not line and not continuing:
            continue
        starts_with_amp = line.lstrip().startswith("&")
        if starts_with_amp:
            line = line.lstrip()[1:].lstrip()
        if continuing:
            pending += line
        else:
            pending = line
            pending_lineno = lineno
            pending_raw = original_line
        if pending.endswith("&"):
            pending = pending[:-1].rstrip()
            continuing = True
            continue
        folded.append((pending, pending_lineno, pending_raw))
        pending = ""
        pending_lineno = 0
        pending_raw = ""
        continuing = False

    if pending:
        folded.append((pending, pending_lineno, pending_raw))
    return folded
