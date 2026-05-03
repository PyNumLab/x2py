# -*- coding: utf-8 -*-
from __future__ import annotations


def detect_source_form(code: str, filename: str | None = None) -> str:
    if filename:
        lowered = filename.lower()
        if lowered.endswith((".f", ".for", ".ftn")):
            return "fixed"
        if lowered.endswith((".f90", ".f95", ".f03", ".f08")):
            return "free"

    for line in code.splitlines()[:20]:
        if len(line) >= 6 and line[:5].strip() == "" and line[5:6].strip():
            return "fixed"
    return "free"


def split_csv(text: str | None) -> list[str]:
    if not text:
        return []
    out, cur, depth = [], [], 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        if ch == "," and depth == 0:
            piece = "".join(cur).strip()
            if piece:
                out.append(piece)
            cur = []
            continue
        cur.append(ch)
    piece = "".join(cur).strip()
    if piece:
        out.append(piece)
    return out
