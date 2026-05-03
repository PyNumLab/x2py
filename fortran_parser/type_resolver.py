# -*- coding: utf-8 -*-
from __future__ import annotations


def extract_kind_from_type_spec(base_type: str, type_spec: str) -> str | None:
    if not type_spec:
        return None
    inside = type_spec[1:-1].strip()
    lowered = inside.lower()
    if "kind" in lowered and "=" in inside:
        return inside.split("=", 1)[1].strip()
    if base_type == "character" and "len" in lowered:
        return inside
    return None
