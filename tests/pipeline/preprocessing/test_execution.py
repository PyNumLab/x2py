"""Tests split by stable ownership concept from `test_cli.py`."""

from tests.pipeline.preprocessing._support import (
    Path,
    PreprocessingConfig,
    PreprocessingError,
    json,
    preprocessing,
    pytest,
    run_compiler_preprocessor,
    run_compiler_preprocessor_with_recipe,
    subprocess,
    sys,
)


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
