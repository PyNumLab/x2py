import ast
from dataclasses import asdict
from pathlib import Path

import pytest

from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules
from x2py.semantics.models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticConstraint,
    SemanticEnumerator,
    SemanticField,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticModule,
    SemanticEnum,
    SemanticType,
    SemanticVariable,
)
from x2py.semantics.pyi_parser import (
    _PyiAstParser,
    _node_text,
    convert_pyi_to_ir,
    load_pyi_file,
    load_pyi_modules,
    parse_pyi_text,
)
from x2py.codegen.printers.pyi_printer import emit_module
from tests._shared.fixture_outputs import FORTRAN_DATA_DIR, FORTRAN_SUFFIXES
from x2py import parse_fortran_file


PYI_COMPARE_DIRS = ("general", "blas", "lapack", "scifortran")
_ALL_FORTRAN_PYI_COMPARE_FIXTURES = sorted(
    path
    for dirname in PYI_COMPARE_DIRS
    for path in (FORTRAN_DATA_DIR / dirname).rglob("*")
    if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
)


def _sample_pyi_compare_fixtures(paths: list[Path]) -> list[Path]:
    by_dir: dict[str, list[Path]] = {}
    for path in paths:
        by_dir.setdefault(path.relative_to(FORTRAN_DATA_DIR).parts[0], []).append(path)

    selected: list[Path] = []
    for dirname in PYI_COMPARE_DIRS:
        selected.extend(by_dir.get(dirname, [])[:8])

    for relpath in [
        "general/module_vars_use.f90",
        "lapack/clartg.f90",
        "lapack/la_constants.f90",
        "scifortran/GAUSS_QUADRATURE.f90",
    ]:
        path = FORTRAN_DATA_DIR / relpath
        if path.exists():
            selected.append(path)

    return sorted(set(selected))


FORTRAN_PYI_COMPARE_FIXTURES = _sample_pyi_compare_fixtures(_ALL_FORTRAN_PYI_COMPARE_FIXTURES)


def _semantic_modules_for_source(path: Path):
    parsed = parse_fortran_file(
        path.read_text(encoding="utf-8"),
        filename=str(path.relative_to(FORTRAN_DATA_DIR)),
    )
    return fortran_file_to_semantic_modules(parsed, standalone_module_name=path.stem)


def test_parse_pyi_text_dispatches_nested_and_qualified_semantic_types():
    module = parse_pyi_text(
        """
import typing

public_value: Int32
bounded: Final[Annotated[Int32, Bounded(1, 8)]]
callback: typing.Callable
pointer: Ptr(Float64)
read_only_pointer: Ptr(Const(Float64))
""",
        module_name="dispatch",
    )

    public_value, bounded, callback, pointer, read_only_pointer = module.variables
    assert isinstance(public_value, SemanticVariable)
    assert public_value.visibility == "public"
    assert bounded.semantic_type.constraints == [
        SemanticConstraint("Bounded", [1, 8]),
        SemanticConstraint("Constant"),
    ]
    assert callback.semantic_type.name == "Callable"
    assert pointer.semantic_type.storage.kind == "reference"
    assert read_only_pointer.semantic_type.storage.mutable is False


def test_parse_pyi_text_allows_user_modified_stub():
    pyi = """
import iso_c_binding

class particle:
    id: Int32

scale: private[Float64]
answer: Final[Int32]
hidden_answer: private[Final[Int32]]
literal_answer: Final[Int32] = 42

def touch(
    p: particle
) -> Returns["p", particle]: ...
"""

    module = parse_pyi_text(pyi, module_name="edited")

    assert module.name == "edited"
    assert module.imports == ["iso_c_binding"]
    assert module.classes[0].name == "particle"
    assert isinstance(module.classes[0].fields[0], SemanticField)
    assert module.variables[0].name == "scale"
    assert module.variables[0].visibility == "private"
    assert module.variables[1].name == "answer"
    assert [c.name for c in module.variables[1].semantic_type.constraints] == ["Constant"]
    assert module.variables[2].name == "hidden_answer"
    assert module.variables[2].visibility == "private"
    assert [c.name for c in module.variables[2].semantic_type.constraints] == ["Constant"]
    assert module.variables[3].name == "literal_answer"
    assert module.variables[3].default_value == "42"
    assert module.functions[0].arguments[0].intent == "inout"


def test_parse_pyi_text_round_trips_open_enum_with_unscoped_enumerators():
    source = """class status(Enum[Int]):
    pass

STATUS_OK: Final[status] = 0
STATUS_NEXT: Final[status] = STATUS_OK + 1

def set_status(
    value: status
) -> None: ...
"""

    module = parse_pyi_text(source, module_name="status_api")

    assert len(module.enums) == 1
    enum = module.enums[0]
    assert isinstance(enum, SemanticEnum)
    assert enum.name == "status"
    assert enum.open is True
    assert enum.underlying_type.name == "Int"
    assert all(isinstance(item, SemanticEnumerator) for item in enum.enumerators)
    assert [item.name for item in enum.enumerators] == ["STATUS_OK", "STATUS_NEXT"]
    assert module.variables[1].default_value == "STATUS_OK + 1"
    assert module.functions[0].arguments[0].semantic_type.name == "status"
    emitted = emit_module(module)
    assert "class status(Enum[Int]):" in emitted
    assert "STATUS_NEXT: Final[status] = STATUS_OK + 1" in emitted
    assert parse_pyi_text(emitted, module_name="status_api") == module


def test_parse_pyi_text_preserves_callable_signature_metadata():
    module = parse_pyi_text(
        """
from typing import Callable

class sim_state:
    n: Int32

def integrate(
    state: sim_state,
    objective: Callable[[sim_state, Float64], Float64]
) -> Float64: ...
""",
        module_name="callbacks",
    )

    callback_type = module.functions[0].arguments[1].semantic_type
    assert callback_type.name == "Callable"
    assert callback_type.dtype == "Callable"
    assert [arg.name for arg in callback_type.metadata["arguments"]] == ["sim_state", "Float64"]
    assert callback_type.metadata["return"].name == "Float64"


def test_parse_pyi_text_accepts_import_aliases():
    module = parse_pyi_text(
        "from list_input import delete_input_list as delete_input\n",
        module_name="edited",
    )

    assert module.imports == [
        SemanticImport(
            module="list_input",
            items=[SemanticImportItem(source="delete_input_list", target="delete_input")],
        )
    ]


def test_parse_pyi_text_accepts_relative_imports():
    module = parse_pyi_text("from ..types_mod import particle\nfrom . import local_particle\n", module_name="edited")

    assert module.imports == [
        SemanticImport(
            module="..types_mod",
            items=[SemanticImportItem(source="particle")],
        ),
        SemanticImport(
            module=".",
            items=[SemanticImportItem(source="local_particle")],
        ),
    ]


def test_parse_pyi_text_annotates_types_from_each_import_statement():
    module = parse_pyi_text(
        """
from first_mod import first_t
from second_mod import second_t as local_t

answer: Int32

def create() -> local_t: ...
""",
        module_name="edited",
    )

    assert module.functions[0].return_type.metadata["external_type_ref"] == {
        "name": "second_t",
        "local_name": "local_t",
        "origin_module": "second_mod",
        "wrapped": False,
        "representation": "opaque",
    }
    qualified = parse_pyi_text(
        """
import first_mod, shared as local_shared

answer: Int32

def create() -> local_shared.inner.types_mod.particle: ...
""",
        module_name="edited",
    )
    assert qualified.functions[0].return_type.metadata["external_type_ref"] == {
        "name": "particle",
        "local_name": "local_shared.inner.types_mod.particle",
        "origin_module": "shared",
        "wrapped": False,
        "representation": "opaque",
    }


def test_load_pyi_modules_reconciles_opaque_and_edited_external_types(tmp_path: Path):
    physics = tmp_path / "physics.pyi"
    types_mod = tmp_path / "types_mod.pyi"
    physics.write_text(
        """
from types_mod import particle

answer: Int32

def create_particle() -> Ptr(particle): ...

def move(p: Annotated[Ptr(particle), CompatibleHandle]) -> None: ...
""",
        encoding="utf-8",
    )
    types_mod.write_text(
        """
class particle(Opaque):
    pass
""",
        encoding="utf-8",
    )

    modules = {module.name: module for module in load_pyi_modules(tmp_path)}
    opaque = modules["types_mod"].classes[0]
    create_ref = modules["physics"].functions[0].return_type.metadata["external_type_ref"]
    move_type = modules["physics"].functions[1].arguments[0].semantic_type

    assert opaque.metadata == {"representation": "opaque"}
    assert create_ref == {
        "name": "particle",
        "local_name": "particle",
        "origin_module": "types_mod",
        "wrapped": False,
        "representation": "opaque",
    }
    assert [constraint.name for constraint in move_type.constraints] == ["CompatibleHandle"]

    types_mod.write_text(
        """
class particle:
    mass: Float64
""",
        encoding="utf-8",
    )
    edited_modules = {module.name: module for module in load_pyi_modules([physics, types_mod])}
    edited_ref = edited_modules["physics"].functions[0].return_type.metadata["external_type_ref"]

    assert edited_ref["wrapped"] is True
    assert edited_ref["representation"] == "wrapped"
    assert edited_modules["types_mod"].classes[0].fields[0].name == "mass"


def test_load_pyi_modules_preserves_dotted_module_names_from_directory(tmp_path: Path):
    package = tmp_path / "shared"
    package.mkdir()
    (tmp_path / "physics.pyi").write_text(
        """
from shared.types_mod import particle

def move(p: Ptr(particle)) -> None: ...
""",
        encoding="utf-8",
    )
    (package / "types_mod.pyi").write_text(
        """
class particle(Opaque):
    pass
""",
        encoding="utf-8",
    )

    modules = {module.name: module for module in load_pyi_modules(tmp_path)}
    particle_ref = modules["physics"].functions[0].arguments[0].semantic_type.metadata["external_type_ref"]

    assert "shared.types_mod" in modules
    assert particle_ref["origin_module"] == "shared.types_mod"
    assert particle_ref["representation"] == "opaque"


def test_load_pyi_modules_handles_duplicate_roots_and_ambiguous_module_names(tmp_path: Path):
    package = tmp_path / "shared"
    package.mkdir()
    pyi_path = package / "types_mod.pyi"
    pyi_path.write_text("class particle:\n    pass\n", encoding="utf-8")

    assert [module.name for module in load_pyi_modules([tmp_path, tmp_path])] == ["shared.types_mod"]
    with pytest.raises(ValueError) as error:
        load_pyi_modules([tmp_path, package])
    assert str(error.value) == f"Ambiguous module name for {pyi_path}: 'shared.types_mod' or 'types_mod'"


def test_load_pyi_modules_ignores_directories_with_pyi_suffix(tmp_path: Path):
    (tmp_path / "ignored.pyi").mkdir()
    (tmp_path / "types_mod.pyi").write_text("class particle:\n    pass\n", encoding="utf-8")

    assert [module.name for module in load_pyi_modules(tmp_path)] == ["types_mod"]


def test_load_pyi_file_and_modules_forward_module_name_encoding_and_filename(tmp_path: Path):
    pyi_path = tmp_path / "types_mod.pyi"
    pyi_path.write_bytes("# caf\xe9\nclass particle:\n    pass\n".encode("latin-1"))

    module = load_pyi_file(pyi_path, module_name="custom.types_mod", encoding="latin-1")
    assert module.name == "custom.types_mod"
    assert module.classes[0].name == "particle"
    assert load_pyi_modules(pyi_path, encoding="latin-1")[0].name == "types_mod"

    invalid_path = tmp_path / "invalid.pyi"
    invalid_path.write_text("from broken import\n", encoding="utf-8")
    with pytest.raises(SyntaxError) as error:
        load_pyi_file(invalid_path)
    assert error.value.filename == str(invalid_path)


def test_convert_pyi_to_ir_and_import_parser_edge_cases():
    module = convert_pyi_to_ir("from m import a, b as c\n", module_name="edited")
    assert module.name == "edited"
    assert module.imports == [
        SemanticImport(
            module="m",
            items=[
                SemanticImportItem(source="a"),
                SemanticImportItem(source="b", target="c"),
            ],
        ),
    ]

    with pytest.raises(SyntaxError):
        convert_pyi_to_ir("from m import\n", module_name="edited")


def test_parse_pyi_text_forwards_filename_to_syntax_errors():
    with pytest.raises(SyntaxError) as error:
        parse_pyi_text("from broken import\n", filename="custom.pyi")
    assert error.value.filename == "custom.pyi"


def test_parse_pyi_text_class_body_visibility_and_native_call():
    module = parse_pyi_text(
        """
class wrapper:
    pass

class particle:
    @private
    @native_call([Arg(0)])
    def reset(self: particle) -> Int32: ...
""",
        module_name="edited",
    )

    empty_cls, particle_cls = module.classes
    assert empty_cls.name == "wrapper"
    assert particle_cls.methods[0].name == "reset"
    assert particle_cls.methods[0].native_name == "reset"
    assert particle_cls.methods[0].visibility == "private"
    assert [arg.name for arg in particle_cls.methods[0].arguments] == ["self"]
    assert particle_cls.methods[0].return_type.name == "Int32"
    assert asdict(particle_cls.methods[0].projection[0]) == {
        "python_name": "self",
        "native_name": "self",
        "native_position": 0,
        "python_position": 0,
        "result_position": None,
        "value_kind": "",
        "value": None,
        "intent": "in",
    }


def test_parse_pyi_text_applies_decorators_after_native_call():
    module = parse_pyi_text(
        """
@native_call([])
@private
def hidden() -> None: ...
""",
        module_name="edited",
    )

    assert module.functions[0].visibility == "private"


def test_pyi_parser_reports_unsupported_lines_and_invalid_helpers():
    with pytest.raises(ValueError, match=r"Unsupported .pyi node"):
        parse_pyi_text("bare_name\n", module_name="edited")

    with pytest.raises(ValueError, match="Unsupported class body node"):
        parse_pyi_text("class C:\n    bare_name\n", module_name="edited")

    with pytest.raises(ValueError, match="Expected typed argument"):
        parse_pyi_text("def f(x) -> None: ...\n", module_name="edited")

    with pytest.raises(ValueError, match="expects positional arguments only"):
        parse_pyi_text("@native_call([Arg(0, name='x')])\ndef f(x: Int32) -> None: ...\n", module_name="edited")

    with pytest.raises(ValueError, match="Unsupported native_call projection entry"):
        parse_pyi_text("@native_call([Unknown(0)])\ndef f(x: Int32) -> None: ...\n", module_name="edited")

    with pytest.raises(ValueError, match="Expected Arg"):
        parse_pyi_text("@native_call([Len(Unknown(0))])\ndef f(x: Int32) -> None: ...\n", module_name="edited")

    with pytest.raises(ValueError, match="Unknown semantic type is not allowed"):
        parse_pyi_text("x: Unknown\n", module_name="edited")


def test_pyi_parser_preserves_generic_constraints_as_annotation_metadata():
    module = parse_pyi_text(
        """
value: Annotated[Int32, Bounded(1, 8), Finite]
alias: Annotated[Int32, Name("native_alias"), Finite]
""",
        module_name="edited",
    )

    assert module.variables[0].name == "value"
    assert module.variables[0].semantic_type.constraints == [
        SemanticConstraint("Bounded", [1, 8]),
        SemanticConstraint("Finite"),
    ]
    assert module.variables[1].name == "native_alias"
    assert module.variables[1].semantic_type.constraints == [SemanticConstraint("Finite")]
    emitted = emit_module(SemanticModule(name="constraints", variables=[module.variables[0]]))
    assert "value: Annotated[Int32, Bounded(1, 8), Finite]" in emitted
    assert parse_pyi_text(emitted, module_name="constraints").variables[0] == module.variables[0]


def test_parse_pyi_text_accepts_qualified_ast_wrapper_names():
    module = parse_pyi_text(
        """
import typing

alias: typing.Annotated[Float64[1:n], typing.Name("native_alias")]

def f() -> typing.Tuple[Float64, typing.Returns["y", Float64]]: ...
""",
        module_name="edited",
    )

    assert module.variables[0].name == "native_alias"
    assert module.variables[0].semantic_type.shape == ["1:n"]
    assert module.functions[0].return_type is not None
    assert module.functions[0].return_type.name == "Float64"
    assert module.functions[0].arguments[0].name == "y"
    assert module.functions[0].arguments[0].intent == "out"


def test_parse_pyi_text_accepts_ast_only_projection_value_refs():
    module = parse_pyi_text(
        """
@native_call([Return(0), Len(Return(0)), Work("tmp").shape[0]])
def f() -> Float64: ...
""",
        module_name="edited",
    )

    projection = module.functions[0].projection
    assert projection[1].value == {"kind": "return", "position": 0}
    assert projection[2].value == {"value": {"kind": "work", "name": "tmp"}, "dim": 0}


def test_parse_pyi_text_accepts_plain_return_type():
    pyi = """
def make_value(
    x: Float64
) -> Float64: ...
"""

    module = parse_pyi_text(pyi, module_name="edited")

    func = module.functions[0]
    assert func.return_type is not None
    assert func.return_type.name == "Float64"
    assert func.arguments[0].intent == "in"


def test_function_equality_treats_argument_names_as_placeholders():
    left = parse_pyi_text(
        """
def resize(
    n: Int32,
    x: Float64[1:n]
) -> None: ...
""",
        module_name="edited",
    )
    right = parse_pyi_text(
        """
def resize(
    extent: Int32,
    values: Float64[1:extent]
) -> None: ...
""",
        module_name="edited",
    )

    assert left == right
    assert left.functions[0].arguments[0] != right.functions[0].arguments[0]


def test_plain_return_type_represents_direct_return_not_output_argument():
    from_pyi = parse_pyi_text(
        """
def add(
    a: Float64,
    b: Float64
) -> Float64: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]
    assert func.return_type.name == "Float64"
    assert [arg.name for arg in func.arguments] == ["a", "b"]


def test_native_call_preserves_unnamed_output_argument_position():
    from_pyi = parse_pyi_text(
        """
@native_call([Arg(0), Arg(1), Return(0)])
def add(
    a: Float64,
    b: Float64
) -> Float64: ...
""",
        module_name="edited",
    )
    from_ir = SemanticModule(
        name="edited",
        functions=[
            SemanticFunction(
                name="add",
                native_name="add",
                arguments=[
                    SemanticArgument("a", SemanticType("Float64", dtype="Float64")),
                    SemanticArgument("b", SemanticType("Float64", dtype="Float64")),
                    SemanticArgument(
                        "c",
                        SemanticType("Float64", dtype="Float64"),
                        intent="out",
                    ),
                ],
                projection=[
                    ProjectionMapping(
                        native_name="c",
                        native_position=2,
                        result_position=0,
                        intent="out",
                    )
                ],
            )
        ],
    )

    assert from_pyi != from_ir
    assert from_pyi.functions[0].arguments[2].intent == "out"
    assert from_pyi.functions[0].projection[2].native_position == 2


def test_native_call_accepts_hidden_native_values():
    module = parse_pyi_text(
        """
@native_call([
    Arg(0),
    Const(1),
    Len(Arg(0)),
    Arg(0).shape[0],
    IsPresent(Arg(1)),
    Work("tmp"),
])
def wrapper(
    x: Float64[n],
    b: Vector | None = None
) -> None: ...
""",
        module_name="edited",
    )

    projection = module.functions[0].projection

    assert [asdict(mapping) for mapping in projection] == [
        {
            "python_name": "x",
            "native_name": "x",
            "native_position": 0,
            "python_position": 0,
            "result_position": None,
            "value_kind": "",
            "value": None,
            "intent": "inout",
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 1,
            "python_position": None,
            "result_position": None,
            "value_kind": "const",
            "value": 1,
            "intent": "in",
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 2,
            "python_position": None,
            "result_position": None,
            "value_kind": "len",
            "value": {"kind": "arg", "position": 0},
            "intent": "in",
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 3,
            "python_position": None,
            "result_position": None,
            "value_kind": "shape",
            "value": {"value": {"kind": "arg", "position": 0}, "dim": 0},
            "intent": "in",
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 4,
            "python_position": None,
            "result_position": None,
            "value_kind": "is_present",
            "value": {"kind": "arg", "position": 1},
            "intent": "in",
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 5,
            "python_position": None,
            "result_position": None,
            "value_kind": "work",
            "value": "tmp",
            "intent": "in",
        },
    ]
    assert projection[1].value_kind == "const"
    assert projection[1].value == 1
    assert projection[2].value_kind == "len"
    assert projection[2].value == {"kind": "arg", "position": 0}
    assert projection[3].value_kind == "shape"
    assert projection[3].value == {"value": {"kind": "arg", "position": 0}, "dim": 0}
    assert projection[4].value_kind == "is_present"
    assert projection[4].value == {"kind": "arg", "position": 1}
    assert projection[5].value_kind == "work"
    assert projection[5].value == "tmp"
    assert module.functions[0].arguments[1].optional


def test_emit_native_call_hidden_native_values():
    module = SemanticModule(
        name="edited",
        functions=[
            SemanticFunction(
                name="wrapper",
                native_name="wrapper",
                arguments=[
                    SemanticArgument("x", SemanticType("Float64", dtype="Float64")),
                    SemanticArgument("b", SemanticType("Vector", dtype="Vector"), optional=True),
                ],
                projection=[
                    ProjectionMapping(native_position=0, python_position=0),
                    ProjectionMapping(native_position=1, value_kind="const", value=1),
                    ProjectionMapping(
                        native_position=2,
                        value_kind="len",
                        value={"kind": "arg", "position": 0},
                    ),
                    ProjectionMapping(
                        native_position=3,
                        value_kind="shape",
                        value={"value": {"kind": "arg", "position": 0}, "dim": 0},
                    ),
                    ProjectionMapping(
                        native_position=4,
                        value_kind="is_present",
                        value={"kind": "arg", "position": 1},
                    ),
                    ProjectionMapping(native_position=5, value_kind="work", value="tmp"),
                ],
            )
        ],
    )

    pyi = emit_module(module)

    assert "@native_call([Arg(0), Const(1), Len(Arg(0)), Arg(0).shape[0], IsPresent(Arg(1)), Work('tmp')])" in pyi


def test_plain_return_without_native_call_does_not_preserve_native_output_position():
    from_pyi = parse_pyi_text(
        """
def add(
    a: Float64,
    b: Float64
) -> Float64: ...
""",
        module_name="edited",
    )
    with_native_call = SemanticModule(
        name="edited",
        functions=[
            SemanticFunction(
                name="add",
                native_name="add",
                arguments=[
                    SemanticArgument("a", SemanticType("Float64", dtype="Float64")),
                    SemanticArgument("b", SemanticType("Float64", dtype="Float64")),
                    SemanticArgument(
                        "c",
                        SemanticType("Float64", dtype="Float64"),
                        intent="out",
                    ),
                ],
                projection=[
                    ProjectionMapping(
                        native_name="c",
                        native_position=2,
                        result_position=0,
                        intent="out",
                    )
                ],
            )
        ],
    )

    assert from_pyi != with_native_call


def test_plain_tuple_return_types_parse_component_returns():
    from_pyi = parse_pyi_text(
        """
def split(
    x: Float64
) -> tuple[Float64, Int32]: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]
    assert func.return_type.name == "Float64"
    assert [arg.name for arg in func.arguments] == ["x", "__return_1"]
    assert func.arguments[1].intent == "out"


def test_return_projection_preserves_multiple_plain_output_components():
    parser = _PyiAstParser(module_name="internal")

    return_type, returned = parser.return_projection(ast.parse("tuple[Float64, Int32, Logical]", mode="eval").body)

    assert return_type.name == "Float64"
    assert [asdict(arg) for arg in returned] == [
        asdict(
            SemanticArgument(
                "__return_1",
                SemanticType("Int32", dtype="Int32"),
                intent="out",
                metadata={"return_position": 1},
            )
        ),
        asdict(
            SemanticArgument(
                "__return_2",
                SemanticType("Logical", dtype="Logical"),
                intent="out",
                metadata={"return_position": 2},
            )
        ),
    ]


def test_method_equality_treats_argument_names_as_placeholders():
    left = parse_pyi_text(
        """
class vector:
    def scale(
        self,
        n: Int32,
        x: Float64[1:n]
    ) -> None: ...
""",
        module_name="edited",
    )
    right = parse_pyi_text(
        """
class vector:
    def scale(
        self,
        extent: Int32,
        values: Float64[1:extent]
    ) -> None: ...
""",
        module_name="edited",
    )

    assert left == right


def test_non_callable_argument_names_remain_significant():
    assert parse_pyi_text("value: Int32\n", module_name="edited") != parse_pyi_text(
        "other: Int32\n",
        module_name="edited",
    )
    assert parse_pyi_text(
        """
class vector:
    x: Float64
""",
        module_name="edited",
    ) != parse_pyi_text(
        """
class vector:
    y: Float64
""",
        module_name="edited",
    )


@pytest.mark.parametrize(
    "source, message",
    [
        (
            "value: Int32[foo.bar]\n",
            "Non-dimensional type subscriptions are not supported; use Final[...] for constants and "
            "Annotated[...] for constraints or array metadata",
        ),
        ("foo.bar: Int32\n", "Unsupported annotation target: 'foo.bar'"),
        ("value: Annotated[Int32, Name('x', 'y')]\n", "Name metadata expects one argument: \"Name('x', 'y')\""),
        ("def f(x: Int32): ...\n", "Unsupported function header: 'def f(x: Int32):'"),
        ("def f(\n    x: Int32,\n): ...\n", "Unterminated callable starting at line 1"),
        ("def f(*x: Int32) -> None: ...\n", "Unsupported function header: 'def f(*x: Int32) -> None:'"),
        ("def f(*, x: Int32) -> None: ...\n", "Unsupported function header: 'def f(*, x: Int32) -> None:'"),
        ("def f(x: Int32, /) -> None: ...\n", "Unsupported function header: 'def f(x: Int32, /) -> None:'"),
        ("def f() -> None:\n    ...\n    ...\n", "Unsupported function header: 'def f() -> None:'"),
        ("def f() -> None: pass\n", "Unsupported function header: 'def f() -> None:'"),
        ("@native_call_bad([])\ndef f(x: Int32) -> None: ...\n", "Unsupported .pyi decorator: 'native_call_bad([])'"),
        ("@bad\nclass C:\n    pass\n", "Unsupported class decorator: 'bad'"),
        ("class C:\n    @bad\n    def f(self) -> None: ...\n", "Unsupported class body decorator: 'bad'"),
        ("@native_call([])\nclass C:\n    pass\n", "Unsupported class decorator: 'native_call([])'"),
        ("@native_call(Arg(0))\ndef f(x: Int32) -> None: ...\n", "native_call expects a list of projection entries"),
        ("@native_call([Arg(0)], foo=1)\ndef f(x: Int32) -> None: ...\n", "native_call expects a single list argument"),
        ("@native_call([1])\ndef f(x: Int32) -> None: ...\n", "native_call expects projection entry calls"),
        ("@native_call([Arg(1)])\ndef f(x: Int32) -> None: ...\n", "native_call argument position is out of range: 1"),
        ("@native_call([Arg()])\ndef f(x: Int32) -> None: ...\n", "Arg expects one positional index"),
        ("@native_call([Return()])\ndef f(x: Int32) -> None: ...\n", "Return expects one positional index"),
        ("@native_call([Const()])\ndef f(x: Int32) -> None: ...\n", "Const expects one value"),
        ("@native_call([Len()])\ndef f(x: Int32) -> None: ...\n", "Len expects one value reference"),
        ("@native_call([IsPresent()])\ndef f(x: Int32) -> None: ...\n", "IsPresent expects one value reference"),
        ("@native_call([Work()])\ndef f(x: Int32) -> None: ...\n", "Work expects one workspace name"),
        (
            "@native_call([Len(1)])\ndef f(x: Int32) -> None: ...\n",
            "Expected Arg(...), Return(...), or Work(...) value reference",
        ),
        (
            "@native_call([Len(Arg(0, 1))])\ndef f(x: Int32) -> None: ...\n",
            "Arg value reference expects one positional argument",
        ),
        (
            "@native_call([Len(Unknown(0))])\ndef f(x: Int32) -> None: ...\n",
            "Expected Arg(...), Return(...), or Work(...) value reference",
        ),
        ("def f(x: Int32) -> Returns['x']: ...\n", "Returns expects a name and type: \"Returns['x']\""),
        ("value: Final[Int32, Float64]\n", "Final expects exactly one type: 'Final[Int32, Float64]'"),
        ("value: Unknown\n", "Unknown semantic type is not allowed in .pyi annotations"),
        ("value: Annotated[()]\n", "Annotated type is empty: 'Annotated[()]'"),
    ],
)
def test_parse_pyi_text_rejects_invalid_projection_and_type_forms(source: str, message: str):
    with pytest.raises(ValueError) as error:
        parse_pyi_text(source, module_name="edited")
    assert str(error.value) == message


def test_parse_pyi_text_accepts_multiline_native_call_decorator():
    module = parse_pyi_text(
        """
@native_call([
    Arg(0),
    Return(0),
])
def wrapper(
    x: Int32
) -> Float64: ...
""",
        module_name="edited",
    )

    func = module.functions[0]
    assert func.name == "wrapper"
    assert func.projection[0].python_position == 0
    assert func.projection[1].result_position == 0
    assert func.projection[1].intent == "out"


def test_fortran_to_pyi_and_back_preserves_mixed_input_output_projection():
    source = """
module solver_mod
contains
  subroutine solve(a, x, b)
    real(8), intent(in) :: a
    real(8), intent(out) :: x
    real(8), intent(in) :: b
  end subroutine solve
end module solver_mod
"""

    parsed = parse_fortran_file(source)
    modules = fortran_file_to_semantic_modules(parsed)
    pyi = "\n\n".join(emit_module(module) for module in modules)
    reparsed = parse_pyi_text(pyi, module_name="solver_mod")

    assert "@native_call" not in pyi
    func = reparsed.functions[0]
    assert func.name == "solve"
    assert [arg.name for arg in func.arguments] == ["a", "x", "b"]
    assert func.arguments[1].intent == "out"


def test_parse_pyi_text_accepts_c_and_fortran_order_constraints():
    module = parse_pyi_text(
        """
def consume(
    a: Float64[:, :],
    b: Annotated[Float64[:, :], ORDER_F],
    c: Annotated[Float64[:, :], ORDER_C],
    any_order: Annotated[Float64[:, :], ORDER_ANY]
) -> None: ...
""",
        module_name="edited",
    )

    arrays = [arg.semantic_type.storage.array for arg in module.functions[0].arguments]
    assert arrays[0].order == "ORDER_C"
    assert arrays[1].order == "ORDER_F"
    assert arrays[2].order == "ORDER_C"
    assert arrays[3].order == "ORDER_ANY"
    assert arrays[0].category is None
    assert arrays[1].source_shape == []
    assert all(not arg.semantic_type.constraints for arg in module.functions[0].arguments)


def test_parse_pyi_text_preserves_extended_array_metadata_and_nested_selector():
    module = parse_pyi_text(
        """
value: Annotated[Float64, ORDER_F, Allocatable, Pointer, Contiguous, ArrayCategory("deferred_shape"), SourceDims("1:n", "*", "extent"), LowerBounds(None, "0"), UpperBounds("n", None)]
nested: Float64[:, :][rank, kind]
name: Annotated[Ptr(String), FortranCharacterLength("16"), FortranAllocatable]

def fill(x: Annotated[Float64[:], Intent("out")]) -> None: ...
""",
        module_name="metadata",
    )

    value_type = module.variables[0].semantic_type
    value = value_type.storage.array
    nested = module.variables[1].semantic_type
    name = module.variables[2].semantic_type
    output = module.functions[0].arguments[0]
    assert value.order == "ORDER_F"
    assert value.allocatable is True
    assert value.pointer is True
    assert value.contiguous is True
    assert value.category == "deferred_shape"
    assert value.source_shape == ["1:n", "*", "extent"]
    assert value.lower_bounds == [None, "0"]
    assert value.upper_bounds == ["n", None]
    assert value_type.constraints == []
    assert nested.metadata["rank_selector"] == "rank, kind"
    assert nested.storage.array.metadata["rank_selector"] == "rank, kind"
    assert name.metadata["fortran_character_length"] == "16"
    assert name.metadata["fortran_allocatable"] is True
    assert output.intent == "out"


def test_parse_pyi_text_handles_callable_and_pointer_storage_variants():
    module = parse_pyi_text(
        """
import typing

plain_callback: Callable
qualified_callback: typing.Callable
opaque_callback: Callable[..., Float64]
constant: Const(Int32)
deep: Ptr[3](Const(Float64))
rank_any: Float64[...]
strided: Float64[0:n:Strided]
computed: Float64[size(xl)]
bounded_answer: Final[Annotated[Int32, Bounded(1, 8)]]
nested_answer: Final[Final[Int32]]
""",
        module_name="storage",
    )

    plain, qualified, callback, constant, deep, rank_any, strided, computed, bounded, nested = [
        var.semantic_type for var in module.variables
    ]
    assert plain.name == "Callable"
    assert plain.dtype == "Callable"
    assert qualified.name == "Callable"
    assert qualified.dtype == "Callable"
    assert callback.metadata["arguments"] is None
    assert callback.dtype == "Callable"
    assert callback.metadata["return"].name == "Float64"
    assert constant.storage.kind == "value"
    assert constant.storage.read_only is True
    assert deep.storage.kind == "pointer"
    assert deep.storage.pointer_depth == 3
    assert deep.storage.read_only is True
    assert deep.storage.mutable is False
    assert rank_any.storage.array.rank is None
    assert rank_any.rank == 0
    assert strided.storage.array.contiguous is False
    assert computed.shape == ["size(xl)"]
    assert bounded.constraints == [
        SemanticConstraint("Bounded", [1, 8]),
        SemanticConstraint("Constant"),
    ]
    assert nested.constraints == [SemanticConstraint("Constant")]


def test_parse_pyi_text_preserves_module_fields_and_private_callable_arguments():
    module = parse_pyi_text(
        """
output: Annotated[Float64[:], Intent("out")] = ...

def consume(value: private[Int32]) -> None: ...
""",
        module_name="fields",
    )

    assert module.variables[0].intent == "out"
    assert module.variables[0].optional is True
    assert module.functions[0].arguments[0].visibility == "private"


@pytest.mark.parametrize(
    "source, message",
    [
        ("value: Const(Int32, Float64)\n", "Const type expects one argument: 'Const(Int32, Float64)'"),
        ("value: Ptr(Int32, Float64)\n", "Ptr type expects one argument: 'Ptr(Int32, Float64)'"),
        ("value: Ptr[1](Int32)\n", "Ptr[1](...) is invalid; use Ptr(...)"),
        ("value: Callable[Int32]\n", "Callable expects argument types and a return type: 'Callable[Int32]'"),
        ("value: Callable[Int32, Float64]\n", "Callable arguments must be a list: 'Callable[Int32, Float64]'"),
        (
            "value: Annotated[Float64[:], Intent('out', 'extra')]\n",
            "Intent metadata expects one argument: \"Intent('out', 'extra')\"",
        ),
        ("value: Annotated[Float64[:], SourceShape('n')]\n", "SourceShape metadata is not supported; use SourceDims"),
        (
            "value: Int32[Constant]\n",
            "Non-dimensional type subscriptions are not supported; use Final[...] for constants and "
            "Annotated[...] for constraints or array metadata",
        ),
        (
            "value: Float64[ORDER_F]\n",
            "Non-dimensional type subscriptions are not supported; use Final[...] for constants and "
            "Annotated[...] for constraints or array metadata",
        ),
        (
            "value: Float64[Shape]\n",
            "Non-dimensional type subscriptions are not supported; use Final[...] for constants and "
            "Annotated[...] for constraints or array metadata",
        ),
        (
            "value: Float64[Shape('n')]\n",
            "Non-dimensional type subscriptions are not supported; use Final[...] for constants and "
            "Annotated[...] for constraints or array metadata",
        ),
        ("value: Annotated[Int32, Constant]\n", "Constant metadata is not supported; use Final[...]"),
        ("value: Annotated[Float64[:], Shape('n')]\n", "Shape metadata is not supported; put dimensions inside T[...]"),
        (
            "value: Annotated[Int32, Bounded(lower=1)]\n",
            "Constraint metadata expects positional arguments only: 'Bounded(lower=1)'",
        ),
        ("value: Annotated[Int32, 'bad']\n", "Unsupported Annotated metadata: \"'bad'\""),
        ("value: Float64[:, foo.bar]\n", "Unsupported array dimension expression: 'foo.bar'"),
        (
            "value: Int32[()]\n",
            "Non-dimensional type subscriptions are not supported; use Final[...] for constants and "
            "Annotated[...] for constraints or array metadata",
        ),
        (
            "@native_call([Arg(0).other[0]])\ndef f(x: Int32) -> None: ...\n",
            "native_call expects projection entry calls",
        ),
    ],
)
def test_parse_pyi_text_rejects_additional_invalid_storage_forms(source: str, message: str):
    with pytest.raises(ValueError) as error:
        parse_pyi_text(source, module_name="invalid")
    assert str(error.value) == message


def test_pyi_parser_internal_projection_helpers_preserve_native_names():
    parser = _PyiAstParser(module_name="internal")
    return_type, returned_values = parser.return_projection(
        ast.parse("tuple[Float64, Returns['extra', Int32, Optional], Returns['other', Float64]]", mode="eval").body
    )
    pointer = parser.semantic_type(ast.parse("Ptr(Float64)", mode="eval").body)
    returned = SemanticArgument("result", SemanticType("Float64"), intent="out", metadata={"return_position": 1})
    mapping = ProjectionMapping(native_name="native_result", result_position=1, intent="out")
    _, values = parser._apply_native_call_returns(None, [returned], [mapping])
    native_arg = SemanticArgument("python_name", SemanticType("Int32"))
    arg_mapping = ProjectionMapping(native_name="native_name", python_position=0)
    parser._apply_native_call_argument_names([native_arg], {}, [arg_mapping])

    assert return_type.name == "Float64"
    assert returned_values[0].name == "extra"
    assert returned_values[0].intent == "out"
    assert returned_values[0].optional is True
    assert returned_values[0].metadata == {"return_position": 1}
    assert returned_values[0].semantic_type.ownership.mutable is True
    assert returned_values[1].name == "other"
    assert returned_values[1].metadata == {"return_position": 2}
    assert pointer.storage.mutable is True
    assert pointer.ownership.mutable is True
    assert values[0].name == "native_result"
    assert arg_mapping.native_name == "native_name"


def test_node_text_falls_back_to_node_type_for_empty_unparse():
    assert _node_text(ast.Module(body=[], type_ignores=[])) == "Module"


def test_generated_pyi_compares_equal_to_original_ir_for_all_fortran_fixtures(tmp_path: Path):
    assert FORTRAN_PYI_COMPARE_FIXTURES

    checked_modules = 0
    skipped_unresolved_types = 0
    for fixture in FORTRAN_PYI_COMPARE_FIXTURES:
        try:
            modules = _semantic_modules_for_source(fixture)
        except ValueError as exc:
            if "Unsupported Fortran semantic type" not in str(exc):
                raise
            skipped_unresolved_types += 1
            continue

        for module in modules:
            pyi_path = tmp_path / f"{module.name}.pyi"
            pyi_path.write_text(emit_module(module) + "\n", encoding="utf-8")

            try:
                assert load_pyi_file(pyi_path) == module
            finally:
                pyi_path.unlink(missing_ok=True)

            checked_modules += 1

    assert checked_modules > 0
    assert skipped_unresolved_types > 0
    assert not list(tmp_path.glob("*.pyi"))
