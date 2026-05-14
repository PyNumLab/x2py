# -*- coding: utf-8 -*-
"""Pytest import setup for in-place repository runs."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
