#!/usr/bin/env python3
"""Run mutmut with deterministic child-process cleanup and waiting."""

from __future__ import annotations

import os
from multiprocessing import Pool
import subprocess
from time import sleep
from types import TracebackType
from typing import Any

import mutmut.__main__ as mutmut_main


class _TrackedOS:
    """Proxy mutmut's os calls so its worker loop only waits for its own forks."""

    def __init__(self) -> None:
        self._children: set[int] = set()

    def __getattr__(self, name: str) -> Any:
        return getattr(os, name)

    def fork(self) -> int:
        pid = os.fork()
        if pid:
            self._children.add(pid)
        return pid

    def wait(self) -> tuple[int, int]:
        while self._children:
            for pid in tuple(self._children):
                try:
                    waited_pid, wait_status = os.waitpid(pid, os.WNOHANG)
                except ChildProcessError:
                    self._children.remove(pid)
                    continue
                if waited_pid:
                    self._children.remove(waited_pid)
                    return waited_pid, wait_status
            sleep(0.01)
        raise ChildProcessError


class _JoinedPool:
    """Ensure mutmut's generation workers exit before mutation workers start."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._pool = Pool(*args, **kwargs)

    def __enter__(self) -> Any:
        return self._pool

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self._pool.close()
        else:
            self._pool.terminate()
        self._pool.join()


class _StatsSafePopen(subprocess.Popen):
    """Keep mutmut's process-local stats instrumentation out of subprocesses."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if os.getenv("MUTANT_UNDER_TEST") == "stats":
            env = dict(kwargs.get("env") or os.environ)
            env["MUTANT_UNDER_TEST"] = ""
            kwargs["env"] = env
        super().__init__(*args, **kwargs)


def main() -> None:
    mutmut_main.Pool = _JoinedPool
    mutmut_main.os = _TrackedOS()
    subprocess.Popen = _StatsSafePopen
    mutmut_main.cli()


if __name__ == "__main__":
    main()
