"""Tests split by stable ownership concept from `test_readiness_reports.py`."""

from tests.cli._cli_support import (
    Path,
    PreprocessingError,
    TEST_FILE,
    _MainParserError,
    _install_main_parser,
    _main_args,
    json,
    pytest,
    subprocess,
    sys,
    types,
    x2py_cli,
)


def test_cli_pyi_out_rejects_ambiguous_single_file_contract_package(tmp_path: Path):
    source = tmp_path / "combined.f90"
    source.write_text(
        """module first_mod
contains
  subroutine first()
  end subroutine first
end module first_mod

module second_mod
contains
  subroutine second()
  end subroutine second
end module second_mod
""",
        encoding="utf-8",
    )
    output = tmp_path / "combined.pyi"

    cmd = [sys.executable, "-m", "x2py", str(source), "--pyi", "--out", str(output)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode != 0
    assert "generated contracts use one file per module" in result.stderr
    assert not output.exists()


def test_cli_rejects_conflicting_json_and_pyi_out_from_inline_code(tmp_path: Path):
    f90 = tmp_path / "conflict.f90"
    f90.write_text(
        """module conflict_mod
contains
  subroutine ping()
  end subroutine ping
end module conflict_mod
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(f90), "--pyi", "--json", "--out", str(tmp_path / "out")]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 2
    assert "--out cannot be used with both --json and --pyi" in res.stderr


def test_x2py_pyi_report_formats_and_rejects_conflicting_dependency_stubs():
    report = {
        "first.f90": {
            "pyi": "def first() -> None: ...",
            "pyi_dependencies": {"shared": "class shared(Opaque):\n    pass"},
        },
        "second.f90": {
            "pyi": "def second() -> None: ...",
            "pyi_dependencies": {
                "shared": "class shared(Opaque):\n    pass",
                "extra": "class extra(Opaque):\n    pass",
            },
        },
        "empty.f90": {},
    }

    text = x2py_cli._format_pyi_report(report)

    assert (
        text
        == """File: first.f90
def first() -> None: ...

Dependency stub: shared.pyi
class shared(Opaque):
    pass

File: second.f90
def second() -> None: ...

Dependency stub: extra.pyi
class extra(Opaque):
    pass

File: empty.f90
<no module declarations found>"""
    )
    with pytest.raises(ValueError, match="Conflicting generated dependency stub"):
        x2py_cli._write_pyi_dependencies(
            {
                "first.f90": {"pyi_dependencies": {"shared": "class shared:\n    pass"}},
                "second.f90": {"pyi_dependencies": {"shared": "class shared:\n    value: int"}},
            }
        )


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        (
            {"language": "c"},
            "--language c requires a stage flag: choose one of --parse, --semantics, --pyi, --wrap-readiness, or --wrap",
        ),
        (
            {"language": "c", "parse": True, "show_vars": True},
            "--show-vars is Fortran-only and is not supported for --language c",
        ),
        (
            {"out": ""},
            "--out for wrapper builds requires an output name",
        ),
        (
            {"out": "module.txt"},
            "--out for wrapper builds expects NAME or NAME.so",
        ),
        (
            {"out": "bad-name"},
            "--out for wrapper builds expects a valid Python module name",
        ),
        (
            {"out": "module", "makefile": True},
            "--out names a compiled wrapper extension and cannot be combined with --makefile",
        ),
        (
            {"makefile": True, "verbose": True},
            "--makefile cannot be combined with --verbose",
        ),
        (
            {"parse": True, "semantics": True},
            "Choose exactly one stage flag; cannot combine --parse, --semantics",
        ),
        (
            {"parse": True, "pyi": True},
            "Choose exactly one stage flag; cannot combine --parse, --pyi",
        ),
        (
            {"parse": True, "wrap_readiness": True},
            "Choose exactly one stage flag; cannot combine --parse, --wrap-readiness",
        ),
        (
            {"parse": True, "wrap": True},
            "Choose exactly one stage flag; cannot combine --parse, --wrap",
        ),
        (
            {"semantics": True, "pyi": True},
            "Choose exactly one stage flag; cannot combine --semantics, --pyi",
        ),
        (
            {"semantics": True, "wrap_readiness": True},
            "Choose exactly one stage flag; cannot combine --semantics, --wrap-readiness",
        ),
        (
            {"semantics": True, "wrap": True},
            "Choose exactly one stage flag; cannot combine --semantics, --wrap",
        ),
        (
            {"pyi": True, "wrap_readiness": True},
            "Choose exactly one stage flag; cannot combine --pyi, --wrap-readiness",
        ),
        (
            {"pyi": True, "wrap": True},
            "Choose exactly one stage flag; cannot combine --pyi, --wrap",
        ),
        (
            {"wrap_readiness": True, "wrap": True},
            "Choose exactly one stage flag; cannot combine --wrap-readiness, --wrap",
        ),
        ({"show_vars": True}, "--show-vars/--print-limit require --parse"),
        ({"print_limit": 1}, "--show-vars/--print-limit require --parse"),
        ({"vars_limit": 1}, "--show-vars/--print-limit require --parse"),
        ({"parse": True, "print_limit": -1}, "--print-limit must be >= 0"),
        ({"parse": True, "c_type_report": "types.json"}, "C type probe options require --language c"),
        (
            {"language": "c", "parse": True, "refresh_c_type_probe": True},
            "C type probe options require --semantics, --pyi, or --wrap-readiness",
        ),
        (
            {"language": "c", "semantics": True, "c_type_report": "types.json", "refresh_c_type_probe": True},
            "--c-type-report cannot be combined with automatic C type probe options",
        ),
        (
            {"language": "c", "semantics": True, "fortran_type_report": "types.json"},
            "Fortran type probe options require --language fortran",
        ),
        (
            {"parse": True, "refresh_fortran_type_probe": True},
            "Fortran type probe options require --semantics, --pyi, --wrap-readiness, or --wrap",
        ),
        (
            {"semantics": True, "fortran_type_report": "types.json", "refresh_fortran_type_probe": True},
            "--fortran-type-report cannot be combined with automatic Fortran type probe options",
        ),
        (
            {"paths": ["input.pyi"]},
            "A .pyi wrapper build requires --native-fortran-sources, --native-objects, "
            "--native-library, or --native-link-item",
        ),
    ],
)
def test_x2py_main_preserves_validation_diagnostics(monkeypatch, overrides, expected):
    args = _main_args(**overrides)
    _install_main_parser(monkeypatch, args)
    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: object())

    with pytest.raises(_MainParserError) as exc_info:
        x2py_cli.main()

    assert str(exc_info.value) == expected


def test_x2py_main_collects_many_native_inputs_from_one_option_group(
    monkeypatch,
    tmp_path: Path,
    capsys,
):
    contract = tmp_path / "module.pyi"
    contract.write_text("def scale(x: float) -> float: ...\n", encoding="utf-8")
    build_dir = tmp_path / "build"
    calls = []
    result = types.SimpleNamespace(
        to_dict=lambda: {
            "module_name": "module",
            "shared_library": str(build_dir / "module.so"),
        }
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "x2py",
            str(contract),
            "--native-fortran-sources",
            "source_one.f90",
            "source_two.f90",
            "--native-fortran-flags=-O2 -g0",
            "--native-objects",
            "one.o",
            "two.a",
            "libsolver.so",
            "--native-library",
            "blas",
            "lapack",
            "--native-link-item",
            "arg:-Wl,--start-group",
            "object:one.o",
            "arg:-Wl,--end-group",
            "--native-library-dir",
            "lib",
            "vendor/lib",
            "--native-include-dir",
            "mods",
            "vendor/mods",
            "--wrapper-compiler-debug",
            "--wrapper-fortran-flags=-fno-range-check -g0",
            "--wrapper-c-flags=-O0 -g0",
            "--out-dir",
            str(build_dir),
            "--json",
        ],
    )
    monkeypatch.setattr(
        x2py_cli,
        "_run_wrap_build_with_diagnostics",
        lambda active_args, active_preprocessing: calls.append((active_args, active_preprocessing)) or result,
    )

    assert x2py_cli.main() == 0

    assert len(calls) == 1
    active_args, _preprocessing = calls[0]
    assert active_args.paths == [str(contract)]
    assert active_args.native_fortran_sources == ["source_one.f90", "source_two.f90"]
    assert active_args.native_fortran_flags == ["-O2 -g0"]
    assert active_args.native_objects == ["one.o", "two.a", "libsolver.so"]
    assert active_args.native_libraries == ["blas", "lapack"]
    assert active_args.native_link_items == [
        "arg:-Wl,--start-group",
        "object:one.o",
        "arg:-Wl,--end-group",
    ]
    assert active_args.native_library_dirs == ["lib", "vendor/lib"]
    assert active_args.native_include_dirs == ["mods", "vendor/mods"]
    assert active_args.wrapper_compiler_debug is True
    assert active_args.wrapper_fortran_flags == ["-fno-range-check -g0"]
    assert active_args.wrapper_c_flags == ["-O0 -g0"]
    payload = json.loads(capsys.readouterr().out)
    assert payload["module_name"] == "module"


@pytest.mark.parametrize(
    "overrides",
    [
        {"paths": ["input.f90"]},
        {"paths": ["contract.pyi"], "native_objects": ["native.o"]},
        {"paths": ["input.f90"], "makefile": True},
        {"paths": [], "build_manifest": "build/x2py-build.json"},
    ],
)
def test_wrapper_inputs_select_the_default_build_stage(overrides):
    assert x2py_cli._stage_defaults_to_wrap(_main_args(**overrides))


def test_explicit_inspection_stage_prevents_default_wrapper_selection():
    assert not x2py_cli._stage_defaults_to_wrap(_main_args(parse=True))


def test_cli_native_fortran_flags_split_grouped_shell_words():
    assert x2py_cli._cli_native_fortran_flags(["-O2 -g0", "-DNAME='value with spaces'"]) == (
        "-O2",
        "-g0",
        "-DNAME=value with spaces",
    )


def test_cli_wrapper_flags_split_grouped_shell_words():
    assert x2py_cli._cli_wrapper_fortran_flags(["-O0 -g", "-DNAME='value with spaces'"]) == (
        "-O0",
        "-g",
        "-DNAME=value with spaces",
    )
    assert x2py_cli._cli_wrapper_c_flags(["-O1 -g0"]) == ("-O1", "-g0")


def test_cli_native_fortran_flags_reject_malformed_grouped_value():
    with pytest.raises(ValueError, match="Invalid --native-fortran-flags value"):
        x2py_cli._cli_native_fortran_flags(["'-O2"])


def test_cli_wrapper_flags_reject_malformed_grouped_value():
    with pytest.raises(ValueError, match="Invalid --wrapper-c-flags value"):
        x2py_cli._cli_wrapper_c_flags(["'-O0"])


def test_x2py_build_preprocessing_config_preserves_full_config_contract(monkeypatch):
    args = types.SimpleNamespace(
        defines=["USE_FAST=1"],
        undefs=["LEGACY"],
        compiler="cc",
        compile_commands="compile_commands.json",
        preprocessor_adapter="command-template",
        preprocess_template="{compiler} -E {source}",
        include_dirs=["include"],
        std="c11",
        compiler_args=["--target=test"],
        include_exposure="all-project",
        public_includes=["public.h"],
        private_includes=["private.h"],
        language="c",
    )
    config = types.SimpleNamespace(
        uses_compiler=True,
        command_template=args.preprocess_template,
        adapter=args.preprocessor_adapter,
        compiler=args.compiler,
        compile_commands=args.compile_commands,
        include_dirs=args.include_dirs,
    )
    calls = []

    class Parser:
        def error(self, message):
            raise AssertionError(message)

    def validate(value, option):
        calls.append(("validate", value, option))

    def build(**kwargs):
        calls.append(("build", kwargs))
        return config

    monkeypatch.setattr(x2py_cli, "validate_macro_name", validate)
    monkeypatch.setattr(x2py_cli, "PreprocessingConfig", build)

    assert x2py_cli._build_preprocessing_config(args, Parser()) is config
    assert calls == [
        ("validate", "USE_FAST=1", "--define/-D"),
        ("validate", "LEGACY", "--undef/-U"),
        (
            "build",
            {
                "mode": "compiler",
                "compiler": "cc",
                "compile_commands": "compile_commands.json",
                "adapter": "command-template",
                "command_template": "{compiler} -E {source}",
                "include_dirs": ["include"],
                "defines": ["USE_FAST=1"],
                "undefs": ["LEGACY"],
                "std": "c11",
                "compiler_args": ["--target=test"],
                "include_exposure": "all-project",
                "public_includes": ["public.h"],
                "private_includes": ["private.h"],
            },
        ),
    ]


def test_x2py_build_preprocessing_config_preserves_macro_validation_errors(monkeypatch):
    class Parser:
        def error(self, message):
            raise ValueError(message)

    def args(**overrides):
        values = {
            "defines": [],
            "undefs": [],
            "compiler": None,
            "compile_commands": None,
            "preprocessor_adapter": "auto",
            "preprocess_template": None,
            "include_dirs": [],
            "std": None,
            "compiler_args": [],
            "include_exposure": "reachable-project",
            "public_includes": [],
            "private_includes": [],
            "language": "fortran",
        }
        values.update(overrides)
        return types.SimpleNamespace(**values)

    def reject(value, option):
        raise PreprocessingError(f"{option}: invalid {value}", category="INVALID_MACRO_NAME")

    monkeypatch.setattr(x2py_cli, "validate_macro_name", reject)

    with pytest.raises(ValueError) as define_error:
        x2py_cli._build_preprocessing_config(args(defines=["=bad"]), Parser())
    assert str(define_error.value) == "--define/-D: invalid =bad"

    with pytest.raises(ValueError) as undef_error:
        x2py_cli._build_preprocessing_config(args(undefs=["=bad"]), Parser())
    assert str(undef_error.value) == "--undef/-U: invalid =bad"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {"compiler": "cc", "preprocess_template": "{source}"},
            "--preprocess-template requires --preprocessor-adapter command-template",
        ),
    ],
)
def test_x2py_build_preprocessing_config_preserves_validation_diagnostics(overrides, message):
    values = {
        "defines": [],
        "undefs": [],
        "compiler": None,
        "compile_commands": None,
        "preprocessor_adapter": "auto",
        "preprocess_template": None,
        "include_dirs": [],
        "std": None,
        "compiler_args": [],
        "include_exposure": "reachable-project",
        "public_includes": [],
        "private_includes": [],
        "language": "fortran",
    }
    values.update(overrides)

    class Parser:
        def error(self, received):
            raise ValueError(received)

    with pytest.raises(ValueError) as error:
        x2py_cli._build_preprocessing_config(types.SimpleNamespace(**values), Parser())
    assert str(error.value) == message


def test_x2py_resolve_language_handles_requested_and_default_edges(tmp_path: Path):
    class ErrorParser:
        def error(self, message):
            raise ValueError(message)

    parser = ErrorParser()
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    c_header = tmp_path / "api.h"
    c_header.write_text("int add(int x);\n", encoding="utf-8")
    f_source = tmp_path / "solver.F90"
    f_source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")
    stub = tmp_path / "iface.PYI"
    stub.write_text("def solve() -> None: ...\n", encoding="utf-8")
    unknown = tmp_path / "notes.txt"
    unknown.write_text("notes\n", encoding="utf-8")

    assert x2py_cli._resolve_language([str(unknown)], "c", parser) == "c"
    with pytest.raises(ValueError) as requested_error:
        x2py_cli._resolve_language([str(input_dir), str(c_header)], "fortran", parser)
    assert str(requested_error.value) == (
        f"C input {c_header} is incompatible with --language fortran; pass --language c. Use --help for examples."
    )

    with pytest.raises(ValueError) as directory_error:
        x2py_cli._resolve_language([str(input_dir)], None, parser)
    assert str(directory_error.value) == (
        f"Input directory {input_dir} requires an explicit frontend; "
        "pass --language fortran or --language c. Use --help for examples."
    )

    assert x2py_cli._resolve_language([str(f_source)], None, parser) == "fortran"
    assert x2py_cli._resolve_language([str(stub)], None, parser) == "fortran"

    with pytest.raises(ValueError) as unknown_error:
        x2py_cli._resolve_language([str(unknown)], None, parser)
    assert str(unknown_error.value) == (
        f"Cannot determine the input language for {unknown}; "
        "pass --language fortran or --language c. Use --help for examples."
    )


def test_cli_wrapper_out_requires_name_for_default_wrap():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--out"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "--out for wrapper builds requires an output name" in res.stderr


def test_x2py_main_preserves_argument_parser_contract(monkeypatch):
    class StopAfterParserSetup(Exception):
        pass

    captured = {}

    class FakeArgumentGroup:
        def __init__(self, title: str):
            self.title = title

        def add_argument(self, *args, **kwargs):
            captured["arguments"].append((self.title, args, kwargs))

    class FakeParser:
        def __init__(self, *args, **kwargs):
            captured["parser"] = (args, kwargs)
            captured["groups"] = []
            captured["arguments"] = []

        def add_argument(self, *args, **kwargs):
            captured["arguments"].append(("parser", args, kwargs))

        def add_argument_group(self, title):
            captured["groups"].append(title)
            return FakeArgumentGroup(title)

        def parse_args(self):
            raise StopAfterParserSetup

    monkeypatch.setattr(x2py_cli.argparse, "ArgumentParser", FakeParser)

    with pytest.raises(StopAfterParserSetup):
        x2py_cli.main()

    assert captured["parser"] == (
        (),
        {
            "prog": "python3 -m x2py",
            "description": x2py_cli._CLI_HELP_DESCRIPTION,
            "formatter_class": x2py_cli.argparse.RawDescriptionHelpFormatter,
            "epilog": x2py_cli._CLI_HELP_EPILOG,
        },
    )
    assert captured["groups"] == [
        "input selection",
        "inspection stages",
        "compiler preprocessing",
        "target type probes",
        "C include exposure",
        "parse report controls",
        "wrapper builds",
        "output and diagnostics",
    ]
    assert [(group, args) for group, args, _ in captured["arguments"]] == [
        ("parser", ("paths",)),
        ("input selection", ("--language",)),
        ("inspection stages", ("--parse",)),
        ("inspection stages", ("--semantics",)),
        ("inspection stages", ("--pyi",)),
        ("inspection stages", ("--wrap-readiness",)),
        ("compiler preprocessing", ("--preprocessor-adapter",)),
        ("compiler preprocessing", ("--compiler",)),
        ("compiler preprocessing", ("--compile-commands",)),
        ("compiler preprocessing", ("--preprocess-template",)),
        ("compiler preprocessing", ("-I", "--include-dir")),
        ("compiler preprocessing", ("-D", "--define")),
        ("compiler preprocessing", ("-U", "--undef")),
        ("compiler preprocessing", ("--std",)),
        ("compiler preprocessing", ("--compiler-arg",)),
        ("target type probes", ("--c-type-report",)),
        ("target type probes", ("--c-type-probe-runner",)),
        ("target type probes", ("--c-type-probe-cache-dir",)),
        ("target type probes", ("--refresh-c-type-probe",)),
        ("target type probes", ("--fortran-type-report",)),
        ("target type probes", ("--fortran-type-probe-runner",)),
        ("target type probes", ("--fortran-type-probe-cache-dir",)),
        ("target type probes", ("--refresh-fortran-type-probe",)),
        ("C include exposure", ("--include-exposure",)),
        ("C include exposure", ("--public-include",)),
        ("C include exposure", ("--private-include",)),
        ("parse report controls", ("--show-vars",)),
        ("parse report controls", ("--print-limit",)),
        ("parse report controls", ("--vars-limit",)),
        ("wrapper builds", ("--wrap",)),
        ("wrapper builds", ("--makefile",)),
        ("wrapper builds", ("--strict-wrapper-names",)),
        ("wrapper builds", ("--wrapper-compiler-debug",)),
        ("wrapper builds", ("--wrapper-fortran-flags",)),
        ("wrapper builds", ("--wrapper-c-flags",)),
        ("wrapper builds", ("--build-manifest",)),
        ("wrapper builds", ("--native-fortran-sources",)),
        ("wrapper builds", ("--native-fortran-flags",)),
        ("wrapper builds", ("--native-objects",)),
        ("wrapper builds", ("--native-library",)),
        ("wrapper builds", ("--native-link-item",)),
        ("wrapper builds", ("--native-library-dir", "--library-dir")),
        ("wrapper builds", ("--native-include-dir",)),
        ("output and diagnostics", ("--json",)),
        ("output and diagnostics", ("--out",)),
        ("output and diagnostics", ("--out-dir",)),
        ("output and diagnostics", ("--verbose",)),
        ("output and diagnostics", ("--no-color",)),
        ("output and diagnostics", ("--debug", "--debug-traceback")),
    ]

    arguments_by_name = {args[0]: kwargs for _, args, kwargs in captured["arguments"]}
    assert arguments_by_name["paths"] == {
        "nargs": "*",
        "help": "Source file(s), .pyi file(s), or directory path(s); omit when using --build-manifest",
    }
    assert arguments_by_name["--language"] == {
        "choices": ("fortran", "c"),
        "default": None,
        "help": (
            "Frontend language. Omission is allowed for recognizable Fortran files and .pyi readiness input; "
            "C files, directories, and unknown-suffix source inputs require this flag."
        ),
    }
    assert arguments_by_name["--preprocessor-adapter"] == {
        "choices": ("auto", "gcc-compatible-c", "gnu-fortran", "command-template"),
        "default": "auto",
        "help": "Compiler adapter family. Use command-template for unsupported compiler families.",
    }
    assert arguments_by_name["--include-exposure"] == {
        "choices": ("reachable-project", "roots-only"),
        "default": "reachable-project",
        "help": "Public wrapper exposure policy for reachable included files.",
    }
    assert arguments_by_name["--vars-limit"] == {"type": int, "metavar": "N", "help": x2py_cli.argparse.SUPPRESS}
    assert arguments_by_name["--native-objects"] == {
        "dest": "native_objects",
        "action": "extend",
        "nargs": "+",
        "metavar": "PATH",
        "help": "Native object, static archive, or shared library paths linked into a .pyi wrapper build",
    }
    assert arguments_by_name["--native-fortran-sources"] == {
        "dest": "native_fortran_sources",
        "action": "extend",
        "nargs": "+",
        "metavar": "PATH",
        "help": "Native Fortran implementation source paths compiled for a .pyi wrapper build",
    }
    assert arguments_by_name["--native-fortran-flags"] == {
        "dest": "native_fortran_flags",
        "action": "extend",
        "nargs": "+",
        "metavar": "FLAG",
        "help": "Fortran compiler flags applied to each source passed with --native-fortran-sources",
    }
    assert arguments_by_name["--wrapper-compiler-debug"] == {
        "action": "store_true",
        "help": "Use the compiler debug profile for direct wrapper builds instead of the default release profile",
    }
    assert arguments_by_name["--wrapper-fortran-flags"] == {
        "dest": "wrapper_fortran_flags",
        "action": "extend",
        "nargs": "+",
        "metavar": "FLAG",
        "help": "Fortran compiler flags appended to generated wrapper bridge compilation commands",
    }
    assert arguments_by_name["--wrapper-c-flags"] == {
        "dest": "wrapper_c_flags",
        "action": "extend",
        "nargs": "+",
        "metavar": "FLAG",
        "help": "C compiler flags appended to generated CPython wrapper compilation commands",
    }
    assert arguments_by_name["--native-library"] == {
        "dest": "native_libraries",
        "action": "extend",
        "nargs": "+",
        "metavar": "NAME",
        "help": "Native libraries linked into a .pyi wrapper build, passed as -lNAME unless already prefixed",
    }
    assert arguments_by_name["--native-link-item"] == {
        "dest": "native_link_items",
        "action": "extend",
        "nargs": "+",
        "metavar": "KIND:VALUE",
        "help": "Ordered native link items for .pyi builds: object, archive, shared-library, library, or arg",
    }
    assert arguments_by_name["--native-library-dir"] == {
        "dest": "native_library_dirs",
        "action": "extend",
        "nargs": "+",
        "metavar": "DIR",
        "help": "Directories searched and added to rpath for native libraries in a .pyi wrapper build",
    }
    assert arguments_by_name["--native-include-dir"] == {
        "dest": "native_include_dirs",
        "action": "extend",
        "nargs": "+",
        "metavar": "DIR",
        "help": "Directories containing native module/interface files needed to compile .pyi wrapper bridges",
    }
    assert arguments_by_name["--debug"] == {
        "dest": "debug",
        "action": "store_true",
        "help": "Re-raise parser errors so Python prints a traceback for parser debugging",
    }


def test_cli_requires_explicit_language_for_directory_and_unknown_suffix(tmp_path: Path):
    source = tmp_path / "solver.source"
    source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")

    unknown = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse"],
        capture_output=True,
        text=True,
    )
    assert unknown.returncode == 2
    assert "Cannot determine the input language" in unknown.stderr
    assert "--language fortran or --language c" in unknown.stderr

    directory = subprocess.run(
        [sys.executable, "-m", "x2py", str(tmp_path), "--parse"],
        capture_output=True,
        text=True,
    )
    assert directory.returncode == 2
    assert "requires an explicit frontend" in directory.stderr

    explicit = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--language", "fortran", "--parse"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "subroutine solve" in explicit.stdout


def test_cli_rejects_fortran_file_with_explicit_c_frontend(tmp_path: Path):
    source = tmp_path / "solver.f90"
    source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--language", "c", "--parse"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "incompatible with --language c" in result.stderr
    assert "pass --language fortran" in result.stderr


def test_cli_fortran_rejects_embedded_c_declaration_outside_execution_body(tmp_path: Path):
    source = tmp_path / "solver.f90"
    source.write_text(
        "subroutine solve()\n  int add(int a, int b);\nend subroutine solve\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--pyi"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "PARSE_UNSUPPORTED_DECLARATION" in result.stderr
    assert "Unknown or unsupported datatype declaration" in result.stderr


def test_x2py_cli_defaults_pyi_to_wrapper_and_requires_native_implementation(tmp_path: Path):
    pyi = tmp_path / "module.pyi"
    pyi.write_text("def f() -> None: ...\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "x2py", str(pyi)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 2
    assert "A .pyi wrapper build requires --native-fortran-sources" in res.stderr


@pytest.mark.parametrize("macro_flag", ["-D", "-U"])
def test_x2py_main_rejects_invalid_macro_names(macro_flag: str, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x2py", str(TEST_FILE), "--parse", macro_flag, "=invalid"])
    with pytest.raises(SystemExit):
        x2py_cli.main()
