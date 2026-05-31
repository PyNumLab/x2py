# -*- coding: utf-8 -*-
"""Pytest import setup for in-place repository runs."""

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from hypothesis import HealthCheck, settings
except ImportError:  # pragma: no cover - base test installs can omit QA extras.
    pass
else:
    settings.register_profile(
        "dev",
        max_examples=75,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow],
    )
    settings.register_profile(
        "ci",
        max_examples=250,
        deadline=None,
        derandomize=True,
        suppress_health_check=[HealthCheck.too_slow],
    )
    settings.register_profile(
        "fuzz",
        max_examples=1000,
        deadline=None,
        suppress_health_check=[
            HealthCheck.filter_too_much,
            HealthCheck.too_slow,
        ],
    )
    settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
