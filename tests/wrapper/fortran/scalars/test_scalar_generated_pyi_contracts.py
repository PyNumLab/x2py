"""Generated `.pyi` package fixtures for scalar wrapper inputs."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.wrapper.fortran._generated_contracts import (
    GeneratedContractCase,
    assert_generated_contract_matches_fixture,
    contract_case_id,
    source_contract_case,
)

CONTRACT_ROOT = Path(__file__).parent / "contracts"
CASES = (
    source_contract_case(CONTRACT_ROOT, "fenums_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fbind_value_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fmath.f"),
    source_contract_case(CONTRACT_ROOT, "fmath_arrays.f"),
    source_contract_case(CONTRACT_ROOT, "fmath_arrays_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fmath_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fscalar_kinds_f90.f90"),
)


@pytest.mark.parametrize("case", CASES, ids=contract_case_id)
def test_scalar_generated_pyi_contract_matches_fixture(case: GeneratedContractCase, tmp_path: Path):
    assert_generated_contract_matches_fixture(case, tmp_path)
