# Function Calls

Scope: Python-callable procedure behavior that is not specific to one data
category, including optional arguments, output-argument projection, and
`@native_call` metadata needed to preserve native argument ordering.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/function_calls`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated call-surface packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for argument intent,
hidden outputs, projected returns, optional arguments, call signatures,
native-call projection metadata, and generated-contract replay from native
shared-library inputs.

Tests: `test_function_call_generated_pyi_contracts.py`,
`test_optional_arguments.py`, `test_output_arguments.py`,
`test_native_call_examples.py`.
