import re
import shlex
import sys

from x2py.compiling.compilers import Compiler


def test_run_command_verbose_prints_replayable_command(capsys):
    cmd = [sys.executable, "-c", ""]

    returned = Compiler.run_command(cmd, verbose=1)

    assert returned == cmd
    output = capsys.readouterr().out.splitlines()
    assert output[0] == shlex.join(cmd)
    assert re.fullmatch(r">> Command completed in \d+\.\d{3}s", output[1])


def test_record_only_compiler_keeps_exact_command_without_executing(monkeypatch):
    compiler = Compiler("GNU", execute_commands=False)
    monkeypatch.setattr(
        Compiler,
        "run_command",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("command executed")),
    )

    command = ["gfortran", "-O3", "source.f90", "-o", "source.o"]

    assert compiler._run_or_record_command(command, verbose=0) == command
    assert compiler.command_log == (tuple(command),)


def test_user_compile_flags_are_appended_after_default_profile_flags():
    compiler = Compiler("GNU", debug=False, execute_commands=False)
    compiler._language_info = compiler._compiler_info["c"]

    flags = compiler._get_flags(["-O0", "-g0"])

    assert flags.index("-O3") < flags.index("-O0")
    assert flags.index("-DNDEBUG") < flags.index("-g0")


def test_python_sysconfig_profile_flags_do_not_override_wrapper_profile():
    compiler = Compiler("GNU", debug=False, execute_commands=False)

    assert compiler._without_python_profile_flags(["-g", "-O2", "-DNDEBUG", "-Wall"]) == ["-Wall"]
