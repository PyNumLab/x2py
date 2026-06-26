# Arrays

Scope: NumPy array arguments, results, shape/rank/order validation,
assumed-rank and assumed-size forms, multidimensional arrays, and `bind(C)`
array behavior.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/arrays`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated array packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for array dtype, rank,
shape, order, stride, lower-bound, writeability, and zero-extent validation.

Tests: `test_array_contracts.py`, `test_array_results.py`,
`test_assumed_rank_arrays.py`, `test_array_generated_pyi_contracts.py`,
`test_bind_c_array_type.py`, `test_multidimensional_arrays.py`.
