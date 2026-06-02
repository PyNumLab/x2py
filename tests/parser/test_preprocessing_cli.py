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


def _assert_preprocessing_error(
    exc_info: pytest.ExceptionInfo[PreprocessingError],
    *,
    message: str,
    category: str = "INVALID_COMPILER_ARGUMENTS",
) -> None:
    assert str(exc_info.value) == message
    assert exc_info.value.category == category
    assert exc_info.value.diagnostics == []


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

    assert invocation == preprocessing.Invocation(
        argv=[
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
        ],
        cwd=None,
        adapter="gcc-compatible-c",
        language="c",
        compiler="/usr/bin/clang-18",
        capabilities={"dependency_output": True, "macro_dump": True, "linemarkers": True},
    )


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

    assert invocation == preprocessing.Invocation(
        argv=[
            "/usr/bin/gfortran-12",
            "-E",
            "-cpp",
            "-Iinclude",
            "-DUSE_MPI",
            "-UDEBUG",
            "-std=f2018",
            str(source),
        ],
        cwd=None,
        adapter="gnu-fortran",
        language="fortran",
        compiler="/usr/bin/gfortran-12",
        capabilities={"dependency_output": True, "macro_dump": True, "linemarkers": True},
    )


def test_preprocessing_config_internal_macros_recipe_and_validation(tmp_path: Path):
    source = tmp_path / "source.F90"
    plain = PreprocessingConfig()
    selected = PreprocessingConfig(defines=["USE_MPI", "VALUE=3"], undefs=["DEBUG"])

    assert plain.uses_compiler is False
    assert plain.fortran_internal_recipe(source) is None
    assert selected.fortran_internal_recipe(source)["source_path"] == str(source)
    validate_macro_name("NAME", "--define")
    validate_macro_name("name", "--define")
    validate_macro_name("_NAME=value", "--define")
    validate_macro_name("_NAME=value=with=equals", "--define")
    with pytest.raises(PreprocessingError) as exc_info:
        validate_macro_name("=value", "--define")
    _assert_preprocessing_error(exc_info, message="--define requires a macro name before '='")
    with pytest.raises(PreprocessingError) as exc_info:
        validate_macro_name("", "--define")
    _assert_preprocessing_error(exc_info, message="--define requires a macro name")
    with pytest.raises(PreprocessingError) as exc_info:
        validate_macro_name("bad-name", "--define")
    _assert_preprocessing_error(
        exc_info,
        message="--define: invalid macro name 'bad-name'; must be a valid identifier",
    )


def test_preprocessing_error_default_category_and_diagnostics():
    diagnostic = preprocessing.PreprocessingDiagnostic(category="PREPROCESSOR_FAILED", message="bad")

    default_error = PreprocessingError("default")
    detailed_error = PreprocessingError("detailed", diagnostics=[diagnostic])

    assert default_error.category == "PREPROCESSOR_FAILED"
    assert default_error.diagnostics == []
    assert str(default_error) == "default"
    assert detailed_error.category == "PREPROCESSOR_FAILED"
    assert detailed_error.diagnostics == [diagnostic]
    assert str(detailed_error) == "detailed"


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

    assert diagnostic.to_dict() == {
        "category": "PREPROCESSOR_FAILED",
        "message": "bad flag",
        "severity": "error",
        "path": str(source),
        "line": 3,
        "command": ["cc", "-E"],
    }
    assert plan.to_dict() == {
        "language": "c",
        "source_path": str(source),
        "adapter": "direct",
        "compiler": "cc",
        "cwd": None,
        "include_dirs": ["include"],
        "defines": ["API=1"],
        "undefs": ["DEBUG"],
        "standard": "c11",
        "compiler_args": ["-Wall"],
        "compile_commands": None,
        "command_template": None,
    }
    assert included.to_dict() == {
        "path": str(tmp_path / "public.h"),
        "included_by": str(source),
        "include_line": 1,
        "mechanism": "cpp_include",
        "dependency_kind": "project",
        "exposure": "public",
    }
    assert mapping.to_dict() == {
        "generated_line": 2,
        "original_path": str(source),
        "original_line": 7,
        "include_stack": [str(source)],
    }
    assert macro.to_dict() == {
        "name": "SQR",
        "value": "((x) * (x))",
        "function_like": True,
        "parameters": ["x"],
        "path": str(source),
        "line": 4,
        "builtin": False,
    }
    assert result.to_dict() == {
        "source": "#define SQR(x) ((x) * (x))\n",
        "recipe": {"mode": "compiler"},
        "included_files": [included.to_dict()],
        "source_mappings": [mapping.to_dict()],
        "macros": [macro.to_dict()],
        "diagnostics": [diagnostic.to_dict()],
    }
    assert recipe.std == "c11"
    assert recipe.to_dict() == {
        "language": "c",
        "compiler": "cc",
        "mode": "compiler",
        "adapter": "direct",
        "argv": [],
        "cwd": None,
        "include_dirs": [],
        "defines": [],
        "undefs": [],
        "standard": "c11",
        "std": "c11",
        "compiler_args": [],
        "source_path": None,
        "source_file": None,
        "compile_commands": None,
        "compile_commands_entry": None,
        "command_template": None,
        "included_files": [],
        "source_mappings": [],
        "macros": [],
        "diagnostics": [],
        "capabilities": {},
    }

    adapter = preprocessing.GCCCompatibleCAdapter()
    config = PreprocessingConfig(mode="compiler", compiler="cc")
    assert adapter.build_preprocess_invocation(source, language="c", config=config) == preprocessing.Invocation(
        argv=["cc", "-E", "-x", "c", str(source)],
        cwd=None,
        adapter="gcc-compatible-c",
        language="c",
        compiler="cc",
        capabilities={"dependency_output": True, "macro_dump": True, "linemarkers": True},
    )
    assert adapter.collect_dependencies(result) == [included]
    assert adapter.collect_macros(result) == [macro]
    assert adapter.parse_linemarkers('#line 7 "dir\\\\api\\".h"\nint x;\n')[0].original_line == 7
    assert adapter.parse_linemarkers("int x;\n", filename="api.h")[0].original_path == "api.h"

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


def test_recipe_round_trip_preserves_all_preprocessing_metadata(monkeypatch, tmp_path: Path):
    source = tmp_path / "solver.F90"
    included = preprocessing.IncludedFile(
        path=str(tmp_path / "decls.inc"),
        included_by=str(source),
        include_line=2,
        mechanism="fortran_include",
        exposure="private",
    )
    mapping = preprocessing.SourceMapping(
        generated_line=3,
        original_path=included.path,
        original_line=1,
        include_stack=[str(source), included.path],
    )
    macro = preprocessing.MacroDefinition(name="USE_MPI", value="1", path=str(source), line=1)
    diagnostic = preprocessing.PreprocessingDiagnostic(
        category="PROVENANCE_UNAVAILABLE",
        message="no markers",
        severity="warning",
        command=["vendor-fc", "--expand"],
    )
    config = PreprocessingConfig(
        mode="compiler",
        include_dirs=["include"],
        defines=["USE_MPI=1"],
        undefs=["DEBUG"],
        std="f2018",
        compiler_args=["--dialect=strict"],
        command_template="{compiler} --expand {source}",
    )
    invocation = preprocessing.Invocation(
        argv=["vendor-fc", "--expand", str(source)],
        cwd=str(tmp_path),
        adapter="command-template",
        language="fortran",
        compiler="vendor-fc",
        compile_commands=str(tmp_path / "compile_commands.json"),
        compile_commands_entry={"directory": str(tmp_path), "file": str(source)},
        capabilities={"dependency_output": False, "macro_dump": False, "linemarkers": False},
    )
    result = preprocessing.PreprocessResult(
        source="expanded\n",
        recipe={},
        included_files=[included],
        source_mappings=[mapping],
        macros=[macro],
        diagnostics=[diagnostic],
    )
    expected = {
        "language": "fortran",
        "compiler": "vendor-fc",
        "mode": "compiler",
        "adapter": "command-template",
        "argv": ["vendor-fc", "--expand", str(source)],
        "cwd": str(tmp_path),
        "include_dirs": ["include"],
        "defines": ["USE_MPI=1"],
        "undefs": ["DEBUG"],
        "standard": "f2018",
        "std": "f2018",
        "compiler_args": ["--dialect=strict"],
        "source_path": str(source),
        "source_file": str(source),
        "compile_commands": str(tmp_path / "compile_commands.json"),
        "compile_commands_entry": {"directory": str(tmp_path), "file": str(source)},
        "command_template": "{compiler} --expand {source}",
        "included_files": [included.to_dict()],
        "source_mappings": [mapping.to_dict()],
        "macros": [macro.to_dict()],
        "diagnostics": [diagnostic.to_dict()],
        "capabilities": {"dependency_output": False, "macro_dump": False, "linemarkers": False},
    }

    recipe = preprocessing._recipe_from_invocation(source, "fortran", config, invocation, result)
    assert recipe.to_dict() == expected

    result.recipe = expected
    monkeypatch.setattr(preprocessing, "preprocess_source", lambda *_args, **_kwargs: result)
    expanded, restored = run_compiler_preprocessor_with_recipe(source, language="fortran", config=config)
    assert expanded == "expanded\n"
    assert restored.to_dict() == expected


def test_direct_preprocess_invocation_rejects_missing_compiler_and_unknown_language(tmp_path: Path):
    source = tmp_path / "input.txt"
    with pytest.raises(PreprocessingError) as exc_info:
        build_direct_preprocess_invocation(source, language="c", config=PreprocessingConfig(mode="compiler"))
    _assert_preprocessing_error(
        exc_info,
        message="c compiler preprocessing requires --compiler with an exact executable",
    )
    with pytest.raises(PreprocessingError) as exc_info:
        build_direct_preprocess_invocation(
            source,
            language="rust",
            config=PreprocessingConfig(mode="compiler", compiler="cc"),
        )
    _assert_preprocessing_error(
        exc_info,
        message="compiler preprocessing is not supported for language 'rust'",
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

    assert invocation == preprocessing.Invocation(
        argv=[
            str(fake_compiler),
            "-E",
            "-DCLI_DEFINE=1",
            "-Iproject/include",
            "-DPROJECT_API=",
            str(source),
        ],
        cwd=str(tmp_path),
        adapter="gcc-compatible-c",
        language="c",
        compiler=str(fake_compiler),
        compile_commands=str(database),
        compile_commands_entry={
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
        },
        capabilities={"dependency_output": True, "macro_dump": True, "linemarkers": True},
    )


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

    with pytest.raises(PreprocessingError, match=message) as exc_info:
        build_compile_commands_invocation(
            source,
            config=PreprocessingConfig(mode="compiler", compile_commands=str(database)),
        )
    assert exc_info.value.category == "INVALID_COMPILER_ARGUMENTS"
    assert exc_info.value.diagnostics == []


def test_compile_commands_invocation_reports_missing_file_and_supports_command_strings(tmp_path: Path):
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    with pytest.raises(PreprocessingError) as exc_info:
        build_compile_commands_invocation(source, config=PreprocessingConfig(mode="compiler"))
    _assert_preprocessing_error(exc_info, message="compile_commands database path is missing")

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


def test_compile_commands_internal_helpers_cover_paths_commands_and_selection(monkeypatch, tmp_path: Path):
    source = tmp_path / "src" / "api.c"
    source.parent.mkdir()
    source.write_text("int api(void);\n", encoding="utf-8")
    relative_entry = {"directory": str(tmp_path), "file": "src/api.c"}
    absolute_entry = {"directory": "/ignored", "file": str(source)}

    assert preprocessing._entry_file_path(relative_entry) == source
    assert preprocessing._entry_file_path(absolute_entry) == source
    assert preprocessing._entry_file_path({"file": "api.c"}) == Path("api.c")
    with pytest.raises(PreprocessingError) as exc_info:
        preprocessing._entry_file_path({})
    _assert_preprocessing_error(exc_info, message="compile_commands entry is missing 'file'")

    assert preprocessing._compile_command_argv({"arguments": ["cc", 7]}) == ["cc", "7"]
    assert preprocessing._compile_command_argv({"command": "cc -DNAME='two words' api.c"}) == [
        "cc",
        "-DNAME=two words",
        "api.c",
    ]
    for entry, message in [
        ({"arguments": "cc api.c"}, "compile_commands entry 'arguments' must contain a list"),
        ({"command": ["cc", "api.c"]}, "compile_commands entry 'command' must contain a string"),
        ({}, "compile_commands entry must contain 'arguments' or 'command'"),
        ({"arguments": []}, "compile_commands entry has an empty command"),
    ]:
        with pytest.raises(PreprocessingError) as exc_info:
            preprocessing._compile_command_argv(entry)
        _assert_preprocessing_error(exc_info, message=message)

    args = [
        "-c",
        "/c",
        "-o",
        "api.o",
        "-oother.o",
        "/Fowindows.obj",
        "-MF",
        "deps.d",
        "-MT",
        "api.o",
        "-MQ",
        "api.o",
        "-MFdeps2.d",
        "-MTapi",
        "-MQapi",
        "src/api.c",
        "-Wall",
    ]
    assert preprocessing._filter_compile_only_args(args, source, tmp_path) == ["-Wall"]
    assert preprocessing._compile_commands_entry(source, [relative_entry]) == relative_entry
    with pytest.raises(PreprocessingError) as exc_info:
        preprocessing._compile_commands_entry(source, [1])
    _assert_preprocessing_error(exc_info, message="compile_commands entries must be objects")

    original_resolve = Path.resolve

    def fail_resolve(path: Path):
        raise OSError(f"cannot resolve {path}")

    monkeypatch.setattr(Path, "resolve", fail_resolve)
    try:
        assert preprocessing._same_source(source, source)
    finally:
        monkeypatch.setattr(Path, "resolve", original_resolve)


def test_load_compile_commands_uses_explicit_utf8_and_exact_errors(monkeypatch, tmp_path: Path):
    database = tmp_path / "compile_commands.json"
    seen_encodings = []

    def read_empty_database(_path: Path, *, encoding: str):
        seen_encodings.append(encoding)
        return "[]"

    monkeypatch.setattr(Path, "read_text", read_empty_database)
    assert preprocessing._load_compile_commands(database) == []
    assert seen_encodings == ["utf-8"]

    def fail_read(_path: Path, *, encoding: str):
        raise OSError(f"denied with {encoding}")

    monkeypatch.setattr(Path, "read_text", fail_read)
    with pytest.raises(PreprocessingError) as exc_info:
        preprocessing._load_compile_commands(database)
    _assert_preprocessing_error(
        exc_info,
        message=f"cannot read compile commands file {database}: denied with utf-8",
    )

    monkeypatch.setattr(Path, "read_text", lambda _path, *, encoding: "not json")
    with pytest.raises(PreprocessingError) as exc_info:
        preprocessing._load_compile_commands(database)
    _assert_preprocessing_error(
        exc_info,
        message="invalid compile commands JSON: Expecting value: line 1 column 1 (char 0)",
    )

    monkeypatch.setattr(Path, "read_text", lambda _path, *, encoding: "{}")
    with pytest.raises(PreprocessingError) as exc_info:
        preprocessing._load_compile_commands(database)
    _assert_preprocessing_error(exc_info, message="compile_commands.json must contain a list")


@pytest.mark.parametrize(
    "compile_only_args",
    [
        ["-c"],
        ["/c"],
        ["-o", "api.o"],
        ["-oapi.o"],
        ["/Foapi.o"],
        ["-MF", "deps.d"],
        ["-MT", "api.o"],
        ["-MQ", "api.o"],
        ["-MFdeps.d"],
        ["-MTapi.o"],
        ["-MQapi.o"],
    ],
)
def test_compile_only_arg_filter_removes_each_flag_without_skipping_following_args(
    compile_only_args: list[str], tmp_path: Path
):
    source = tmp_path / "api.c"

    assert preprocessing._filter_compile_only_args([*compile_only_args, "-Wall"], source, tmp_path) == ["-Wall"]


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


def test_compile_commands_invocation_defaults_missing_directory_to_current_directory(tmp_path: Path):
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps([{"file": str(source), "arguments": ["cc", str(source)]}]),
        encoding="utf-8",
    )

    invocation = build_compile_commands_invocation(
        source,
        config=PreprocessingConfig(mode="compiler", compile_commands=str(database)),
    )

    assert invocation.cwd == "."
    assert invocation.argv == ["cc", "-E", str(source)]


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

    assert invocation == preprocessing.Invocation(
        argv=[
            str(compiler),
            "-E",
            "-cpp",
            "-Iproject/include",
            "-cpp",
            str(source),
        ],
        cwd=str(tmp_path),
        adapter="gnu-fortran",
        language="fortran",
        compiler=str(compiler),
        compile_commands=str(database),
        compile_commands_entry={
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
        },
        capabilities={"dependency_output": True, "macro_dump": True, "linemarkers": True},
    )


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

    assert invocation == preprocessing.Invocation(
        argv=[
            "vendor-cc",
            "--preprocess",
            "-Iinclude",
            "-DAPI_EXPORT=",
            "-UDEBUG",
            "-std=c11",
            "--target=x86_64-linux",
            str(source),
        ],
        adapter="command-template",
        language="c",
        compiler="vendor-cc",
        capabilities={"dependency_output": False, "macro_dump": False, "linemarkers": False},
    )


def test_command_template_tokens_expand_exactly(tmp_path: Path):
    source = tmp_path / "api.h"
    config = PreprocessingConfig(
        mode="compiler",
        compiler="vendor-cc",
        include_dirs=["include"],
        defines=["API=1"],
        undefs=["DEBUG"],
        std="c11",
        compiler_args=["--target=x86_64-linux"],
    )

    assert preprocessing._template_token_value("{source}", source, "c", config) == [str(source)]
    assert preprocessing._template_token_value("{compiler}", source, "c", config) == ["vendor-cc"]
    assert preprocessing._template_token_value("{language}", source, "c", config) == ["c"]
    assert preprocessing._template_token_value("{include_dirs}", source, "c", config) == ["-Iinclude"]
    assert preprocessing._template_token_value("{defines}", source, "c", config) == ["-DAPI=1"]
    assert preprocessing._template_token_value("{undefs}", source, "c", config) == ["-UDEBUG"]
    assert preprocessing._template_token_value("{standard}", source, "c", config) == ["-std=c11"]
    assert preprocessing._template_token_value("{compiler_args}", source, "c", config) == ["--target=x86_64-linux"]
    assert preprocessing._template_token_value("--std={standard}", source, "c", config) == ["--std=c11"]
    assert preprocessing._template_token_value(
        "--meta={source}:{compiler}:{language}:{standard}",
        source,
        "c",
        config,
    ) == [f"--meta={source}:vendor-cc:c:c11"]
    assert preprocessing._template_token_value("{standard}", source, "c", PreprocessingConfig()) == []
    assert preprocessing._template_token_value("{compiler}", source, "c", PreprocessingConfig()) == [""]
    assert preprocessing._template_token_value("{include_dirs}", source, "c", PreprocessingConfig()) == []
    assert preprocessing._template_token_value("{defines}", source, "c", PreprocessingConfig()) == []
    assert preprocessing._template_token_value("{undefs}", source, "c", PreprocessingConfig()) == []
    assert preprocessing._template_token_value("{compiler_args}", source, "c", PreprocessingConfig()) == []
    assert preprocessing._template_token_value(
        "--meta={compiler}:{standard}",
        source,
        "c",
        PreprocessingConfig(),
    ) == ["--meta=:"]
    with pytest.raises(KeyError, match="unknown"):
        preprocessing._template_token_value("{unknown}", source, "c", PreprocessingConfig())


def test_command_template_validation_and_dispatch_edges(tmp_path: Path):
    source = tmp_path / "api.h"
    source.write_text("int api(void);\n", encoding="utf-8")

    with pytest.raises(PreprocessingError, match="requires --preprocess-template"):
        build_template_preprocess_invocation(
            source,
            language="c",
            config=PreprocessingConfig(mode="compiler", adapter="command-template"),
        )
    with pytest.raises(PreprocessingError) as exc_info:
        build_template_preprocess_invocation(
            source,
            language="c",
            config=PreprocessingConfig(
                mode="compiler",
                adapter="command-template",
                command_template="''",
            ),
        )
    _assert_preprocessing_error(exc_info, message="custom command-template adapter expanded to an empty command")

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

    with pytest.raises(PreprocessingError) as exc_info:
        build_preprocess_invocation(
            source,
            language="c",
            config=PreprocessingConfig(mode="compiler", adapter="command-template"),
        )
    _assert_preprocessing_error(
        exc_info,
        message="custom command-template adapter requires --preprocess-template",
    )
    assert build_preprocess_invocation(
        source,
        language="c",
        config=PreprocessingConfig(mode="compiler", command_template="vendor-cc {source}"),
    ).argv == ["vendor-cc", str(source)]


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
    assert preprocessing._unescape_linemarker_filename(r"a\nb\rc\td\\e\"f\x") == 'a\nb\rc\td\\e"fx'
    assert preprocessing._unescape_linemarker_filename("trailing\\") == "trailing\\"
    assert preprocessing._parse_linemarker('# 12 "api.h" 1 3') == (12, "api.h", [1, 3])
    assert preprocessing._parse_linemarker("#line 14 api.h") == (14, "api.h", [])
    assert preprocessing._parse_linemarker("int api;") is None
    assert preprocessing._dependency_kind("api.h", [3]) == "system"
    assert preprocessing._dependency_kind("<command-line>") == "system"
    assert preprocessing._dependency_kind("api.h") == "project"
    assert preprocessing._exposure_for(
        "private/api.h", "project", PreprocessingConfig(private_includes=["private"])
    ) == ("private")
    assert preprocessing._exposure_for("public/api.h", "project", PreprocessingConfig(public_includes=["public"])) == (
        "public"
    )
    assert preprocessing._exposure_for("api.h", "system", PreprocessingConfig()) == "private"
    assert preprocessing._exposure_for("api.h", "project", PreprocessingConfig(include_exposure="roots-only")) == (
        "private"
    )
    assert preprocessing._exposure_for("api.h", "root", PreprocessingConfig(include_exposure="roots-only")) == "public"
    assert preprocessing._line_marker(3, 'dir\\api".h') == '# 3 "dir\\\\api\\".h"'
    assert preprocessing._line_marker(3, "api.h", 1) == '# 3 "api.h" 1'
    assert preprocessing._mapping_for_generated_line(mappings, mappings[0].generated_line, root) == mappings[0]
    fallback = preprocessing._mapping_for_generated_line([], 99, root)
    assert fallback.generated_line == 99
    assert fallback.original_path == str(root)
    assert fallback.original_line == 99
    assert fallback.include_stack == [str(root)]
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
    assert [mapping.to_dict() for mapping in mappings] == [
        {
            "generated_line": 2,
            "original_path": 'src\\api".h',
            "original_line": 7,
            "include_stack": ['src\\api".h'],
        },
        {
            "generated_line": 4,
            "original_path": "<built-in>",
            "original_line": 1,
            "include_stack": ['src\\api".h', "<built-in>"],
        },
        {
            "generated_line": 8,
            "original_path": "public/api.h",
            "original_line": 1,
            "include_stack": ["src/api.h", "public/api.h"],
        },
        {
            "generated_line": 10,
            "original_path": "private/internal.h",
            "original_line": 1,
            "include_stack": ["src/api.h", "public/api.h", "private/internal.h"],
        },
        {
            "generated_line": 12,
            "original_path": "project/hidden.h",
            "original_line": 1,
            "include_stack": ["src/api.h", "public/api.h", "private/internal.h", "project/hidden.h"],
        },
    ]
    assert [item.to_dict() for item in files] == [
        {
            "path": str(root),
            "included_by": None,
            "include_line": None,
            "mechanism": "c_include",
            "dependency_kind": "root",
            "exposure": "public",
        },
        {
            "path": "<built-in>",
            "included_by": 'src\\api".h',
            "include_line": 8,
            "mechanism": "c_include",
            "dependency_kind": "system",
            "exposure": "private",
        },
        {
            "path": "public/api.h",
            "included_by": "src/api.h",
            "include_line": 2,
            "mechanism": "c_include",
            "dependency_kind": "project",
            "exposure": "public",
        },
        {
            "path": "private/internal.h",
            "included_by": "public/api.h",
            "include_line": 2,
            "mechanism": "c_include",
            "dependency_kind": "project",
            "exposure": "private",
        },
        {
            "path": "project/hidden.h",
            "included_by": "private/internal.h",
            "include_line": 2,
            "mechanism": "c_include",
            "dependency_kind": "project",
            "exposure": "private",
        },
    ]
    assert [macro.to_dict() for macro in macros] == [
        {
            "name": "BUILTIN",
            "value": "1",
            "function_like": False,
            "parameters": None,
            "path": "<built-in>",
            "line": 1,
            "builtin": True,
        }
    ]


def test_linemarker_parser_accepts_bare_filename():
    assert preprocessing._parse_linemarker("# 14 api.h") == (14, "api.h", [])


def test_dependency_kind_requires_both_system_filename_brackets():
    assert preprocessing._dependency_kind("<api.h") == "project"
    assert preprocessing._dependency_kind("api.h>") == "project"


def test_line_marker_escapes_paths_and_omits_absent_flag():
    assert preprocessing._line_marker(3, 'dir\\api".h') == '# 3 "dir\\\\api\\".h"'


def test_linemarker_mapping_and_macro_helpers_cover_default_and_return_edges():
    source = "\n".join(
        [
            "int before;",
            '# 1 "same.h" 1',
            '# 2 "same.h" 1',
            "int nested;",
            '# 8 "root.c" 2',
            "int returned;",
            '# 3 "unknown.h" 2',
            "int unknown;",
            '# 9 "replacement.h"',
            "int replacement;",
            "#define EMPTY",
            "#define NOARGS() value",
            "#define ARGS(left, right) left + right",
        ]
    )

    mappings = preprocessing.parse_linemarker_mappings(source)

    assert mappings[0].to_dict() == {
        "generated_line": 1,
        "original_path": "<preprocessed>",
        "original_line": 1,
        "include_stack": ["<preprocessed>"],
    }
    assert mappings[1].include_stack == ["<preprocessed>", "same.h"]
    assert mappings[2].include_stack == ["root.c"]
    assert mappings[3].include_stack == ["unknown.h"]
    assert mappings[4].include_stack == ["replacement.h"]
    assert [macro.to_dict() for macro in preprocessing._parse_macro_definitions(source, mappings)] == [
        {
            "name": "EMPTY",
            "value": None,
            "function_like": False,
            "parameters": None,
            "path": "replacement.h",
            "line": 10,
            "builtin": False,
        },
        {
            "name": "NOARGS",
            "value": "value",
            "function_like": True,
            "parameters": [],
            "path": "replacement.h",
            "line": 11,
            "builtin": False,
        },
        {
            "name": "ARGS",
            "value": "left + right",
            "function_like": True,
            "parameters": ["left", "right"],
            "path": "replacement.h",
            "line": 12,
            "builtin": False,
        },
    ]
    assert preprocessing._parse_macro_definitions("#define UNMAPPED 1", []) == [
        preprocessing.MacroDefinition(name="UNMAPPED", value="1")
    ]


def test_linemarker_included_files_fortran_metadata_and_duplicate_entries(tmp_path: Path):
    root = tmp_path / "root.F90"
    source = "\n".join(
        [
            f'# 1 "{root}"',
            '# 1 "decls.inc" 1',
            "integer :: from_include",
            '# 1 "decls.inc" 1',
            '# 2 "unknown.inc" 2',
        ]
    )

    files = preprocessing._included_files_from_linemarkers(
        source,
        root_path=root,
        language="fortran",
        config=PreprocessingConfig(),
    )

    assert [item.to_dict() for item in files] == [
        {
            "path": str(root),
            "included_by": None,
            "include_line": None,
            "mechanism": "cpp_include",
            "dependency_kind": "root",
            "exposure": "public",
        },
        {
            "path": "decls.inc",
            "included_by": str(root),
            "include_line": 1,
            "mechanism": "cpp_include",
            "dependency_kind": "project",
            "exposure": "public",
        },
    ]


def test_linemarker_nested_returns_restore_parent_stack(tmp_path: Path):
    root = tmp_path / "root.F90"
    source = "\n".join(
        [
            f'# 1 "{root}"',
            '# 1 "one.inc" 1',
            '# 1 "two.inc" 1',
            '# 4 "one.inc" 2',
            '# 1 "sibling.inc" 1',
            "integer :: sibling_value",
        ]
    )

    mappings = preprocessing.parse_linemarker_mappings(source, filename=str(root))
    files = preprocessing._included_files_from_linemarkers(
        source,
        root_path=root,
        language="fortran",
        config=PreprocessingConfig(),
    )

    assert mappings == [
        preprocessing.SourceMapping(
            generated_line=6,
            original_path="sibling.inc",
            original_line=1,
            include_stack=[str(root), "one.inc", "sibling.inc"],
        )
    ]
    assert [(item.path, item.included_by) for item in files] == [
        (str(root), None),
        ("one.inc", str(root)),
        ("two.inc", "one.inc"),
        ("sibling.inc", "one.inc"),
    ]
    assert preprocessing._included_files_from_linemarkers(
        f'# 1 "{root}" 1',
        root_path=root,
        language="fortran",
        config=PreprocessingConfig(),
    ) == [
        preprocessing.IncludedFile(
            path=str(root),
            included_by=None,
            include_line=None,
            mechanism="cpp_include",
            dependency_kind="root",
            exposure="public",
        )
    ]
    direct_include = preprocessing._included_files_from_linemarkers(
        '# 1 "direct.inc" 1',
        root_path=root,
        language="fortran",
        config=PreprocessingConfig(),
    )[1]
    assert direct_include.included_by == str(root)
    assert direct_include.include_line == 1


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
    root_abs = str(root.resolve())
    include_abs = str(include.resolve())
    nested_abs = str(nested.resolve())
    assert expanded == "\n".join(
        [
            "module m",
            f'# 1 "{include_abs}" 1',
            f'# 1 "{nested_abs}" 1',
            "real :: from_nested",
            f'# 2 "{include_abs}" 2',
            "integer :: from_decls",
            f'# 3 "{root_abs}" 2',
            f'# 1 "{include_abs}" 1',
            f'# 1 "{nested_abs}" 1',
            "real :: from_nested",
            f'# 2 "{include_abs}" 2',
            "integer :: from_decls",
            f'# 4 "{root_abs}" 2',
            "end module m",
            "",
        ]
    )
    assert [item.to_dict() for item in included_files] == [
        {
            "path": include_abs,
            "included_by": root_abs,
            "include_line": 2,
            "mechanism": "fortran_include",
            "dependency_kind": "project",
            "exposure": "public",
        },
        {
            "path": nested_abs,
            "included_by": include_abs,
            "include_line": 1,
            "mechanism": "fortran_include",
            "dependency_kind": "project",
            "exposure": "public",
        },
        {
            "path": include_abs,
            "included_by": root_abs,
            "include_line": 3,
            "mechanism": "fortran_include",
            "dependency_kind": "project",
            "exposure": "public",
        },
        {
            "path": nested_abs,
            "included_by": include_abs,
            "include_line": 1,
            "mechanism": "fortran_include",
            "dependency_kind": "project",
            "exposure": "public",
        },
    ]
    assert [
        (mapping.generated_line, mapping.original_path, mapping.original_line, mapping.include_stack)
        for mapping in mappings
    ] == [
        (1, root_abs, 1, [root_abs]),
        (2, root_abs, 2, [root_abs]),
        (3, include_abs, 1, [include_abs]),
        (4, nested_abs, 1, [nested_abs]),
        (5, include_abs, 1, [include_abs]),
        (6, include_abs, 2, [include_abs]),
        (7, root_abs, 2, [root_abs]),
        (8, root_abs, 3, [root_abs]),
        (9, include_abs, 1, [include_abs]),
        (10, nested_abs, 1, [nested_abs]),
        (11, include_abs, 1, [include_abs]),
        (12, include_abs, 2, [include_abs]),
        (13, root_abs, 3, [root_abs]),
        (14, root_abs, 4, [root_abs]),
    ]


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
    assert [diagnostic.to_dict() for diagnostic in diagnostics] == [
        {
            "category": "INCLUDE_NOT_FOUND",
            "message": 'Fortran INCLUDE file "absent.inc" was not found',
            "severity": "error",
            "path": str(root.resolve()),
            "line": 1,
            "command": [],
        }
    ]

    cycle_a = root.parent / "a.inc"
    cycle_b = root.parent / "b.inc"
    cycle_a.write_text('include "b.inc"\n', encoding="utf-8")
    cycle_b.write_text('include "a.inc"\n', encoding="utf-8")
    _expanded, _included_files, _mappings, diagnostics = expand_native_fortran_includes(
        'include "a.inc"\n',
        root_path=root,
        include_dirs=[],
    )
    assert [diagnostic.to_dict() for diagnostic in diagnostics] == [
        {
            "category": "INCLUDE_CYCLE",
            "message": (
                f"Fortran INCLUDE cycle detected: {root.resolve()} -> {cycle_a.resolve()} -> "
                f"{cycle_b.resolve()} -> {cycle_a.resolve()}"
            ),
            "severity": "error",
            "path": str(cycle_b.resolve()),
            "line": 1,
            "command": [],
        }
    ]


def test_native_fortran_include_reports_files_that_disappear_before_read(monkeypatch, tmp_path: Path):
    root = tmp_path / "root.F90"
    include = tmp_path / "vanished.inc"
    root.write_text('include "vanished.inc"\n', encoding="utf-8")
    include.write_text("integer :: vanished\n", encoding="utf-8")
    original_read_text = Path.read_text

    seen_encodings = []

    def fail_for_include(path: Path, *args, **kwargs):
        if path == include:
            seen_encodings.append(kwargs["encoding"])
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
    assert seen_encodings == ["utf-8"]
    assert [diagnostic.to_dict() for diagnostic in diagnostics] == [
        {
            "category": "INCLUDE_NOT_FOUND",
            "message": 'Fortran INCLUDE file "vanished.inc" could not be read: disappeared',
            "severity": "error",
            "path": str(root.resolve()),
            "line": 1,
            "command": [],
        }
    ]


def test_native_fortran_include_resolution_continues_after_oserror(monkeypatch, tmp_path: Path):
    root = tmp_path / "src" / "root.F90"
    include_dir = tmp_path / "include"
    root.parent.mkdir()
    include_dir.mkdir()
    include = include_dir / "decls.inc"
    include.write_text("integer :: from_include_dir\n", encoding="utf-8")
    first_candidate = root.parent / "decls.inc"
    original_is_file = Path.is_file

    def fail_first_candidate(path: Path):
        if path == first_candidate:
            raise OSError("lookup failed")
        return original_is_file(path)

    monkeypatch.setattr(Path, "is_file", fail_first_candidate)

    expanded, included_files, _mappings, diagnostics = expand_native_fortran_includes(
        'include "decls.inc"\n',
        root_path=root,
        include_dirs=[str(include_dir)],
    )

    assert diagnostics == []
    assert "from_include_dir" in expanded
    assert [Path(item.path) for item in included_files] == [include]


def test_native_fortran_include_uses_absolute_fallback_when_resolve_fails(monkeypatch, tmp_path: Path):
    root = tmp_path / "root.F90"
    include = tmp_path / "decls.inc"
    include.write_text("integer :: value\n", encoding="utf-8")
    original_resolve = Path.resolve

    def fail_include_resolve(path: Path):
        if path == include:
            raise OSError("cannot resolve include")
        return original_resolve(path)

    monkeypatch.setattr(Path, "resolve", fail_include_resolve)

    expanded, included_files, _mappings, diagnostics = expand_native_fortran_includes(
        'include "decls.inc"\n',
        root_path=root,
        include_dirs=[],
    )

    assert diagnostics == []
    assert f'# 1 "{include.absolute()}" 1' in expanded
    assert [item.path for item in included_files] == [str(include.absolute())]


def test_native_fortran_include_diagnostics_do_not_drop_following_lines(monkeypatch, tmp_path: Path):
    root = tmp_path / "root.F90"
    cycle = tmp_path / "cycle.inc"
    vanished = tmp_path / "vanished.inc"
    cycle.write_text('include "cycle.inc"\ninteger :: after_cycle\n', encoding="utf-8")
    vanished.write_text("integer :: vanished\n", encoding="utf-8")
    original_read_text = Path.read_text

    def fail_for_vanished(path: Path, *args, **kwargs):
        if path == vanished:
            raise OSError("disappeared")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_for_vanished)

    expanded, _included_files, _mappings, diagnostics = expand_native_fortran_includes(
        'include "cycle.inc"\ninclude "vanished.inc"\ninteger :: after_read_error\n',
        root_path=root,
        include_dirs=[],
    )

    assert "after_cycle" in expanded
    assert "after_read_error" in expanded
    assert [diagnostic.category for diagnostic in diagnostics] == ["INCLUDE_CYCLE", "INCLUDE_NOT_FOUND"]


def test_native_fortran_include_expansion_preserves_input_linemarkers_and_private_exposure(tmp_path: Path):
    root = tmp_path / "root.F90"
    include = tmp_path / "private.inc"
    include.write_text("integer :: from_include\n", encoding="utf-8")
    source = f'# 40 "{root}"\ninclude "private.inc"'

    expanded, included_files, mappings, diagnostics = expand_native_fortran_includes(
        source,
        root_path=root,
        include_dirs=[],
        config=PreprocessingConfig(private_includes=["private"]),
    )

    assert diagnostics == []
    assert expanded == "\n".join(
        [
            f'# 40 "{root}"',
            f'# 1 "{include}" 1',
            "integer :: from_include",
            f'# 41 "{root}" 2',
        ]
    )
    assert [item.to_dict() for item in included_files] == [
        {
            "path": str(include),
            "included_by": str(root),
            "include_line": 40,
            "mechanism": "fortran_include",
            "dependency_kind": "project",
            "exposure": "private",
        }
    ]
    assert [(mapping.generated_line, mapping.original_path, mapping.original_line) for mapping in mappings] == [
        (1, str(root), 1),
        (2, str(root), 40),
        (3, str(include), 1),
        (4, str(root), 40),
    ]


def test_native_fortran_missing_include_does_not_drop_following_source(tmp_path: Path):
    root = tmp_path / "root.F90"

    expanded, included_files, mappings, diagnostics = expand_native_fortran_includes(
        'include "missing.inc"\ninteger :: retained\n',
        root_path=root,
        include_dirs=[],
    )

    assert expanded == "integer :: retained\n"
    assert included_files == []
    assert [(mapping.generated_line, mapping.original_path, mapping.original_line) for mapping in mappings] == [
        (1, str(root), 2)
    ]
    assert [diagnostic.to_dict() for diagnostic in diagnostics] == [
        {
            "category": "INCLUDE_NOT_FOUND",
            "message": 'Fortran INCLUDE file "missing.inc" was not found',
            "severity": "error",
            "path": str(root),
            "line": 1,
            "command": [],
        }
    ]


def test_run_compiler_preprocessor_success_and_failures(monkeypatch, tmp_path: Path):
    config = PreprocessingConfig(mode="compiler", compiler="cc")
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    calls = []

    def succeed(*args, **kwargs):
        calls.append((args, kwargs))
        return type("Done", (), {"returncode": 0, "stdout": "expanded", "stderr": ""})()

    monkeypatch.setattr(preprocessing.subprocess, "run", succeed)
    expanded, recipe = run_compiler_preprocessor_with_recipe(source, language="c", config=config)
    assert expanded == "expanded"
    assert recipe.compiler == "cc"
    assert run_compiler_preprocessor(source, language="c", config=config) == "expanded"
    assert calls == [
        (
            (["cc", "-E", "-x", "c", str(source)],),
            {"cwd": None, "capture_output": True, "text": True, "timeout": 60, "check": False},
        ),
        (
            (["cc", "-E", "-x", "c", str(source)],),
            {"cwd": None, "capture_output": True, "text": True, "timeout": 60, "check": False},
        ),
    ]

    def raise_oserror(*_args, **_kwargs):
        raise OSError("cannot start")

    monkeypatch.setattr(preprocessing.subprocess, "run", raise_oserror)
    with pytest.raises(PreprocessingError) as exc_info:
        run_compiler_preprocessor(source, language="c", config=config)
    assert str(exc_info.value) == "failed to run compiler preprocessor: cannot start"
    assert exc_info.value.category == "PREPROCESSOR_FAILED"
    assert [diagnostic.to_dict() for diagnostic in exc_info.value.diagnostics] == [
        {
            "category": "PREPROCESSOR_FAILED",
            "message": "failed to run compiler preprocessor: cannot start",
            "severity": "error",
            "path": None,
            "line": None,
            "command": ["cc", "-E", "-x", "c", str(source)],
        }
    ]

    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 1, "stdout": "", "stderr": "bad option"})(),
    )
    with pytest.raises(PreprocessingError) as exc_info:
        run_compiler_preprocessor(source, language="c", config=config)
    assert str(exc_info.value) == "compiler preprocessing failed with exit code 1\nbad option"
    assert exc_info.value.category == "PREPROCESSOR_FAILED"
    assert [diagnostic.to_dict() for diagnostic in exc_info.value.diagnostics] == [
        {
            "category": "PREPROCESSOR_FAILED",
            "message": "bad option",
            "severity": "error",
            "path": None,
            "line": None,
            "command": ["cc", "-E", "-x", "c", str(source)],
        }
    ]


def test_preprocess_source_preserves_exact_success_metadata(monkeypatch, tmp_path: Path):
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    expanded = f'# 1 "{source}"\n#define API 1\nint value;\n'
    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 0, "stdout": expanded, "stderr": ""})(),
    )
    config = PreprocessingConfig(
        mode="compiler",
        compiler=str(tmp_path / "cc"),
        include_dirs=["include"],
        defines=["CLI=1"],
        undefs=["DEBUG"],
        std="c11",
        compiler_args=["-dD"],
    )

    result = preprocessing.preprocess_source(source, language="c", config=config)

    argv = [
        str(tmp_path / "cc"),
        "-E",
        "-x",
        "c",
        "-Iinclude",
        "-DCLI=1",
        "-UDEBUG",
        "-std=c11",
        "-dD",
        str(source),
    ]
    included_files = [
        {
            "path": str(source),
            "included_by": None,
            "include_line": None,
            "mechanism": "c_include",
            "dependency_kind": "root",
            "exposure": "public",
        }
    ]
    mappings = [
        {
            "generated_line": 2,
            "original_path": str(source),
            "original_line": 1,
            "include_stack": [str(source)],
        },
        {
            "generated_line": 3,
            "original_path": str(source),
            "original_line": 2,
            "include_stack": [str(source)],
        },
    ]
    macros = [
        {
            "name": "API",
            "value": "1",
            "function_like": False,
            "parameters": None,
            "path": str(source),
            "line": 1,
            "builtin": False,
        }
    ]
    recipe = {
        "language": "c",
        "compiler": str(tmp_path / "cc"),
        "mode": "compiler",
        "adapter": "gcc-compatible-c",
        "argv": argv,
        "cwd": None,
        "include_dirs": ["include"],
        "defines": ["CLI=1"],
        "undefs": ["DEBUG"],
        "standard": "c11",
        "std": "c11",
        "compiler_args": ["-dD"],
        "source_path": str(source),
        "source_file": str(source),
        "compile_commands": None,
        "compile_commands_entry": None,
        "command_template": None,
        "included_files": included_files,
        "source_mappings": mappings,
        "macros": macros,
        "diagnostics": [],
        "capabilities": {"dependency_output": True, "macro_dump": True, "linemarkers": True},
    }
    assert result.to_dict() == {
        "source": expanded,
        "recipe": recipe,
        "included_files": included_files,
        "source_mappings": mappings,
        "macros": macros,
        "diagnostics": [],
    }


def test_preprocess_source_preserves_plain_source_mapping_and_fortran_native_metadata(monkeypatch, tmp_path: Path):
    c_source = tmp_path / "api.c"
    fortran_source = tmp_path / "solver.F90"
    private_include = tmp_path / "private.inc"
    c_source.write_text("int api(void);\n", encoding="utf-8")
    fortran_source.write_text('include "private.inc"\n', encoding="utf-8")
    private_include.write_text("integer :: hidden\n", encoding="utf-8")

    outputs = iter(["int api(void);\n", 'include "private.inc"\n'])
    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 0, "stdout": next(outputs), "stderr": ""})(),
    )

    c_result = preprocessing.preprocess_source(
        c_source,
        language="c",
        config=PreprocessingConfig(mode="compiler", compiler=str(tmp_path / "cc")),
    )
    fortran_result = preprocessing.preprocess_source(
        fortran_source,
        language="fortran",
        config=PreprocessingConfig(
            mode="compiler",
            compiler=str(tmp_path / "gfortran"),
            private_includes=["private"],
        ),
    )

    assert c_result.source_mappings == [
        preprocessing.SourceMapping(
            generated_line=1,
            original_path=str(c_source),
            original_line=1,
            include_stack=[str(c_source)],
        )
    ]
    assert [item.to_dict() for item in fortran_result.included_files] == [
        {
            "path": str(fortran_source),
            "included_by": None,
            "include_line": None,
            "mechanism": "cpp_include",
            "dependency_kind": "root",
            "exposure": "public",
        },
        {
            "path": str(private_include),
            "included_by": str(fortran_source.resolve()),
            "include_line": 1,
            "mechanism": "fortran_include",
            "dependency_kind": "project",
            "exposure": "private",
        },
    ]
    assert fortran_result.source_mappings == [
        preprocessing.SourceMapping(
            generated_line=1,
            original_path=str(fortran_source.resolve()),
            original_line=1,
            include_stack=[str(fortran_source.resolve())],
        ),
        preprocessing.SourceMapping(
            generated_line=2,
            original_path=str(private_include),
            original_line=1,
            include_stack=[str(private_include)],
        ),
        preprocessing.SourceMapping(
            generated_line=3,
            original_path=str(fortran_source.resolve()),
            original_line=1,
            include_stack=[str(fortran_source.resolve())],
        ),
    ]


def test_preprocess_source_reparses_fortran_mapping_when_native_expansion_returns_none(monkeypatch, tmp_path: Path):
    source = tmp_path / "solver.F90"
    source.write_text("integer :: value\n", encoding="utf-8")
    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 0, "stdout": "ignored\n", "stderr": ""})(),
    )
    monkeypatch.setattr(
        preprocessing,
        "expand_native_fortran_includes",
        lambda *_args, **_kwargs: ("integer :: value\n", [], [], []),
    )

    result = preprocessing.preprocess_source(
        source,
        language="fortran",
        config=PreprocessingConfig(mode="compiler", compiler=str(tmp_path / "gfortran")),
    )

    assert result.source_mappings == [
        preprocessing.SourceMapping(
            generated_line=1,
            original_path=str(source),
            original_line=1,
            include_stack=[str(source)],
        )
    ]


def test_run_compiler_preprocessor_with_recipe_restores_sparse_recipe_defaults(monkeypatch, tmp_path: Path):
    source = tmp_path / "api.c"
    result = preprocessing.PreprocessResult(source="expanded\n", recipe={"language": "c"})
    monkeypatch.setattr(preprocessing, "preprocess_source", lambda *_args, **_kwargs: result)

    expanded, recipe = run_compiler_preprocessor_with_recipe(source, language="c", config=PreprocessingConfig())

    assert expanded == "expanded\n"
    assert recipe.mode == "compiler"
    assert recipe.adapter == "direct"


def test_preprocess_source_uses_compile_database_working_directory(monkeypatch, tmp_path: Path):
    source = tmp_path / "api.c"
    source.write_text("int api(void);\n", encoding="utf-8")
    compiler = tmp_path / "cc"
    database = tmp_path / "compile_commands.json"
    database.write_text(
        json.dumps([{"directory": str(tmp_path), "file": str(source), "arguments": [str(compiler), str(source)]}]),
        encoding="utf-8",
    )
    calls = []

    def succeed(*args, **kwargs):
        calls.append((args, kwargs))
        return type("Done", (), {"returncode": 0, "stdout": "int api(void);\n", "stderr": ""})()

    monkeypatch.setattr(preprocessing.subprocess, "run", succeed)

    result = preprocessing.preprocess_source(
        source,
        language="c",
        config=PreprocessingConfig(mode="compiler", compile_commands=str(database)),
    )

    assert result.source == "int api(void);\n"
    assert result.source_mappings == [
        preprocessing.SourceMapping(
            generated_line=1,
            original_path=str(source),
            original_line=1,
            include_stack=[str(source)],
        )
    ]
    assert calls == [
        (
            ([str(compiler), "-E", str(source)],),
            {"cwd": str(tmp_path), "capture_output": True, "text": True, "timeout": 60, "check": False},
        )
    ]


def test_preprocess_source_error_paths_and_fortran_include_diagnostics(monkeypatch, tmp_path: Path):
    c_source = tmp_path / "api.c"
    c_source.write_text("int api(void);\n", encoding="utf-8")

    with pytest.raises(PreprocessingError, match="not configured") as exc_info:
        preprocessing.preprocess_source(c_source, language="c", config=PreprocessingConfig())
    assert str(exc_info.value) == "Compiler preprocessing not configured"
    assert exc_info.value.category == "INVALID_COMPILER_ARGUMENTS"
    assert exc_info.value.diagnostics == []

    missing_name = "x2py-definitely-missing-preprocessor"
    with pytest.raises(PreprocessingError, match="preprocessor not found") as exc_info:
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler=missing_name),
        )
    assert exc_info.value.category == "PREPROCESSOR_NOT_FOUND"
    assert [diagnostic.to_dict() for diagnostic in exc_info.value.diagnostics] == [
        {
            "category": "PREPROCESSOR_NOT_FOUND",
            "message": f"preprocessor not found: {missing_name}",
            "severity": "error",
            "path": None,
            "line": None,
            "command": [missing_name, "-E", "-x", "c", str(c_source)],
        }
    ]

    def raise_file_not_found(*_args, **_kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(preprocessing.subprocess, "run", raise_file_not_found)
    missing_path = str(tmp_path / "missing-cc")
    with pytest.raises(PreprocessingError, match="preprocessor not found") as exc_info:
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler=missing_path),
        )
    assert str(exc_info.value) == f"preprocessor not found: {missing_path}"
    assert exc_info.value.category == "PREPROCESSOR_NOT_FOUND"
    assert [diagnostic.to_dict() for diagnostic in exc_info.value.diagnostics] == [
        {
            "category": "PREPROCESSOR_NOT_FOUND",
            "message": f"preprocessor not found: {missing_path}",
            "severity": "error",
            "path": None,
            "line": None,
            "command": [missing_path, "-E", "-x", "c", str(c_source)],
        }
    ]

    def raise_timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="cc", timeout=60)

    monkeypatch.setattr(preprocessing.subprocess, "run", raise_timeout)
    slow_path = str(tmp_path / "slow-cc")
    with pytest.raises(PreprocessingError, match="timed out") as exc_info:
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler=slow_path),
        )
    assert str(exc_info.value) == "compiler preprocessing failed: timed out after 60 seconds"
    assert exc_info.value.category == "PREPROCESSOR_FAILED"
    assert [diagnostic.to_dict() for diagnostic in exc_info.value.diagnostics] == [
        {
            "category": "PREPROCESSOR_FAILED",
            "message": "compiler preprocessing timed out after 60 seconds",
            "severity": "error",
            "path": None,
            "line": None,
            "command": [slow_path, "-E", "-x", "c", str(c_source)],
        }
    ]

    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 2, "stdout": "", "stderr": ""})(),
    )
    bad_path = str(tmp_path / "bad-cc")
    with pytest.raises(PreprocessingError, match="exit code 2") as exc_info:
        preprocessing.preprocess_source(
            c_source,
            language="c",
            config=PreprocessingConfig(mode="compiler", compiler=bad_path),
        )
    assert exc_info.value.category == "PREPROCESSOR_FAILED"
    assert [diagnostic.to_dict() for diagnostic in exc_info.value.diagnostics] == [
        {
            "category": "PREPROCESSOR_FAILED",
            "message": "compiler preprocessing failed with exit code 2",
            "severity": "error",
            "path": None,
            "line": None,
            "command": [bad_path, "-E", "-x", "c", str(c_source)],
        }
    ]

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
    assert [diagnostic.to_dict() for diagnostic in result.diagnostics] == [
        {
            "category": "PROVENANCE_UNAVAILABLE",
            "message": "selected compiler adapter did not provide source linemarkers",
            "severity": "warning",
            "path": None,
            "line": None,
            "command": [sys.executable, str(c_source)],
        }
    ]

    monkeypatch.setattr(
        preprocessing.subprocess,
        "run",
        lambda *_args, **_kwargs: type("Done", (), {"returncode": 0, "stdout": "", "stderr": ""})(),
    )
    result = preprocessing.preprocess_source(
        c_source,
        language="c",
        config=PreprocessingConfig(mode="compiler", compiler=str(tmp_path / "cc")),
    )
    assert result.diagnostics == []

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
    assert str(exc_info.value) == 'Fortran INCLUDE file "missing.inc" was not found'
    assert exc_info.value.category == "INCLUDE_NOT_FOUND"
    assert [diagnostic.to_dict() for diagnostic in exc_info.value.diagnostics] == [
        {
            "category": "INCLUDE_NOT_FOUND",
            "message": 'Fortran INCLUDE file "missing.inc" was not found',
            "severity": "error",
            "path": str(fortran_source.resolve()),
            "line": 1,
            "command": [],
        }
    ]


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
