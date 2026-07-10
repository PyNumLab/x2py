import builtins

from dataclasses import dataclass

import json

import os

import runpy

import subprocess

import sys

import types

from pathlib import Path

import pytest

from x2py.fortran_parser import cli as fortran_parser_cli

from x2py import FortranParseError

from x2py import cli as x2py_cli

from x2py.pipeline.preprocessing import PreprocessingConfig, PreprocessingDiagnostic, PreprocessingError

TEST_FILE = Path(__file__).parent.parent / "data" / "fortran" / "general" / "basic_subroutine.f90"


class _MainParserError(Exception):
    pass


def _main_args(**overrides):
    values = {
        "paths": ["input.f90"],
        "language": "fortran",
        "parse": False,
        "preprocessor_adapter": "auto",
        "compiler": None,
        "compile_commands": None,
        "preprocess_template": None,
        "include_dirs": [],
        "defines": [],
        "undefs": [],
        "std": None,
        "compiler_args": [],
        "c_type_report": None,
        "c_type_probe_runner": [],
        "c_type_probe_cache_dir": None,
        "refresh_c_type_probe": False,
        "fortran_type_report": None,
        "fortran_type_probe_runner": [],
        "fortran_type_probe_cache_dir": None,
        "refresh_fortran_type_probe": False,
        "include_exposure": "reachable-project",
        "public_includes": [],
        "private_includes": [],
        "show_vars": False,
        "print_limit": None,
        "vars_limit": None,
        "wrap_readiness": False,
        "wrap": False,
        "makefile": False,
        "build_manifest": None,
        "native_fortran_sources": None,
        "native_fortran_flags": None,
        "native_objects": None,
        "native_libraries": None,
        "native_link_items": None,
        "native_library_dirs": None,
        "native_include_dirs": None,
        "strict_wrapper_names": False,
        "wrapper_compiler_debug": False,
        "wrapper_fortran_flags": None,
        "wrapper_c_flags": None,
        "semantics": False,
        "pyi": False,
        "json": False,
        "out": None,
        "out_dir": None,
        "verbose": False,
        "no_color": False,
        "debug": False,
    }
    values.update(overrides)
    return types.SimpleNamespace(**values)


def _install_main_parser(monkeypatch, args):
    class FakeParser:
        def add_argument(self, *_args, **_kwargs):
            pass

        def add_argument_group(self, *_args, **_kwargs):
            return self

        def parse_args(self):
            return args

        def error(self, message):
            raise _MainParserError(message)

    parser = FakeParser()
    monkeypatch.setattr(x2py_cli.argparse, "ArgumentParser", lambda *args, **kwargs: parser)
    return parser


def _patch_main_report_payloads(
    monkeypatch,
    *,
    language="fortran",
    parse_payload=None,
    semantic_payload=None,
    readiness_payload=None,
):
    preprocessing = object()
    calls = []
    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, _active_language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda args, parser: preprocessing)
    monkeypatch.setattr(
        x2py_cli,
        "_parse_report",
        lambda paths, active_preprocessing: calls.append(("parse", paths, active_preprocessing)) or parse_payload,
    )
    monkeypatch.setattr(
        x2py_cli,
        "_semantic_report",
        lambda paths, active_preprocessing, *, language: (
            calls.append(("semantic", paths, active_preprocessing, language)) or semantic_payload
        ),
    )
    monkeypatch.setattr(
        x2py_cli,
        "_wrap_readiness_report",
        lambda paths, active_preprocessing, *, language: (
            calls.append(("readiness", paths, active_preprocessing, language)) or readiness_payload
        ),
    )
    monkeypatch.setattr(
        x2py_cli,
        "_attach_wrap_readiness",
        lambda active_semantic_payload, active_readiness_payload: calls.append(
            ("attach", active_semantic_payload, active_readiness_payload)
        ),
    )
    return preprocessing, calls


__all__ = (
    "TEST_FILE",
    "FortranParseError",
    "Path",
    "PreprocessingConfig",
    "PreprocessingDiagnostic",
    "PreprocessingError",
    "_MainParserError",
    "_install_main_parser",
    "_main_args",
    "_patch_main_report_payloads",
    "builtins",
    "dataclass",
    "fortran_parser_cli",
    "json",
    "os",
    "pytest",
    "runpy",
    "subprocess",
    "sys",
    "types",
    "x2py_cli",
)
