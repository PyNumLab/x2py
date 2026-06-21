"""Structural contracts for navigable codegen classes."""

from __future__ import annotations

import ast
from pathlib import Path


CODEGEN_ROOT = Path(__file__).parents[2] / "x2py" / "codegen"
BOUNDARY_DIRS = ("bridges", "bindings", "printers")
PUBLIC_MODULE_FUNCTIONS = {
    ("bindings", "cpython_api.py", "C_to_Python"),
    ("bindings", "numpy_cpython_api.py", "get_numpy_max_acceptable_version_file"),
    ("printers", "pyi_printer.py", "emit_module"),
    ("printers", "pyi_printer.py", "emit_module_stubs"),
    ("printers", "pyi_printer.py", "opaque_dependency_modules"),
}
SHARED_PRIVATE_FUNCTIONS = {
    ("bindings", "c_concepts.py", "_is_string_literal"),
}


def _boundary_modules():
    """Yield each Python module in the codegen boundaries under review."""
    for directory in BOUNDARY_DIRS:
        for path in sorted((CODEGEN_ROOT / directory).glob("*.py")):
            yield directory, path


def test_codegen_boundary_callables_are_documented():
    """Require every boundary function and method to state its contract."""
    missing = []
    for _, path in _boundary_modules():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and ast.get_docstring(node) is None:
                missing.append(f"{path.name}:{node.lineno}:{node.name}")
            if isinstance(node, ast.ClassDef):
                missing.extend(
                    f"{path.name}:{method.lineno}:{node.name}.{method.name}"
                    for method in node.body
                    if isinstance(method, ast.FunctionDef) and ast.get_docstring(method) is None
                )
    assert not missing, "Undocumented codegen callables:\n" + "\n".join(missing)


def test_codegen_uses_one_model_visitor_protocol():
    """Prevent legacy printer and extractor dispatch protocols from returning."""
    invalid = []
    lowercase_model_names = {"int", "str", "tuple"}
    for _, path in _boundary_modules():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith(("_print_", "_extract_")):
                invalid.append(f"{path.name}:{node.lineno}:{node.name}")
            if isinstance(node, ast.FunctionDef) and node.name.startswith("_visit_"):
                model_name = node.name.removeprefix("_visit_")
                if model_name[:1].islower() and model_name not in lowercase_model_names | {"not_supported"}:
                    invalid.append(f"{path.name}:{node.lineno}:{node.name}")
    assert not invalid, "Use _visit_* handlers or named helpers:\n" + "\n".join(invalid)


def test_public_methods_precede_internal_methods():
    """Keep each class's real public API above its visitors and helpers."""
    misplaced = []
    for _, path in _boundary_modules():
        tree = ast.parse(path.read_text(), filename=str(path))
        for class_node in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            private_seen = False
            for method in (node for node in class_node.body if isinstance(node, ast.FunctionDef)):
                is_public = not method.name.startswith("_")
                if is_public and private_seen:
                    misplaced.append(f"{path.name}:{method.lineno}:{class_node.name}.{method.name}")
                is_dunder = method.name.startswith("__") and method.name.endswith("__")
                if method.name.startswith("_") and not is_dunder:
                    private_seen = True
    assert not misplaced, "Public methods below internal methods:\n" + "\n".join(misplaced)


def test_module_functions_are_deliberate_boundary_apis_or_shared_utilities():
    """Keep stateful generation logic on its owning class."""
    unexpected = []
    allowed = PUBLIC_MODULE_FUNCTIONS | SHARED_PRIVATE_FUNCTIONS
    for directory, path in _boundary_modules():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in (node for node in tree.body if isinstance(node, ast.FunctionDef)):
            key = (directory, path.name, node.name)
            if key not in allowed:
                unexpected.append(f"{path.name}:{node.lineno}:{node.name}")
    assert not unexpected, "Unexpected module-level codegen functions:\n" + "\n".join(unexpected)
