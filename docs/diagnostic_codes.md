# Diagnostic Codes

Diagnostic codes are stable category identifiers for users, tests, and tooling.
They are not source line numbers, occurrence counters, or process exit statuses.

New categories should use explicit symbolic names such as
`PARSE_INVALID_SYNTAX` or `C_UNRESOLVED_INCLUDE`. Existing numbered codes remain
supported for compatibility. Replacing a numbered code should be a deliberate
compatibility change with tests and generated fixtures updated together.

## Fatal Parser Errors

Fatal parser errors stop parsing and are rendered by the CLI without a Python
traceback unless `--debug` is used.

| Code | Frontend | Meaning |
| --- | --- | --- |
| `PARSE001` | Fortran | Compatibility fallback for a Fortran parse error without a more specific code. |
| `PARSE_INVALID_SYNTAX` | Fortran | Syntax cannot be consumed in a modeled Fortran grammar region. |
| `PARSE_WRONG_ENTRYPOINT` | Fortran | A singular public parser API was called for a different source-unit kind. |
| `PARSE_AMBIGUOUS_ENTRYPOINT` | Fortran | A singular public parser API matched more than one source unit. |
| `CPARSE001` | C | Compatibility fallback for a C parse error without a more specific code. |
| `CPARSE002` | C | Unsupported K&R-style function definition. |
| `CPARSE003` | C | Invalid C primitive-specifier sequence. |
| `CPARSE_INVALID_SYNTAX` | C | Syntax cannot be consumed in a modeled C grammar region. |

`PARSE001`, `CPARSE001`, `CPARSE002`, and `CPARSE003` predate the explicit
category naming rule. Prefer symbolic names for new categories. If the numbered
codes are migrated later, useful replacements would be names such as
`PARSE_UNKNOWN_DATATYPE`, `CPARSE_UNSUPPORTED_KNR_DEFINITION`, and
`CPARSE_INVALID_SPECIFIER_SEQUENCE`.

## C Report Diagnostics

The C parser can preserve partial metadata and attach `CDiagnostic` records.
These records do not necessarily stop parsing; inspect each diagnostic's
`severity`.

| Code | Meaning |
| --- | --- |
| `C_UNRESOLVED_INCLUDE` | A local include could not be resolved. |
| `C_UNSUPPORTED_FUNCTION_LIKE_MACRO` | A function-like macro was recorded but not expanded. |
| `C_MACRO_DEPENDENT_DECLARATION` | Declaration parsing requires macro expansion. |
| `C_UNSUPPORTED_DECLARATION` | Recognized declaration form is outside the modeled subset. |
| `C_UNSUPPORTED_DECLARATOR` | Declarator form is outside the modeled subset. |
| `C_UNSUPPORTED_FIELD_DECLARATION` | Aggregate field form is outside the modeled subset. |
| `C_INVALID_FLEXIBLE_ARRAY_MEMBER` | Flexible array member placement is invalid. |
| `C_UNION_BY_VALUE` | A function uses a union by value and needs wrapper policy review. |
| `C_TYPEDEF_CYCLE` | Typedef resolution found a cycle. |
| `C_CONFLICTING_FUNCTION_DECLARATION` | Function declarations conflict. |
| `C_DUPLICATE_FUNCTION_DEFINITION` | Function has more than one definition. |
| `C_CONFLICTING_VARIABLE_DECLARATION` | File-scope variable declarations conflict. |
| `C_DUPLICATE_VARIABLE_DEFINITION` | File-scope variable has more than one definition. |
| `C_CONFLICTING_TYPEDEF` | Typedef declarations conflict. |
| `C_DUPLICATE_TAG_DEFINITION` | Struct, union, or enum tag has more than one definition. |

