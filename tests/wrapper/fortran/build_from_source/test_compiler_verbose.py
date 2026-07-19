import shlex
import sys
from pathlib import Path

from x2py.compiling.objects import ObjectFile
from x2py.compiling.compilers import Compiler
from x2py.compiling.compiler_profiles import available_compilers, vendors


def test_run_command_verbose_prints_replayable_command(capsys):
    cmd = [sys.executable, "-c", ""]

    returned = Compiler.run_command(cmd, verbose=1)

    assert returned == tuple(cmd)
    output = capsys.readouterr().out.splitlines()
    assert output == [shlex.join(cmd)]


def test_record_only_compiler_keeps_object_command_without_executing(monkeypatch, tmp_path: Path):
    compiler = Compiler("GNU", execute_commands=False)
    monkeypatch.setattr(compiler, "_executable", lambda _language, _tools: "gcc")
    monkeypatch.setattr(
        Compiler,
        "run_command",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("command executed")),
    )
    object_file = ObjectFile(
        source=tmp_path / "source.c",
        object_path=tmp_path / "source.o",
        language="c",
    )

    compiler.compile_object(object_file)

    command = compiler.command_log[0]
    assert command[0] == "gcc"
    assert command[-4:] == ("-c", str(object_file.source), "-o", str(object_file.object_path))


def test_user_compile_flags_follow_default_profile_flags(monkeypatch, tmp_path: Path):
    compiler = Compiler("GNU", debug=False, execute_commands=False)
    monkeypatch.setattr(compiler, "_executable", lambda _language, _tools: "gcc")
    object_file = ObjectFile(
        source=tmp_path / "source.c",
        object_path=tmp_path / "source.o",
        language="c",
        flags=("-O0", "-g0"),
    )

    compiler.compile_object(object_file)

    command = compiler.command_log[0]
    assert command.index("-O3") < command.index("-O0")
    assert command.index("-DNDEBUG") < command.index("-g0")


def test_input_language_executable_override_controls_compilation_and_linking(tmp_path: Path):
    compiler = Compiler("GNU", execute_commands=False, executables={"fortran": sys.executable})
    native = ObjectFile(tmp_path / "native.f90", tmp_path / "native.o", "fortran")

    compiler.compile_object(native)
    compiler.link_extension(
        module_name="wrapped",
        output_dir=tmp_path,
        language="fortran",
        objects=(native,),
    )

    assert compiler.command_log[0][0] == sys.executable
    assert compiler.command_log[1][0] == sys.executable


def test_python_sysconfig_profile_flags_do_not_override_wrapper_profile(monkeypatch, tmp_path: Path):
    compiler = Compiler("GNU", debug=False, execute_commands=False)
    monkeypatch.setattr(compiler, "_executable", lambda _language, _tools: "gcc")
    object_file = ObjectFile(
        source=tmp_path / "binding.c",
        object_path=tmp_path / "binding.o",
        language="c",
        tools=frozenset({"python"}),
    )

    compiler.compile_object(object_file)

    command = compiler.command_log[0]
    assert command.count("-O3") == 1
    assert command.count("-DNDEBUG") == 1
    assert "-g" not in command


def test_link_keeps_the_declared_object_and_link_argument_order(monkeypatch, tmp_path: Path):
    compiler = Compiler("GNU", execute_commands=False)
    monkeypatch.setattr(compiler, "_executable", lambda _language, _tools: "gfortran")
    native = ObjectFile(tmp_path / "native.f90", tmp_path / "native.o", "fortran")
    bridge = ObjectFile(tmp_path / "bridge.f90", tmp_path / "bridge.o", "fortran")
    binding = ObjectFile(tmp_path / "binding.c", tmp_path / "binding.o", "c", tools=frozenset({"python"}))

    extension = compiler.link_extension(
        module_name="wrapped",
        output_dir=tmp_path,
        language="fortran",
        objects=(native, bridge, binding),
        link_args=("-Wl,--as-needed", "-lm"),
    )

    command = compiler.command_log[0]
    assert command.index(str(native.object_path)) < command.index(str(bridge.object_path))
    assert command.index(str(bridge.object_path)) < command.index(str(binding.object_path))
    assert command.index(str(binding.object_path)) < command.index("-Wl,--as-needed") < command.index("-lm")
    assert command[command.index("-o") + 1] == str(extension)


def test_builtin_toolchains_keep_c_and_fortran_stage_definitions():
    assert vendors == ("GNU", "intel", "PGI", "nvidia", "LLVM")
    for toolchain in available_compilers.values():
        for language in ("c", "fortran"):
            config = toolchain[language]
            assert config["exec"]
            assert config["debug_flags"]
            assert config["release_flags"]
            assert config["general_flags"]
        assert toolchain["fortran"]["module_output_flag"]
        assert toolchain["c"]["python"]["shared_suffix"]
