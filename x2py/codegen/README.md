# Codegen Package

This package owns generated wrapper representations and printers. It receives
codegen AST from semantic lowering and emits Fortran bridge and C/CPython
binding source for the implemented Fortran wrapper path.

## Package Map

| Path | Owns |
| --- | --- |
| `models/` | Codegen AST nodes and datatype models. |
| `bridges/fortran_to_c.py` | Fortran-to-C ABI bridge generation. |
| `bindings/c_to_python.py` | CPython extension binding generation. |
| `bindings/cpython_api.py` and `bindings/numpy_cpython_api.py` | Helper AST/API models for Python and NumPy C APIs. |
| `printers/fcode.py` | Fortran source printing. |
| `printers/cpythoncode.py` and `printers/ccode.py` | C/CPython source printing. |
| `printers/pyi_printer.py` | Semantic `.pyi` contract printing. |
| `binding_pipeline.py` | Ordered bridge and binding generation pipeline. |
| `scope.py` | Codegen scope and name lookup helpers. |

## Rules Of Thumb

- Keep runtime wrapper policy above codegen when possible: semantic lowering and
  ownership policy decide what should happen; generators emit it.
- Use explicit dispatch tables for secondary policy dimensions such as datatype
  or ownership action.
- Do not add placeholder backends without documented runtime contracts and
  tests.
- A wrapper feature is supported only when generated sources compile, import,
  and pass runtime behavior and failure-path tests.

## Tests And Docs

- User wrapper contract: `docs/user/guide/fortran-wrapper.md`
- Source navigation: `docs/developer/source-map.md`, `docs/developer/feature-to-code-map.md`
- Pipeline map: `docs/maintainer/internal-architecture/pipeline-map.md`
- Runtime tests: `tests/wrapper/fortran/`
- `.pyi` printer tests: `tests/codegen/printers/`
