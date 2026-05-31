# -*- coding: utf-8 -*-
"""Shared preprocessing CLI and compiler-command contract tests."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import x2py.preprocessing as preprocessing
from x2py.preprocessing import (
    PreprocessingError,
    PreprocessingConfig,
    build_compile_commands_invocation,
    build_direct_preprocess_invocation,
    build_preprocess_invocation,
    build_template_preprocess_invocation,
    expand_native_fortran_includes,
    run_compiler_preprocessor,
    run_compiler_preprocessor_with_recipe,
    validate_macro_name,
)


def _fake_compiler(tmp_path: Path, output: str) -> tuple[Path, Path, dict[str, str]]:
    script = tmp_path / "fake-cc"
    args_file = tmp_path / "compiler-args.txt"
    script.write_text(
        f"""#!{sys.executable}
import os
import pathlib
import sys

pathlib.Path(os.environ["X2PY_FAKE_COMPILER_ARGS"]).write_text("\\n".join(sys.argv[1:]), encoding="utf-8")
sys.stdout.write(os.environ["X2PY_FAKE_COMPILER_OUTPUT"])
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    env = {
        **os.environ,
        "X2PY_FAKE_COMPILER_ARGS": str(args_file),
        "X2PY_FAKE_COMPILER_OUTPUT": output,
    }
    return script, args_file, env


def _failing_compiler(tmp_path: Path, stderr: str) -> Path:
    script = tmp_path / "failing-cc"
    script.write_text(
        f"""#!{sys.executable}
import sys

sys.stderr.write({stderr!r})
sys.exit(1)
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_direct_c_preprocess_invocation_uses_exact_compiler_and_flags(tmp_path: Path):
    source = tmp_path / "api.h"
    config = PreprocessingConfig(
        mode="compiler",
        compiler="/usr/bin/clang-18",
        include_dirs=["include", "/opt/sdk/include"],
        defines=["API_EXPORT=", "USE_FAST"],
        undefs=["DEBUG"],
        std="c11",
        compiler_args=["--sysroot=/opt/sdk", "-target", "x86_64-linux-gnu"],
    )

    invocation = build_direct_preprocess_invocation(source, language="c", config=config)

    assert invocation.argv == [
        "/usr/bin/clang-18",
        "-E",
        "-x",
        "c",
        "-Iinclude",
        "-I/opt/sdk/include",
        "-DAPI_EXPORT=",
        "-DUSE_FAST",
        "-UDEBUG",
        "-std=c11",
        "--sysroot=/opt/sdk",
        "-target",
        "x86_64-linux-gnu",
        str(source),
    ]


def test_direct_fortran_preprocess_invocation_uses_exact_compiler_and_cpp(tmp_path: Path):
    source = tmp_path / "solver.F90"
    config = PreprocessingConfig(
        mode="compiler",
        compiler="/usr/bin/gfortran-12",
        include_dirs=["include"],
        defines=["USE_MPI"],
        undefs=["DEBUG"],
        std="f2018",
    )

    invocation = build_direct_preprocess_invocation(source, language="fortran", config=config)

    assert invocation.argv == [
        "/usr/bin/gfortran-12",
        "-E",
        "-cpp",
        "-Iinclude",
        "-DUSE_MPI",
        "-UDEBUG",
        "-std=f2018",
        str(source),
    ]


def test_preprocessing_config_internal_macros_recipe_and_validation(tmp_path: Path):
    source = tmp_path / "source.F90"
    plain = PreprocessingConfig()
    selected = PreprocessingConfig(defines=["USE_MPI", "VALUE=3"], undefs=["DEBUG"])

    assert plain.uses_compiler is False
    assert plain.fortran_internal_recipe(source) is None
    assert selected.fortran_internal_recipe(source)["source_path"] == str(source)
    with pytest.raises(PreprocessingError, match="requires a macro name"):
        validate_macro_name("=value", "--define")
    with pytest.raises(PreprocessingError, match="requires a macro name"):
        validate_macro_name("", "--define")
    with pytest.raises(PreprocessingError, match="invalid macro name"):
        validate_macro_name("bad-name", "--define")


def test_preprocessing_metadata_models_and_adapter_helpers(tmp_path: Path):
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    diagnostic = preprocessing.PreprocessingDiagnostic(
        category="PREPROCESSOR_FAILED",
        message="bad flag",
        path=str(source),
        line=3,
        command=["cc", "-E"],
    )
    included = preprocessing.IncludedFile(
        path=str(tmp_path / "public.h"),
        included_by=str(source),
        include_line=1,
    )
    mapping = preprocessing.SourceMapping(
        generated_line=2,
        original_path=str(source),
        original_line=7,
        include_stack=[str(source)],
    )
    macro = preprocessing.MacroDefinition(
        name="SQR",
        value="((x) * (x))",
        function_like=True,
        parameters=["x"],
        path=str(source),
        line=4,
    )
    plan = preprocessing.PreprocessingPlan(
        language="c",
        source_path=str(source),
        adapter="direct",
        compiler="cc",
        include_dirs=["include"],
        defines=["API=1"],
        undefs=["DEBUG"],
        standard="c11",
        compiler_args=["-Wall"],
    )
    result = preprocessing.PreprocessResult(
        source="#define SQR(x) ((x) * (x))\n",
        recipe={"mode": "compiler"},
        included_files=[included],
        source_mappings=[mapping],
        macros=[macro],
        diagnostics=[diagnostic],
    )
    recipe = preprocessing.PreprocessingRecipe(language="c", compiler="cc", standard="c11")

    assert diagnostic.to_dict()["command"] == ["cc", "-E"]
    assert plan.to_dict()["include_dirs"] == ["include"]
    assert result.to_dict()["macros"][0]["parameters"] == ["x"]
    assert recipe.std == "c11"

    adapter = preprocessing.GCCCompatibleCAdapter()
    config = PreprocessingConfig(mode="compiler", compiler="cc")
    assert adapter.build_preprocess_invocation(source, language="c", config=config).argv[0] == "cc"
    assert adapter.collect_dependencies(result) == [included]
    assert adapter.collect_macros(result) == [macro]
    assert adapter.parse_linemarkers('#line 7 "dir\\\\api\\".h"\nint x;\n')[0].original_line == 7

    invocation = preprocessing.CommandTemplateAdapter().build_preprocess_invocation(
        source,
        language="c",
        config=PreprocessingConfig(
            mode="compiler",
            compiler="vendor-cc",
            adapter="command-template",
            command_template="{compiler} --lang {language} {source}",
        ),
    )
    assert invocation.argv == ["vendor-cc", "--lang", "c", str(source)]
    assert preprocessing.GNUFortranAdapter().name == "gnu-fortran"


def test_direct_preprocess_invocation_rejects_missing_compiler_and_unknown_language(tmp_path: Path):
    source = tmp_path / "input.txt"
    with pytest.raises(PreprocessingError, match="requires --compiler"):
        build_direct_preprocess_invocation(source, language="c", config=PreprocessingConfig(mode="compiler"))
    with pytest.raises(PreprocessingError, match="not supported for language"):
        build_direct_preprocess_invocation(
            source,
            language="rust",
            config=PreprocessingConfig(mode="compiler", compiler="cc"),
        )


def test_compile_commands_invocation_uses_database_compiler_and_filters_compile_only_args(tmp_path: Path):
    source = tmp_path / "src" / "api.c"
    source.parent.mkdir()
    source.write_text("int api(void);\n", encoding="utf-8")
    fake_compiler = tmp_path / "toolchains" / "gcc-13"
    fake_compiler.parent.mkdir()
    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps(
            [
                {
                    "directory": str(tmp_path),
                    "file": str(source),
                    "arguments": [
                        str(fake_compiler),
                        "-Iproject/include",
                        "-DPROJECT_API=",
                        "-c",
                        str(source),
                        "-o",
                        "api.o",
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    config = PreprocessingConfig(mode="compiler", compile_commands=str(database), defines=["CLI_DEFINE=1"])

    invocation = build_compile_commands_invocation(source, config=config)

    assert invocation.cwd == str(tmp_path)
    assert invocation.argv == [
        str(fake_compiler),
        "-E",
        "-DCLI_DEFINE=1",
        "-Iproject/include",
        "-DPROJECT_API=",
        str(source),
    ]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("not json", "invalid compile commands JSON"),
        ("{}", "must contain a list"),
        ("[]", "no compile_commands entry found"),
        (
            '[{"directory": ".", "file": "api.c", "arguments": ["cc"]}, {"directory": ".", "file": "api.c", "arguments": ["cc"]}]',
            "multiple compile_commands entries",
        ),
        ('[{"directory": ".", "arguments": ["cc"]}]', "missing 'file'"),
        ('[{"directory": ".", "file": "api.c", "arguments": "cc -c api.c"}]', "'arguments' must contain a list"),
        ('[{"directory": ".", "file": "api.c", "command": ["cc"]}]', "'command' must contain a string"),
        ('[{"directory": ".", "file": "api.c"}]', "must contain 'arguments' or 'command'"),
        ('[{"directory": ".", "file": "api.c", "arguments": []}]', "empty command"),
        ("[1]", "entries must be objects"),
    ],
)
def test_compile_commands_invocation_reports_invalid_database_entries(tmp_path: Path, payload: str, message: str):
    source = tmp_path / "api.c"
    database = tmp_path / "compile_commands.json"
    source.write_text("int api(void);\n", encoding="utf-8")
    database.write_text(payload.replace('"directory": "."', f'"directory": "{tmp_path}"'), encoding="utf-8")

    with pytest.raises(PreprocessingError, match=message):
        build_compile_commands_invocation(
            source,
            config=PreprocessingConfig(mode="compiler", compile_commands=str(database)),
        )


def test_compile_commands_invocation_reports_missing_file_and_supports_command_strings(tmp_path: Path):
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    with pytest.raises(PreprocessingError, match="database path is missing"):
        build_compile_commands_invocation(source, config=PreprocessingConfig(mode="compiler"))

    missing = tmp_path / "absent.json"
    with pytest.raises(PreprocessingError, match="cannot read compile commands file"):
        build_compile_commands_invocation(
            source,
            config=PreprocessingConfig(mode="compiler", compile_commands=str(missing)),
        )

    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps(
            [{"directory": str(tmp_path), "file": str(source), "command": f"cc -c {source} -oapi.o /Fowindows.obj"}]
        ),
        encoding="utf-8",
    )
    invocation = build_compile_commands_invocation(
        source,
        config=PreprocessingConfig(mode="compiler", compile_commands=str(database), compiler="clang"),
    )
    assert invocation.argv == ["clang", "-E", str(source)]


def test_compile_commands_filters_dependency_and_windows_compile_flags(tmp_path: Path):
    source = tmp_path / "src" / "api.c"
    source.parent.mkdir()
    source.write_text("int api(void);\n", encoding="utf-8")
    compiler = tmp_path / "cc"
    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps(
            [
                {
                    "directory": str(tmp_path),
                    "file": str(source),
                    "arguments": [
                        str(compiler),
                        "-MF",
                        "deps.d",
                        "-MT",
                        "api.o",
                        "-MQtarget",
                        "-MFdeps2.d",
                        "/c",
                        "src/api.c",
                        "-Wall",
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )

    invocation = build_compile_commands_invocation(
        source,
        config=PreprocessingConfig(mode="compiler", compile_commands=str(database)),
    )

    assert invocation.argv == [str(compiler), "-E", "-Wall", str(source)]


def test_build_preprocess_invocation_supports_fortran_compile_database(tmp_path: Path):
    source = tmp_path / "solver.F90"
    source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")
    compiler = tmp_path / "toolchains" / "gfortran-13"
    compiler.parent.mkdir()
    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps(
            [
                {
                    "directory": str(tmp_path),
                    "file": str(source),
                    "arguments": [
                        str(compiler),
                        "-Iproject/include",
                        "-cpp",
                        "-c",
                        str(source),
                        "-o",
                        "solver.o",
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )

    invocation = build_preprocess_invocation(
        source,
        language="fortran",
        config=PreprocessingConfig(mode="compiler", compile_commands=str(database)),
    )

    assert invocation.argv == [
        str(compiler),
        "-E",
        "-cpp",
        "-Iproject/include",
        "-cpp",
        str(source),
    ]


def test_command_template_preprocess_invocation_expands_placeholders(tmp_path: Path):
    source = tmp_path / "api.h"
    config = PreprocessingConfig(
        mode="compiler",
        adapter="command-template",
        command_template="vendor-cc --preprocess {include_dirs} {defines} {undefs} {standard} {compiler_args} {source}",
        include_dirs=["include"],
        defines=["API_EXPORT="],
        undefs=["DEBUG"],
        std="c11",
        compiler_args=["--target=x86_64-linux"],
    )

    invocation = build_template_preprocess_invocation(source, language="c", config=config)

    assert invocation.argv == [
        "vendor-cc",
        "--preprocess",
        "-Iinclude",
        "-DAPI_EXPORT=",
        "-UDEBUG",
        "-std=c11",
        "--target=x86_64-linux",
        str(source),
    ]


def test_command_template_validation_and_dispatch_edges(tmp_path: Path):
    source = tmp_path / "api.h"
    source.write_text("int api(void);\n", encoding="utf-8")

    with pytest.raises(PreprocessingError, match="requires --preprocess-template"):
        build_template_preprocess_invocation(
            source,
            language="c",
            config=PreprocessingConfig(mode="compiler", adapter="command-template"),
        )
    with pytest.raises(PreprocessingError, match="expanded to an empty command"):
        build_template_preprocess_invocation(
            source,
            language="c",
            config=PreprocessingConfig(
                mode="compiler",
                adapter="command-template",
                command_template="''",
            ),
        )

    invocation = build_preprocess_invocation(
        source,
        language="c",
        config=PreprocessingConfig(
            mode="compiler",
            compiler="vendor-cc",
            adapter="command-template",
            command_template="{compiler} {language} --std={standard} {source}",
            std="c99",
        ),
    )

    assert invocation.argv == ["vendor-cc", "c", "--std=c99", str(source)]


def test_linemarker_dependency_exposure_and_macro_edges(tmp_path: Path):
    root = tmp_path / "root.c"
    source = "\n".join(
        [
            '#line 7 "src\\\\api\\".h"',
            "int from_line;",
            '# 1 "<built-in>" 1 3',
            "#define BUILTIN 1",
            '# 2 "<built-in>" 2',
            '# 2 "src/api.h" 2',
            '# 1 "public/api.h" 1',
            "int public_api;",
            '# 1 "private/internal.h" 1',
            "int private_api;",
            '# 1 "project/hidden.h" 1',
            "int hidden_api;",
        ]
    )

    mappings = preprocessing.parse_linemarker_mappings(source, filename=str(root))
    macros = preprocessing._parse_macro_definitions(source, mappings)
    files = preprocessing._included_files_from_linemarkers(
        source,
        root_path=root,
        language="c",
        config=PreprocessingConfig(
            include_exposure="roots-only",
            public_includes=["public"],
            private_includes=["private"],
        ),
    )
    by_path = {item.path: item for item in files}

    assert mappings[0].original_line == 7
    assert 'api".h' in mappings[0].original_path
    assert preprocessing._unescape_linemarker_filename("trailing\\") == "trailing\\"
    assert preprocessing._dependency_kind("<command-line>") == "system"
    assert preprocessing._mapping_for_generated_line(mappings, mappings[0].generated_line, root) == mappings[0]
    fallback = preprocessing._mapping_for_generated_line([], 99, root)
    assert fallback.original_path == str(root)
    assert fallback.original_line == 99
    no_filename_mappings = preprocessing.parse_linemarker_mappings("#line 42\nint next;\n", filename=str(root))
    assert no_filename_mappings[0].original_path == str(root)
    assert no_filename_mappings[0].original_line == 42
    assert preprocessing._included_files_from_linemarkers(
        "#line 5\nint next;\n",
        root_path=root,
        language="c",
        config=PreprocessingConfig(),
    ) == [files[0]]
    assert macros[0].name == "BUILTIN"
    assert macros[0].builtin is True
    assert by_path[str(root)].dependency_kind == "root"
    assert by_path["<built-in>"].dependency_kind == "system"
    assert by_path["public/api.h"].exposure == "public"
    assert by_path["private/internal.h"].exposure == "private"
    assert by_path["project/hidden.h"].exposure == "private"


def test_native_fortran_include_expansion_is_recursive_and_preserves_duplicates(tmp_path: Path):
    root = tmp_path / "src" / "root.F90"
    include = root.parent / "decls.inc"
    nested = root.parent / "nested.inc"
    root.parent.mkdir()
    root.write_text('module m\ninclude "decls.inc"\ninclude "decls.inc"\nend module m\n', encoding="utf-8")
    include.write_text('include "nested.inc"\ninteger :: from_decls\n', encoding="utf-8")
    nested.write_text("real :: from_nested\n", encoding="utf-8")

    expanded, included_files, mappings, diagnostics = expand_native_fortran_includes(
        root.read_text(encoding="utf-8"),
        root_path=root,
        include_dirs=[],
    )

    assert diagnostics == []
    assert expanded.count("integer :: from_decls") == 2
    assert expanded.count("real :: from_nested") == 2
    assert [Path(item.path).name for item in included_files].count("decls.inc") == 2
    assert any(Path(mapping.original_path).name == "nested.inc" for mapping in mappings)


def test_native_fortran_include_lookup_order_missing_and_cycle_diagnostics(tmp_path: Path):
    root = tmp_path / "src" / "root.F90"
    include_dir = tmp_path / "include"
    root.parent.mkdir()
    include_dir.mkdir()
    root.write_text('include "shared.inc"\n', encoding="utf-8")
    (root.parent / "shared.inc").write_text("integer :: relative_wins\n", encoding="utf-8")
    (include_dir / "shared.inc").write_text("integer :: include_dir_loses\n", encoding="utf-8")

    expanded, _included_files, _mappings, diagnostics = expand_native_fortran_includes(
        root.read_text(encoding="utf-8"),
        root_path=root,
        include_dirs=[str(include_dir)],
    )

    assert diagnostics == []
    assert "relative_wins" in expanded
    assert "include_dir_loses" not in expanded

    missing_source = 'include "absent.inc"\n'
    _expanded, _included_files, _mappings, diagnostics = expand_native_fortran_includes(
        missing_source,
        root_path=root,
        include_dirs=[str(include_dir)],
    )
    assert [diagnostic.category for diagnostic in diagnostics] == ["INCLUDE_NOT_FOUND"]

    cycle_a = root.parent / "a.inc"
    cycle_b = root.parent / "b.inc"
    cycle_a.write_text('include "b.inc"\n', encoding="utf-8")
    cycle_b.write_text('include "a.inc"\n', encoding="utf-8")
    _expanded, _included_files, _mappings, diagnostics = expand_native_fortran_includes(
        'include "a.inc"\n',
        root_path=root,
        include_dirs=[],
    )
    assert "INCLUDE_CYCLE" in [diagnostic.category for diagnostic in diagnostics]


def test_native_fortran_include_reports_files_that_disappear_before_read(monkeypatch, tmp_path: Path):
    root = tmp_path / "root.F90"
    include = tmp_path / "vanished.inc"
    root.write_text('include "vanished.inc"\n', encoding="utf-8")
    include.write_text("integer :: vanished\n", encoding="utf-8")
    original_read_text = Path.read_text

    def fail_for_include(path: Path, *args, **kwargs):
        if path == include:
            raise OSError("disappeared")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_for_include)

    expanded, included_files, _mappings, diagnostics = expand_native_fortran_includes(
        root.read_text(encoding="utf-8"),
        root_path=root,
        include_dirs=[],
    )

    assert expanded.startswith(f'# 1 "{include}" 1')
    assert [Path(item.path) for item in included_files] == [include]
    assert [diagnostic.category for diagnostic in diagnostics] == ["INCLUDE_NOT_FOUND"]
    assert "could not be read" in diagnostics[0].message


def test_run_compiler_preprocessor_success_and_failures(monkeypatch, tmp_path: Path):
    config = PreprocessingConfig(mode="compiler", compiler="cc")
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 0, "stdout": "expanded", "stderr": ""})(),
    )
    expanded, recipe = run_compiler_preprocessor_with_recipe(source, language="c", config=config)
    assert expanded == "expanded"
    assert recipe.compiler == "cc"
    assert run_compiler_preprocessor(source, language="c", config=config) == "expanded"

    def raise_oserror(*_args, **_kwargs):
        raise OSError("cannot start")

    monkeypatch.setattr(preprocessing.subprocess, "run", raise_oserror)
    with pytest.raises(PreprocessingError, match="failed to run compiler preprocessor"):
        run_compiler_preprocessor(source, language="c", config=config)

    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 1, "stdout": "", "stderr": "bad option"})(),
    )
    with pytest.raises(PreprocessingError, match="compiler preprocessing failed"):
        run_compiler_preprocessor(source, language="c", config=config)


def test_preprocess_source_error_paths_and_fortran_include_diagnostics(monkeypatch, tmp_path: Path):
    c_source = tmp_path / "api.c"
    c_source.write_text("int api(void);\n", encoding="utf-8")

    with pytest.raises(PreprocessingError, match="not configured"):
        preprocessing.preprocess_source(c_source, language="c", config=PreprocessingConfig())
    with pytest.raises(PreprocessingError, match="preprocessor not found"):
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler="x2py-definitely-missing-preprocessor"),
        )

    def raise_file_not_found(*_args, **_kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(preprocessing.subprocess, "run", raise_file_not_found)
    with pytest.raises(PreprocessingError, match="preprocessor not found"):
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler=str(tmp_path / "missing-cc")),
        )

    def raise_timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="cc", timeout=60)

    monkeypatch.setattr(preprocessing.subprocess, "run", raise_timeout)
    with pytest.raises(PreprocessingError, match="timed out"):
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler=str(tmp_path / "slow-cc")),
        )

    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 2, "stdout": "", "stderr": ""})(),
    )
    with pytest.raises(PreprocessingError, match="exit code 2"):
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler=str(tmp_path / "bad-cc")),
        )

    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 0, "stdout": "", "stderr": ""})(),
    )
    result = preprocessing.preprocess_source(
        c_source,
        language="c",
        config=PreprocessingConfig(
            mode="compiler",
            adapter="command-template",
            command_template=f"{sys.executable} {{source}}",
        ),
    )
    assert [diagnostic.category for diagnostic in result.diagnostics] == ["PROVENANCE_UNAVAILABLE"]

    fortran_source = tmp_path / "solver.F90"
    fortran_source.write_text('include "missing.inc"\n', encoding="utf-8")
    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type(
            "Done", (), {"returncode": 0, "stdout": 'include "missing.inc"\n', "stderr": ""}
        )(),
    )
    with pytest.raises(PreprocessingError) as exc_info:
        preprocessing.preprocess_source(
            fortran_source,
            language="fortran",
            config=PreprocessingConfig(mode="compiler", compiler=str(tmp_path / "gfortran")),
        )
    assert exc_info.value.category == "INCLUDE_NOT_FOUND"


def test_cli_help_documents_exact_compiler_and_preprocessing_examples():
    res = subprocess.run(
        [sys.executable, "-m", "x2py", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "--preprocess {internal,compiler}" in res.stdout
    assert "--compiler COMPILER" in res.stdout
    assert "gcc-13" in res.stdout
    assert "clang-18" in res.stdout
    assert "/usr/bin/gfortran-12" in res.stdout
    assert "--compile-commands build/compile_commands.json" in res.stdout
    assert "-D USE_MPI" in res.stdout


def test_cli_c_internal_mode_accepts_include_dirs_for_raw_include_resolution(tmp_path: Path):
    include_dir = tmp_path / "include"
    include_dir.mkdir()
    dependency = include_dir / "types.h"
    header = tmp_path / "api.h"
    dependency.write_text("typedef int api_int;\n", encoding="utf-8")
    header.write_text('#include "types.h"\nint run(void);\n', encoding="utf-8")

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--parse",
            "--json",
            "-I",
            str(include_dir),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(res.stdout)[str(header)]

    assert payload["preprocessing"] == "raw"
    assert payload["includes"][0]["resolved_path"] == str(dependency)


def test_cli_c_internal_mode_rejects_define_flags_that_need_compiler_selection(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int run(void);\n", encoding="utf-8")

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--parse",
            "-D",
            "USE_FAST",
        ],
        capture_output=True,
        text=True,
    )

    assert res.returncode == 2
    assert "raw C parsing rejects unresolved preprocessing directives" in res.stderr


def test_cli_compiler_mode_requires_exact_compiler_or_compile_database(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int run(void);\n", encoding="utf-8")

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--parse",
            "--preprocess",
            "compiler",
        ],
        capture_output=True,
        text=True,
    )

    assert res.returncode == 2
    assert "requires --compiler with an exact executable" in res.stderr


def test_cli_compiler_specific_flags_require_compiler_mode(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int run(void);\n", encoding="utf-8")

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--parse",
            "--compiler",
            "gcc-13",
        ],
        capture_output=True,
        text=True,
    )

    assert res.returncode == 2
    assert "--compiler requires --preprocess compiler" in res.stderr


def test_cli_accepts_compile_database_for_fortran_compiler_mode(tmp_path: Path):
    source = tmp_path / "solver.F90"
    source.write_text("subroutine solve()\nend subroutine solve\n", encoding="utf-8")
    compiler, _args_file, env = _fake_compiler(
        tmp_path,
        "subroutine from_database()\nend subroutine from_database\n",
    )
    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps(
            [
                {
                    "directory": str(tmp_path),
                    "file": str(source),
                    "arguments": [str(compiler), "-cpp", "-c", str(source), "-o", "solver.o"],
                }
            ]
        ),
        encoding="utf-8",
    )

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--parse",
            "--json",
            "--preprocess",
            "compiler",
            "--compile-commands",
            str(database),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )

    payload = json.loads(res.stdout)[str(source)]
    assert [signature["name"] for signature in payload["signatures"]] == ["from_database"]
    assert payload["preprocessing_recipe"]["compile_commands"] == str(database)


def test_cli_c_compiler_mode_runs_exact_compiler_and_parses_preprocessed_stdout(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("#define API(ret) ret\nAPI(int) hidden(void);\n", encoding="utf-8")
    compiler, args_file, env = _fake_compiler(tmp_path, '# 44 "include/api.h"\nint expanded(void);\n')

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--parse",
            "--json",
            "--preprocess",
            "compiler",
            "--compiler",
            str(compiler),
            "-I",
            "include",
            "-D",
            "API_EXPORT=",
            "-U",
            "DEBUG",
            "--std",
            "c11",
            "--compiler-arg=--sysroot=/opt/sdk",
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    payload = json.loads(res.stdout)[str(header)]
    compiler_args = args_file.read_text(encoding="utf-8").splitlines()

    assert payload["preprocessing"] == "compiler"
    assert [fn["name"] for fn in payload["functions"]] == ["expanded"]
    assert payload["functions"][0]["origin"] == "preprocessed"
    assert payload["functions"][0]["source_location"]["filename"] == "include/api.h"
    assert payload["functions"][0]["source_location"]["line"] == 44
    assert compiler_args == [
        "-E",
        "-x",
        "c",
        "-Iinclude",
        "-DAPI_EXPORT=",
        "-UDEBUG",
        "-std=c11",
        "--sysroot=/opt/sdk",
        str(header),
    ]
    recipe = payload["preprocessing_recipe"]
    assert recipe["mode"] == "compiler"
    assert recipe["language"] == "c"
    assert recipe["source_path"] == str(header)
    assert recipe["compiler"] == str(compiler)
    assert recipe["argv"] == [str(compiler), *compiler_args]
    assert recipe["include_dirs"] == ["include"]
    assert recipe["defines"] == ["API_EXPORT="]
    assert recipe["undefs"] == ["DEBUG"]
    assert recipe["standard"] == "c11"
    assert recipe["compiler_args"] == ["--sysroot=/opt/sdk"]
    assert recipe["compile_commands"] is None
    assert recipe["compile_commands_entry"] is None
    assert payload["original_source_paths"] == ["include/api.h"]


def test_cli_preprocessing_failure_has_category_without_traceback_unless_debug(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("int run(void);\n", encoding="utf-8")
    compiler = _failing_compiler(tmp_path, "bad option\n")

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--parse",
            "--preprocess",
            "compiler",
            "--compiler",
            str(compiler),
        ],
        capture_output=True,
        text=True,
    )
    debug_res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--parse",
            "--preprocess",
            "compiler",
            "--compiler",
            str(compiler),
            "--debug",
        ],
        capture_output=True,
        text=True,
    )

    assert res.returncode == 1
    assert "error[PREPROCESSOR_FAILED]" in res.stderr
    assert "bad option" in res.stderr
    assert "Traceback" not in res.stderr
    assert debug_res.returncode == 1
    assert "Traceback" in debug_res.stderr


def test_cli_c_compile_commands_mode_uses_exact_database_compiler(tmp_path: Path):
    source = tmp_path / "api.c"
    source.write_text("API(int) hidden(void);\n", encoding="utf-8")
    compiler, args_file, env = _fake_compiler(tmp_path, '#line 12 "generated/api.h"\nint from_database(void);\n')
    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps(
            [
                {
                    "directory": str(tmp_path),
                    "file": str(source),
                    "arguments": [
                        str(compiler),
                        "-Iproject/include",
                        "-DPROJECT_API=",
                        "-c",
                        str(source),
                        "-o",
                        "api.o",
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--language",
            "c",
            "--parse",
            "--json",
            "--preprocess",
            "compiler",
            "--compile-commands",
            str(database),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    payload = json.loads(res.stdout)[str(source)]
    compiler_args = args_file.read_text(encoding="utf-8").splitlines()

    assert [fn["name"] for fn in payload["functions"]] == ["from_database"]
    assert payload["functions"][0]["source_location"]["filename"] == "generated/api.h"
    assert payload["functions"][0]["source_location"]["line"] == 12
    assert compiler_args == ["-E", "-Iproject/include", "-DPROJECT_API=", str(source)]
    recipe = payload["preprocessing_recipe"]
    assert recipe["compiler"] == str(compiler)
    assert recipe["argv"] == [str(compiler), *compiler_args]
    assert recipe["cwd"] == str(tmp_path)
    assert recipe["compile_commands"] == str(database)
    assert recipe["compile_commands_entry"]["file"] == str(source)
    assert recipe["compile_commands_entry"]["arguments"][0] == str(compiler)


def test_cli_c_compiler_mode_macro_metadata_flows_to_semantic_constants(tmp_path: Path):
    header = tmp_path / "api.h"
    header.write_text("#define API_VERSION 3\nint api(void);\n", encoding="utf-8")
    compiler, _args_file, env = _fake_compiler(
        tmp_path,
        "#define API_VERSION 3\nint api(void);\n",
    )

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(header),
            "--language",
            "c",
            "--semantics",
            "--json",
            "--preprocess",
            "compiler",
            "--compiler",
            str(compiler),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )

    module = json.loads(res.stdout)[str(header)]["semantic_modules"][0]
    constants = {variable["name"]: variable for variable in module["variables"]}
    assert constants["API_VERSION"]["default_value"] == "3"


def test_cli_fortran_internal_mode_rejects_define_flags_that_need_compiler_selection(tmp_path: Path):
    source = tmp_path / "branch.F90"
    source.write_text(
        """
#ifdef USE_MPI
subroutine selected()
end subroutine selected
#else
subroutine fallback()
end subroutine fallback
#endif
""".strip(),
        encoding="utf-8",
    )

    res = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse", "-D", "USE_MPI"],
        capture_output=True,
        text=True,
    )

    assert res.returncode == 2
    assert "raw Fortran CPP directives require compiler preprocessing" in res.stderr


def test_cli_fortran_internal_json_does_not_record_macro_selection_recipe(tmp_path: Path):
    source = tmp_path / "branch.F90"
    source.write_text(
        "subroutine selected()\nend subroutine selected\n",
        encoding="utf-8",
    )

    res = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "preprocessing_recipe" not in json.loads(res.stdout)[str(source)]


def test_cli_fortran_internal_mode_rejects_include_dirs_that_need_compiler(tmp_path: Path):
    source = tmp_path / "mini.F90"
    source.write_text("subroutine work()\nend subroutine work\n", encoding="utf-8")

    res = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse", "-I", "include"],
        capture_output=True,
        text=True,
    )

    assert res.returncode == 2
    assert "affects Fortran only with --preprocess compiler" in res.stderr


def test_cli_fortran_compiler_mode_runs_exact_compiler_and_parses_stdout(tmp_path: Path):
    source = tmp_path / "generated.F90"
    source.write_text("#define MAKE_SUBROUTINE name\n", encoding="utf-8")
    compiler, args_file, env = _fake_compiler(
        tmp_path,
        "subroutine from_compiler()\nend subroutine from_compiler\n",
    )

    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--parse",
            "--json",
            "--preprocess",
            "compiler",
            "--compiler",
            str(compiler),
            "-I",
            "include",
            "-D",
            "USE_MPI",
            "-U",
            "DEBUG",
            "--std",
            "f2018",
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    compiler_args = args_file.read_text(encoding="utf-8").splitlines()
    payload = json.loads(res.stdout)[str(source)]

    assert [signature["name"] for signature in payload["signatures"]] == ["from_compiler"]
    assert compiler_args == [
        "-E",
        "-cpp",
        "-Iinclude",
        "-DUSE_MPI",
        "-UDEBUG",
        "-std=f2018",
        str(source),
    ]
    recipe = payload["preprocessing_recipe"]
    assert recipe["mode"] == "compiler"
    assert recipe["language"] == "fortran"
    assert recipe["compiler"] == str(compiler)
    assert recipe["argv"] == [str(compiler), *compiler_args]
    assert recipe["include_dirs"] == ["include"]
    assert recipe["defines"] == ["USE_MPI"]
    assert recipe["undefs"] == ["DEBUG"]
    assert recipe["standard"] == "f2018"
