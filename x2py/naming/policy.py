"""Naming policy for public APIs and generated target-language symbols."""

from __future__ import annotations

from dataclasses import dataclass
import keyword
import re
import warnings

from x2py.utilities.strings import create_incremented_string

_INVALID_IDENTIFIER_CHAR_RE = re.compile(r"[^0-9A-Za-z_]")
_SYMBOL_CONTEXTS = frozenset(("module", "function", "class", "variable", "wrapper"))
_PARENT_CONTEXTS = frozenset(("module", "function", "class", "loop", "program"))


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


@dataclass(frozen=True)
class GeneratedSymbolRules:
    """Language-specific generated-symbol constraints."""

    language: str
    keywords: frozenset[str]
    case_sensitive: bool = True
    prefix_module_members: bool = False
    destructor_name: str = "free"
    module_constructor_prefix: bool = False
    rewrite_python_special_names: bool = False
    max_length: int | None = None

    def has_clash(self, name: object, symbols: set[object]) -> bool:
        """Return whether ``name`` collides with keywords or symbols."""
        if self.case_sensitive:
            return str(name) in self.keywords or name in symbols
        lowered = str(name).lower()
        return lowered in self.keywords or any(lowered == str(symbol).lower() for symbol in symbols)


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


class NamingPolicy:
    """Own public Python names and generated target-language symbols."""

    def __init__(self, *, strict_public_names: bool = False):
        self.strict_public_names = strict_public_names
        self._public_names: dict[tuple[str, ...], dict[str, PublicNameRecord]] = {}

    def reserve_public_name(
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

        if self.strict_public_names and normalized.needs_fix:
            raise ValueError(
                f"Public {category} name {raw_text!r} in {namespace_text} normalizes to "
                f"{normalized.name!r}; strict wrapper naming does not fix Python names"
            )

        used = self._public_names.setdefault(namespace_key, {})
        existing = used.get(normalized.name)
        if existing is None:
            used[normalized.name] = PublicNameRecord(raw_text, category, owner_text)
            return normalized.name

        if self.strict_public_names:
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

    def has_generated_symbol_clash(self, name: object, symbols: set[object], *, language: str) -> bool:
        """Return whether a generated symbol collides for ``language``."""
        return generated_symbol_rules(language).has_clash(name, symbols)

    def generated_symbol(
        self,
        name: object,
        symbols: set[object],
        *,
        language: str,
        prefix: str,
        context: str,
        parent_context: str,
    ) -> str:
        """Return a target-language-safe generated symbol."""
        rules = generated_symbol_rules(language)
        proposed = _prepared_generated_symbol(str(name), rules, prefix, context, parent_context)
        symbol = _collisionless_symbol(proposed, symbols, rules)
        if rules.max_length is not None and len(symbol) > rules.max_length:
            warnings.warn(
                f"Name {symbol} is too long for {rules.language}. This may cause compiler errors",
                stacklevel=2,
            )
        return symbol


def generated_symbol_rules(language: str) -> GeneratedSymbolRules:
    """Return generated-symbol rules for a target language."""
    try:
        return _GENERATED_SYMBOL_RULES[language.casefold()]
    except KeyError as exc:
        raise ValueError(f"Unsupported generated-symbol language: {language!r}") from exc


def _prepared_generated_symbol(
    name: str,
    rules: GeneratedSymbolRules,
    prefix: str,
    context: str,
    parent_context: str,
) -> str:
    """Apply language-specific symbol rewrites before collision checks."""
    if context not in _SYMBOL_CONTEXTS:
        raise ValueError(f"Unsupported generated-symbol context: {context!r}")
    if parent_context not in _PARENT_CONTEXTS:
        raise ValueError(f"Unsupported generated-symbol parent context: {parent_context!r}")
    if context == "wrapper":
        return name
    if not rules.rewrite_python_special_names:
        return name
    if name == "__init__":
        return f"{prefix}init" if rules.module_constructor_prefix and parent_context == "module" else "init"
    if name == "__del__":
        return rules.destructor_name
    if len(name) > 4 and all(name[index] == "_" for index in (0, 1, -1, -2)):
        name = "operator" + name[1:-2]
    if name[0] == "_":
        name = "private" + name
    if rules.prefix_module_members and (context == "function" or (parent_context == "module" and context != "module")):
        name = prefix + name
    return name


def _collisionless_symbol(name: str, symbols: set[object], rules: GeneratedSymbolRules) -> str:
    """Return ``name`` or an incremented variant that does not collide."""
    if not rules.has_clash(name, symbols):
        return name
    colliding = set(rules.keywords)
    colliding.update(symbols)
    symbol, _ = create_incremented_string(colliding, prefix=name, counter=1, naming_rules=rules)
    return symbol


_C_KEYWORDS = frozenset(
    {
        "isign",
        "fsign",
        "csign",
        "auto",
        "break",
        "case",
        "char",
        "const",
        "continue",
        "default",
        "do",
        "double",
        "else",
        "enum",
        "extern",
        "float",
        "for",
        "goto",
        "if",
        "inline",
        "int",
        "long",
        "register",
        "restrict",
        "return",
        "short",
        "signed",
        "sizeof",
        "static",
        "struct",
        "switch",
        "typedef",
        "union",
        "unsigned",
        "void",
        "volatile",
        "whie",
        "_Alignas",
        "_Alignof",
        "_Atomic",
        "_Bool",
        "_Complex",
        "Decimal128",
        "_Decimal32",
        "_Decimal64",
        "_Generic",
        "_Imaginary",
        "_Noreturn",
        "_Static_assert",
        "_Thread_local",
        "I",
        "cspan_copy",
        "c_foreach",
        "c_COLMAJOR",
        "c_ROWMAJOR",
        "cspan_md_layout",
        "using_cspan",
        "STC_CSPAN_INDEX_TYPE",
        "array_int64_1d",
        "array_int64_2d",
        "array_int64_3d",
        "array_int32_1d",
        "array_int32_2d",
        "array_int32_3d",
        "array_float_1d",
        "array_float_2d",
        "array_float_3d",
        "array_double_1d",
        "array_double_2d",
        "array_double_3d",
        "array_bool_1d",
        "array_bool_2d",
        "array_bool_3d",
        "array_float_complex_1d",
        "array_float_complex_2d",
        "array_float_complex_3d",
        "array_double_complex_1d",
        "array_double_complex_2d",
        "array_double_complex_3d",
        "c_ALL",
        "c_END",
        "cspan_slice",
        "cspan_transpose",
        "complex_max",
        "complex_min",
        "expm1",
        "complex_expm1",
        "main",
    }
)

_FORTRAN_KEYWORDS = frozenset(
    {
        "assign",
        "backspace",
        "block",
        "blockdata",
        "call",
        "close",
        "common",
        "continue",
        "data",
        "dimension",
        "do",
        "else",
        "elseif",
        "end",
        "endfile",
        "endif",
        "endfunction",
        "endmodule",
        "endprogram",
        "endsubroutine",
        "entry",
        "equivalence",
        "external",
        "format",
        "function",
        "goto",
        "if",
        "implicit",
        "intrinsic",
        "open",
        "parameter",
        "pause",
        "print",
        "program",
        "read",
        "return",
        "rewind",
        "rewrite",
        "save",
        "stop",
        "subroutine",
        "then",
        "write",
        "allocatable",
        "allocate",
        "case",
        "contains",
        "cycle",
        "deallocate",
        "elsewhere",
        "exit",
        "include",
        "interface",
        "intent",
        "module",
        "namelist",
        "nullify",
        "only",
        "operator",
        "optional",
        "pointer",
        "private",
        "procedure",
        "public",
        "recursive",
        "result",
        "select",
        "sequence",
        "target",
        "use",
        "while",
        "where",
        "elemental",
        "forall",
        "pure",
        "abstract",
        "associate",
        "asynchronous",
        "bind",
        "class",
        "deferred",
        "enum",
        "enumerator",
        "extends",
        "final",
        "flush",
        "generic",
        "import",
        "non_overridable",
        "nopass",
        "pass",
        "protected",
        "value",
        "volatile",
        "wait",
        "codimension",
        "concurrent",
        "contiguous",
        "critical",
        "error",
        "submodule",
        "sync",
        "lock",
        "unlock",
        "test",
        "abs",
        "sqrt",
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "exp",
        "log",
        "int",
        "nint",
        "floor",
        "fraction",
        "real",
        "max",
        "mod",
        "count",
        "pack",
        "numpy_sign",
        "c_associated",
        "c_loc",
        "c_f_pointer",
        "c_ptr",
        "c_malloc",
        "storage_size",
        "c_size_t",
    }
)

_GENERATED_SYMBOL_RULES = {
    "python": GeneratedSymbolRules(language="Python", keywords=frozenset()),
    "c": GeneratedSymbolRules(
        language="C",
        keywords=_C_KEYWORDS,
        prefix_module_members=True,
        destructor_name="drop",
        rewrite_python_special_names=True,
    ),
    "fortran": GeneratedSymbolRules(
        language="Fortran",
        keywords=_FORTRAN_KEYWORDS,
        case_sensitive=False,
        module_constructor_prefix=True,
        rewrite_python_special_names=True,
        max_length=96,
    ),
}
