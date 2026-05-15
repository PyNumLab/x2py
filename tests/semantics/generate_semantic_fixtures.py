"""Generate semantic JSON fixtures for tests/data/fortran/general."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests._shared.fixture_outputs import iter_general_fortran_fixtures, write_semantics_fixture


def main() -> None:
    for fixture in iter_general_fortran_fixtures():
        print(f"updated {write_semantics_fixture(fixture)}")


if __name__ == "__main__":
    main()
