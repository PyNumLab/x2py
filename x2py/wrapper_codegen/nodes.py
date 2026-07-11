"""Isolated backend syntax nodes for scalar wrapper source foundations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackendScalarType:
    """Scalar type spelling consumed by C and Fortran printers."""

    semantic_name: str
    c_spelling: str
    fortran_spelling: str
    python_parse_unit: str | None = None
    numpy_type_macro: str | None = None


@dataclass(frozen=True)
class CodeExpression:
    """Raw expression text owned by a backend emitter or focused test."""

    text: str


@dataclass(frozen=True)
class ApiReference:
    """Named CPython, NumPy, or runtime helper API concept."""

    name: str
    include: str | None = None


@dataclass(frozen=True)
class CInclude:
    """C include directive."""

    header: str
    system: bool = True


@dataclass(frozen=True)
class CParameter:
    """C function parameter."""

    name: str
    type_name: str


@dataclass(frozen=True)
class CFunctionPrototype:
    """C function prototype for generated headers."""

    name: str
    return_type: str
    parameters: tuple[CParameter, ...] = ()


@dataclass(frozen=True)
class CDeclaration:
    """C local or global declaration."""

    name: str
    type_name: str
    initializer: CodeExpression | None = None


@dataclass(frozen=True)
class CExpressionStatement:
    """C expression statement."""

    expression: CodeExpression


@dataclass(frozen=True)
class CReturn:
    """C return statement."""

    expression: CodeExpression | None = None


@dataclass(frozen=True)
class CFunction:
    """C function definition."""

    name: str
    return_type: str
    parameters: tuple[CParameter, ...] = ()
    body: tuple[CDeclaration | CExpressionStatement | CReturn, ...] = ()
    storage: str | None = None


@dataclass(frozen=True)
class CHeader:
    """Generated C header module."""

    guard: str
    includes: tuple[CInclude, ...] = ()
    prototypes: tuple[CFunctionPrototype, ...] = ()


@dataclass(frozen=True)
class CModule:
    """Generated C source module."""

    name: str
    includes: tuple[CInclude, ...] = ()
    declarations: tuple[CDeclaration, ...] = ()
    functions: tuple[CFunction, ...] = ()


@dataclass(frozen=True)
class FortranUse:
    """Fortran use statement."""

    module: str
    only: tuple[str, ...] = ()


@dataclass(frozen=True)
class FortranParameter:
    """Fortran procedure argument declaration."""

    name: str
    type_name: str
    attributes: tuple[str, ...] = ()


@dataclass(frozen=True)
class FortranDeclaration:
    """Fortran local or result declaration."""

    name: str
    type_name: str
    attributes: tuple[str, ...] = ()


@dataclass(frozen=True)
class FortranAssignment:
    """Fortran assignment statement."""

    target: str
    expression: CodeExpression


@dataclass(frozen=True)
class FortranCall:
    """Fortran call statement."""

    function_name: str
    arguments: tuple[CodeExpression, ...] = ()


@dataclass(frozen=True)
class FortranFunction:
    """Fortran function or subroutine body used by scalar bridges."""

    name: str
    parameters: tuple[FortranParameter, ...] = ()
    result_name: str | None = None
    result_type: str | None = None
    bind_name: str | None = None
    declarations: tuple[FortranDeclaration, ...] = ()
    body: tuple[FortranAssignment | FortranCall, ...] = ()


@dataclass(frozen=True)
class FortranModule:
    """Generated Fortran module."""

    name: str
    uses: tuple[FortranUse, ...] = ()
    procedures: tuple[FortranFunction, ...] = ()
