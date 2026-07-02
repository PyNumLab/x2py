"""Generate pyi fixtures for tests/data/fortran/general and tests/data/c/general."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests._shared.fixture_outputs import (
    iter_general_c_fixture_projects,
    iter_general_fortran_fixtures,
    reset_fortran_pyi_fixtures,
    write_c_pyi_fixture,
    write_pyi_fixture_package,
)


def main() -> None:
    reset_fortran_pyi_fixtures()
    for fixture in iter_general_fortran_fixtures():
        print(f"updated {write_pyi_fixture_package(fixture)}")
    for project_key, fixtures in iter_general_c_fixture_projects():
        print(f"updated {write_c_pyi_fixture(project_key, fixtures)}")


if __name__ == "__main__":
    main()
