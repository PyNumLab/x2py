"""Python public-name policy for generated wrapper surfaces."""

from __future__ import annotations

from dataclasses import dataclass
import keyword
import re


_INVALID_IDENTIFIER_CHAR_RE = re.compile(r"[^0-9A-Za-z_]")


@dataclass(frozen=True)
class NormalizedPublicName:
    """Result of normalizing one source name for Python exposure."""

    name: str
    needs_fix: bool


@dataclass(frozen=True)
class PublicNameRecord:
    """One reserved public name in a Python namespace."""

    raw_name: str
    category: str
    owner: str


def normalize_public_name(raw_name: object) -> NormalizedPublicName:
    """Return the canonical Python public name for a source-level symbol."""
    raw = str(raw_name).strip()
    lowered = raw.casefold()
    candidate = _INVALID_IDENTIFIER_CHAR_RE.sub("_", lowered)
    if not candidate:
        candidate = "_"
    if not (candidate[0].isalpha() or candidate[0] == "_"):
        candidate = f"_{candidate}"
    if keyword.iskeyword(candidate):
        candidate = f"{candidate}_"
    return NormalizedPublicName(candidate, needs_fix=candidate != lowered)


class PublicNamePolicy:
    """Reserve Python-visible names and optionally reject automatic fixes."""

    def __init__(self, *, strict: bool = False):
        self.strict = strict
        self._used: dict[tuple[str, ...], dict[str, PublicNameRecord]] = {}

    def reserve(
        self,
        namespace: tuple[str, ...],
        raw_name: object,
        *,
        category: str,
        owner: object | None = None,
    ) -> str:
        """Reserve and return the Python-visible name for one public symbol."""
        normalized = normalize_public_name(raw_name)
        owner_text = str(owner or raw_name)
        raw_text = str(raw_name)
        namespace_key = tuple(str(part) for part in namespace)
        namespace_text = ".".join(namespace_key) or "<module>"

        if self.strict and normalized.needs_fix:
            raise ValueError(
                f"Public {category} name {raw_text!r} in {namespace_text} normalizes to "
                f"{normalized.name!r}; strict wrapper naming does not fix Python names"
            )

        used = self._used.setdefault(namespace_key, {})
        existing = used.get(normalized.name)
        if existing is None:
            used[normalized.name] = PublicNameRecord(raw_text, category, owner_text)
            return normalized.name

        if self.strict:
            raise ValueError(
                f"Public {category} name {raw_text!r} in {namespace_text} collides with "
                f"{existing.category} {existing.raw_name!r} ({existing.owner}) as Python name "
                f"{normalized.name!r}; "
                "strict wrapper naming does not fix collisions"
            )

        index = 2
        while True:
            candidate = f"{normalized.name}_{index}"
            if candidate not in used:
                used[candidate] = PublicNameRecord(raw_text, category, owner_text)
                return candidate
            index += 1
