# -*- coding: utf-8 -*-
"""Shared preprocessing CLI and compiler-command contract tests."""

import json
import os
import subprocess
import sys
from pathlib import Path

from x2py.preprocessing import (
    PreprocessingConfig,
    build_compile_commands_invocation,
    build_direct_preprocess_invocation,
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
    assert "raw C mode records source macros" in res.stderr


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


def test_cli_fortran_internal_mode_uses_define_and_undef_for_branch_selection(tmp_path: Path):
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

    selected = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse", "-D", "USE_MPI"],
        capture_output=True,
        text=True,
        check=True,
    )
    fallback = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse", "-U", "USE_MPI"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "subroutine selected" in selected.stdout
    assert "subroutine fallback" not in selected.stdout
    assert "subroutine fallback" in fallback.stdout
    assert "subroutine selected" not in fallback.stdout


def test_cli_fortran_internal_json_records_macro_selection_recipe(tmp_path: Path):
    source = tmp_path / "branch.F90"
    source.write_text(
        "#ifdef USE_MPI\nsubroutine selected()\nend subroutine selected\n#endif\n",
        encoding="utf-8",
    )

    res = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--parse", "--json", "-D", "USE_MPI", "-U", "DEBUG"],
        capture_output=True,
        text=True,
        check=True,
    )
    recipe = json.loads(res.stdout)[str(source)]["preprocessing_recipe"]

    assert recipe["mode"] == "internal"
    assert recipe["language"] == "fortran"
    assert recipe["source_path"] == str(source)
    assert recipe["compiler"] is None
    assert recipe["argv"] == []
    assert recipe["defines"] == ["USE_MPI"]
    assert recipe["undefs"] == ["DEBUG"]


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
