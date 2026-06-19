import shlex
import sys

from x2py.compiling.compilers import Compiler


def test_run_command_verbose_prints_replayable_command(capsys):
    cmd = [sys.executable, "-c", ""]

    returned = Compiler.run_command(cmd, verbose=1)

    assert returned == cmd
    assert capsys.readouterr().out == f"{shlex.join(cmd)}\n"


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
