"""Structural contract for class-based parser, semantics, and codegen visitors."""

from __future__ import annotations

import ast
import inspect

from tests.wrapper.fortran._support import REPO_ROOT
from x2py.c_parser.parser import CParser
from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator
from x2py.codegen.bridges.fortran_to_c import FortranToCBridgeGenerator
from x2py.codegen.generator import _Generator
from x2py.codegen.printers.codeprinter import CodePrinter
from x2py.codegen.printers.pyi_printer import PyiPrinter
from x2py.fortran_parser.parser import FortranParser, SourceUnit, _SOURCE_UNIT_TYPES
from x2py.semantics.c2ir import CToIRConverter
from x2py.semantics.fortran2ir import FortranToIRConverter, _FortranVariableContextVisitor
from x2py.semantics.ir2ast import _SemanticIrToCodegenAstVisitor
from x2py.semantics.pyi2ir import _ClassBodyVisitor, _ModuleVisitor
from x2py.utilities.visitor import ClassVisitor


VISITOR_CLASSES = (
    FortranParser,
    CToIRConverter,
    FortranToIRConverter,
    _FortranVariableContextVisitor,
    _SemanticIrToCodegenAstVisitor,
    _ClassBodyVisitor,
    _ModuleVisitor,
    _Generator,
    CodePrinter,
    PyiPrinter,
    CPythonBindingGenerator,
    FortranToCBridgeGenerator,
)

VISITOR_IMPLEMENTATION_PATHS = (
    REPO_ROOT / "x2py" / "fortran_parser" / "parser.py",
    REPO_ROOT / "x2py" / "semantics" / "c2ir.py",
    REPO_ROOT / "x2py" / "semantics" / "fortran2ir.py",
    REPO_ROOT / "x2py" / "semantics" / "ir2ast.py",
    REPO_ROOT / "x2py" / "semantics" / "pyi2ir.py",
    REPO_ROOT / "x2py" / "codegen" / "generator.py",
    REPO_ROOT / "x2py" / "codegen" / "bindings" / "c_to_python.py",
    REPO_ROOT / "x2py" / "codegen" / "bridges" / "fortran_to_c.py",
    REPO_ROOT / "x2py" / "codegen" / "printers" / "codeprinter.py",
    REPO_ROOT / "x2py" / "codegen" / "printers" / "pyi_printer.py",
)


def test_model_visitors_share_one_class_visitor_base():
    """Route every model visitor through the shared MRO dispatcher."""
    assert all(issubclass(visitor, ClassVisitor) for visitor in VISITOR_CLASSES)


def test_class_visitor_supports_configured_handler_prefix():
    """Allow specialized visitors to use names such as ``_print_<ClassName>``."""

    class Node:
        pass

    class SpecificNode(Node):
        pass

    class ParserVisitor(ClassVisitor):
        visitor_method_prefix = "_parse"

        @staticmethod
        def _parse_Node(node):
            return type(node).__name__

    assert ParserVisitor()._visit(SpecificNode()) == "SpecificNode"


def test_model_visitor_handlers_use_configured_class_names():
    """Reject the stdlib-style ``visit_Class`` protocol and lowercase handlers."""
    invalid = []
    lowercase_model_names = {"int", "str", "tuple"}
    for visitor in VISITOR_CLASSES:
        handler_prefix = f"{visitor.visitor_method_prefix}_"
        for name, _method in inspect.getmembers(visitor, predicate=inspect.isfunction):
            if name.startswith("visit_"):
                invalid.append(f"{visitor.__name__}.{name}")
            if name == "_visit_not_supported" or not name.startswith(handler_prefix):
                continue
            model_name = name.removeprefix(handler_prefix)
            if model_name[:1].islower() and model_name not in lowercase_model_names:
                invalid.append(f"{visitor.__name__}.{name}")
    assert not invalid, "Use configured <prefix>_<ClassName> handlers:\n" + "\n".join(invalid)


def test_ir2ast_visitor_methods_own_their_conversion_bodies():
    """Keep semantic lowering in the visitor instead of one-line module-private shims."""
    invalid = []
    for name in (
        "_visit_SemanticModule",
        "_visit_ProcedureOverloadSet",
        "_visit_SemanticFunction",
        "_visit_SemanticClass",
        "_visit_SemanticArgument",
        "_visit_SemanticVariable",
    ):
        source = inspect.getsource(getattr(_SemanticIrToCodegenAstVisitor, name))
        for forbidden in ("_convert_", "_codegen_callback_argument("):
            if forbidden in source:
                invalid.append(f"_SemanticIrToCodegenAstVisitor.{name} uses {forbidden}")
    assert not invalid, "Move visitor conversion bodies onto _SemanticIrToCodegenAstVisitor:\n" + "\n".join(invalid)


def test_parser_entrypoints_are_not_misnamed_as_visitors():
    """Keep source parsing under ``parse_*`` and reserve visitors for model nodes."""
    invalid = [
        f"{parser.__name__}.{name}"
        for parser in (FortranParser, CParser)
        for name in vars(parser)
        if name.startswith("visit_")
    ]
    assert not invalid, "Source entrypoints must use parse_* names:\n" + "\n".join(invalid)


def test_fortran_source_unit_classes_have_matching_handlers():
    """Require every sliced grammar-unit class to have one matching visitor."""
    assert all(issubclass(unit_type, SourceUnit) for unit_type in _SOURCE_UNIT_TYPES.values())
    assert {
        kind: f"_visit_{unit_type.__name__}"
        for kind, unit_type in _SOURCE_UNIT_TYPES.items()
        if not hasattr(FortranParser, f"_visit_{unit_type.__name__}")
    } == {}


def test_shared_visitor_is_the_only_mro_dispatch_implementation():
    """Prevent local visitor loops from bypassing ``ClassVisitor``."""
    invalid = []
    for path in VISITOR_IMPLEMENTATION_PATHS:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in {"__mro__", "mro"}:
                invalid.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
    assert not invalid, "Use x2py.utilities.visitor.ClassVisitor instead of local MRO dispatch:\n" + "\n".join(invalid)
