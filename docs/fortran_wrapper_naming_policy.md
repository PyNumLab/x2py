# Fortran Wrapper Naming Policy

Generated Fortran wrappers expose a Python surface derived from Fortran public
symbols. Fortran lookup is case-insensitive, while Python lookup is
case-sensitive and has keywords, so x2py applies one public-name policy before
generating the extension.

## Public Name Normalization

Public Fortran module names, procedures, generic interfaces, derived types,
type-bound methods, fields, module constants, generated module-variable
accessors, and Python keyword arguments use these rules:

- Fortran identifiers are case-normalized to lowercase for Python.
- Python keywords gain one trailing underscore, for example `class` becomes
  `class_`.
- Invalid Python identifier characters are replaced with underscores, and a
  leading underscore is added if the first character would otherwise be invalid.
- `bind(C, name=...)` changes only the native ABI symbol. The Python-visible
  name still comes from the Fortran procedure or binding name.
- Scalar mutable module variables are exposed as `get_<name>()` and
  `set_<name>(value)`. Allocatable module arrays are exposed as `get_<name>()`.
  Parameters are exposed as constants named `<name>`.

## Collisions

After normalization, every public name must be unique within its Python
namespace. Module members share one namespace. Each derived type has its own
field and method namespace. Each callable has its own keyword-argument
namespace.

By default, x2py fixes public-name collisions by appending a deterministic
numeric suffix to the normalized base name. For example, public symbols that
normalize to `class_` become `class_`, then `class__2`, then `class__3`.
Generated helper names use the same rule for their public surface, so a
procedure named `get_value` and a mutable module variable named `value` do not
silently overwrite each other.

When `--strict-wrapper-names` is passed to `python -m x2py`, x2py does not fix
public names. A public name that needs keyword/identifier escaping, or a public
name that collides after normalization, raises a deterministic generation error
before native compilation.

Private Fortran procedures, type-bound procedures, variables, fields, and
derived types are not exported as Python public API. Public procedures and
fields must not expose private derived types in their signatures.
