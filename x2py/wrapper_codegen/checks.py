"""Static contracts for the isolated wrapper-plan generator package."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from radon.complexity import cc_visit

__all__ = (
    "WrapperCodegenCheckConfig",
    "WrapperCodegenViolation",
    "check_wrapper_codegen_package",
    "check_wrapper_codegen_paths",
)


INFRASTRUCTURE_MODULES = frozenset({"__init__.py", "checks.py", "visitor.py"})
VISITOR_CLASS_SUFFIXES = ("Analyzer", "Emitter", "Planner", "Renderer", "Validator")
REGISTRY_SUFFIXES = ("_DISPATCHER", "_HANDLERS", "_REGISTRY")
HANDLER_PREFIXES = ("_convert_", "_emit_", "_handle_", "_visit_")
CONTROL_NODES = (ast.For, ast.AsyncFor, ast.If, ast.Match, ast.Try, ast.While, ast.With, ast.AsyncWith)


@dataclass(frozen=True)
class WrapperCodegenCheckConfig:
    """Limits enforced for new wrapper-codegen implementation code."""

    max_complexity: int = 10
    max_statements: int = 30
    max_nesting: int = 4


@dataclass(frozen=True)
class WrapperCodegenViolation:
    """One static-contract violation in ``x2py.wrapper_codegen``."""

    path: Path
    lineno: int
    code: str
    message: str

    @property
    def label(self) -> str:
        return f"{self.path}:{self.lineno}: {self.code}: {self.message}"


DEFAULT_CHECK_CONFIG = WrapperCodegenCheckConfig()


def check_wrapper_codegen_package(
    package_root: Path | None = None,
    *,
    config: WrapperCodegenCheckConfig | None = None,
) -> tuple[WrapperCodegenViolation, ...]:
    """Check every Python module in the isolated wrapper-codegen package."""
    root = package_root or Path(__file__).resolve().parent
    return check_wrapper_codegen_paths(
        sorted(root.rglob("*.py")), package_root=root, config=config or DEFAULT_CHECK_CONFIG
    )


def check_wrapper_codegen_paths(
    paths: list[Path],
    *,
    package_root: Path,
    config: WrapperCodegenCheckConfig | None = None,
) -> tuple[WrapperCodegenViolation, ...]:
    """Check selected wrapper-codegen modules."""
    violations = []
    resolved_config = config or DEFAULT_CHECK_CONFIG
    for path in paths:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        violations.extend(_module_violations(path, tree, package_root))
        violations.extend(_function_size_violations(path, tree, source, resolved_config))
        violations.extend(_registry_violations(path, tree))
    return tuple(violations)


def _module_violations(path: Path, tree: ast.Module, package_root: Path) -> list[WrapperCodegenViolation]:
    if path.name in INFRASTRUCTURE_MODULES:
        return []
    return [
        *_module_function_violations(path, tree),
        *_visitor_class_violations(path, tree),
        *_dependency_violations(path, tree, package_root),
    ]


def _module_function_violations(path: Path, tree: ast.Module) -> list[WrapperCodegenViolation]:
    return [
        _violation(path, node, "module-function", f"move production function {node.name!r} onto a class")
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    ]


def _visitor_class_violations(path: Path, tree: ast.Module) -> list[WrapperCodegenViolation]:
    return [
        _violation(path, node, "visitor-class", f"{node.name} must inherit ClassVisitor")
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name.endswith(VISITOR_CLASS_SUFFIXES)
        and not _inherits_class_visitor(node)
    ]


def _dependency_violations(path: Path, tree: ast.Module, package_root: Path) -> list[WrapperCodegenViolation]:
    if not _is_under(path, package_root):
        return []
    return [
        _violation(path, node, "legacy-codegen-import", "wrapper_codegen must not import x2py.codegen")
        for node in ast.walk(tree)
        if _imports_legacy_codegen(node)
    ]


def _function_size_violations(
    path: Path,
    tree: ast.Module,
    source: str,
    config: WrapperCodegenCheckConfig,
) -> list[WrapperCodegenViolation]:
    return [
        *_complexity_violations(path, source, config.max_complexity),
        *_statement_count_violations(path, tree, config.max_statements),
        *_nesting_violations(path, tree, config.max_nesting),
    ]


def _complexity_violations(path: Path, source: str, max_complexity: int) -> list[WrapperCodegenViolation]:
    return [
        WrapperCodegenViolation(path, block.lineno, "complexity", f"{block.name} has complexity {block.complexity}")
        for block in cc_visit(source)
        if block.complexity > max_complexity
    ]


def _statement_count_violations(path: Path, tree: ast.Module, max_statements: int) -> list[WrapperCodegenViolation]:
    return [
        _violation(path, node, "statement-count", f"{node.name} has {statement_count} statements")
        for node in _functions(tree)
        for statement_count in (_statement_count(node),)
        if statement_count > max_statements
    ]


def _nesting_violations(path: Path, tree: ast.Module, max_nesting: int) -> list[WrapperCodegenViolation]:
    return [
        _violation(path, node, "nesting-depth", f"{node.name} has nesting depth {nesting_depth}")
        for node in _functions(tree)
        for nesting_depth in (_nesting_depth(node),)
        if nesting_depth > max_nesting
    ]


def _registry_violations(path: Path, tree: ast.Module) -> list[WrapperCodegenViolation]:
    violations = []
    for class_node in (node for node in tree.body if isinstance(node, ast.ClassDef)):
        method_names = {node.name for node in class_node.body if isinstance(node, ast.FunctionDef)}
        registry_methods = _registry_methods(class_node)
        violations.extend(_missing_registry_methods(path, class_node, method_names, registry_methods))
        violations.extend(_forbidden_printer_calls(path, class_node, registry_methods))
    return violations


def _missing_registry_methods(
    path: Path,
    class_node: ast.ClassDef,
    method_names: set[str],
    registry_methods: dict[str, ast.AST],
) -> list[WrapperCodegenViolation]:
    return [
        _violation(path, owner, "registry-missing-handler", f"{class_node.name}.{method_name} is not defined")
        for method_name, owner in registry_methods.items()
        if method_name not in method_names
    ]


def _forbidden_printer_calls(
    path: Path,
    class_node: ast.ClassDef,
    registry_methods: dict[str, ast.AST],
) -> list[WrapperCodegenViolation]:
    handler_names = set(registry_methods) | {
        node.name
        for node in class_node.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith(HANDLER_PREFIXES)
    }
    return [
        _violation(path, call, "handler-printer-call", f"{class_node.name}.{method.name} calls a printer directly")
        for method in class_node.body
        if isinstance(method, ast.FunctionDef) and method.name in handler_names
        for call in ast.walk(method)
        if _is_forbidden_printer_call(call)
    ]


def _functions(tree: ast.Module) -> list[ast.FunctionDef]:
    return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def _statement_count(node: ast.FunctionDef) -> int:
    return sum(isinstance(child, ast.stmt) for child in ast.walk(node)) - 1


def _nesting_depth(node: ast.FunctionDef) -> int:
    return max((_node_nesting_depth(statement, 0) for statement in node.body), default=0)


def _node_nesting_depth(node: ast.AST, depth: int) -> int:
    next_depth = depth + 1 if isinstance(node, CONTROL_NODES) else depth
    child_depths = [_node_nesting_depth(child, next_depth) for child in ast.iter_child_nodes(node)]
    return max([next_depth, *child_depths])


def _registry_methods(class_node: ast.ClassDef) -> dict[str, ast.AST]:
    methods = {}
    for assignment in (node for node in class_node.body if isinstance(node, ast.Assign)):
        if _is_registry_assignment(assignment):
            _collect_registry_methods(assignment.value, assignment, methods)
    return methods


def _is_registry_assignment(node: ast.Assign) -> bool:
    return any(isinstance(target, ast.Name) and target.id.endswith(REGISTRY_SUFFIXES) for target in node.targets)


def _collect_registry_methods(node: ast.AST, owner: ast.AST, methods: dict[str, ast.AST]) -> None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        methods.setdefault(node.value, owner)
    if isinstance(node, ast.Dict):
        for value in node.values:
            _collect_registry_methods(value, owner, methods)


def _is_forbidden_printer_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"doprint", "write"}
    )


def _inherits_class_visitor(node: ast.ClassDef) -> bool:
    return any(_base_name(base) == "ClassVisitor" for base in node.bases)


def _base_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _imports_legacy_codegen(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(alias.name == "x2py.codegen" or alias.name.startswith("x2py.codegen.") for alias in node.names)
    return isinstance(node, ast.ImportFrom) and bool(node.module) and _is_codegen_module(node.module)


def _is_codegen_module(module_name: str) -> bool:
    return module_name == "x2py.codegen" or module_name.startswith("x2py.codegen.")


def _is_under(path: Path, directory: Path) -> bool:
    return path.resolve().is_relative_to(directory.resolve())


def _violation(path: Path, node: ast.AST, code: str, message: str) -> WrapperCodegenViolation:
    return WrapperCodegenViolation(path, getattr(node, "lineno", 1), code, message)
