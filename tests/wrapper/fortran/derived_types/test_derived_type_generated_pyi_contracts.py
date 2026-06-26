"""Generated `.pyi` package fixtures for derived-type wrapper inputs."""

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
    source_contract_case(CONTRACT_ROOT, "fbind_c_derived_layout_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fborrowed_finalizer_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fclasses_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fconstructors_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fderived_boundary_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "finheritance_f90.f90"),
    source_contract_case(CONTRACT_ROOT, "fpointers_f90.f90"),
)


@pytest.mark.parametrize("case", CASES, ids=contract_case_id)
def test_derived_type_generated_pyi_contract_matches_fixture(case: GeneratedContractCase, tmp_path: Path):
    assert_generated_contract_matches_fixture(case, tmp_path)
