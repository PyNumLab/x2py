"""Enable coverage collection in subprocesses when requested."""

from __future__ import annotations

import os


if os.getenv("COVERAGE_PROCESS_START"):
    from coverage import process_startup

    process_startup()
