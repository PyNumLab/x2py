import shlex
import sys

from x2py.compiling.compilers import Compiler


def test_run_command_verbose_prints_replayable_command(capsys):
    cmd = [sys.executable, "-c", ""]

    returned = Compiler.run_command(cmd, verbose=1)

    assert returned == cmd
    assert capsys.readouterr().out == f"{shlex.join(cmd)}\n"
