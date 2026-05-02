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


def preprocess_lines(code: str, filename: str | None = None) -> list[str]:
    form = detect_source_form(code, filename)
    raw = [strip_comment(l.rstrip("\n"), form) for l in code.splitlines()]

    folded: list[str] = []
    pending = ""
    continuing = False
    for line in raw:
        if form == "fixed":
            cont = len(line) >= 6 and line[5:6].strip() != ""
            text = line[6:] if len(line) > 6 else ""
            if not text.strip() and not continuing:
                continue
            if cont and pending:
                pending += " " + text.strip()
                continuing = False
                continue
            if pending:
                folded.append(pending)
            pending = text.strip()
            continuing = False
            continue

        stripped = line.rstrip()
        if not stripped and not continuing:
            continue
        starts_with_amp = stripped.lstrip().startswith("&")
        if starts_with_amp:
            stripped = stripped.lstrip()[1:].lstrip()
        if continuing:
            pending += stripped
        else:
            pending = stripped
        if pending.endswith("&"):
            pending = pending[:-1].rstrip()
            continuing = True
            continue
        folded.append(pending)
        pending = ""
        continuing = False

    if pending:
        folded.append(pending)
    return folded
