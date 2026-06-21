"""Shared fixtures for Fortran wrapper runtime tests."""

import pytest


@pytest.fixture(params=("source", "generated-pyi"), ids=("source", "generated-pyi"))
def pyi_parity_build_mode(request: pytest.FixtureRequest) -> str:
    """Select an equivalent source or generated-contract wrapper build."""

    return request.param
