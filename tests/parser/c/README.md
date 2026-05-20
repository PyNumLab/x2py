# C Parser Test Roadmap

This directory contains the planned C parser test suite. The tests are
intentionally skipped until the corresponding parser capability exists.

Unskip tests one capability at a time on a short-lived `c-parser/*` branch, then
merge only into `c-parser/main`.

Guidelines:

- keep these tests separate from the Fortran parser tests
- do not import `c_parser` at module import time while the suite is skipped
- unskip the smallest useful group of tests with each implementation branch
- add fixtures and goldens only when the corresponding schema is stable
- keep cJSON as the first real-world corpus target once corpus tests start

