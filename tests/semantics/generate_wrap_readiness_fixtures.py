"""Generate semantic wrap-readiness message fixtures for Fortran corpora."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests._shared.fixture_outputs import write_wrap_readiness_message_fixture


def main() -> None:
    print(f"updated {write_wrap_readiness_message_fixture()}")


if __name__ == "__main__":
    main()
