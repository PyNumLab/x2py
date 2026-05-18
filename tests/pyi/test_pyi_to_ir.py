from pathlib import Path
import pytest

from semantics.fortran2ir import fortran_file_to_semantic_modules
from semantics.models import (
    ProjectionMapping,
    SemanticArgument,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticModule,
    SemanticType,
)
from semantics.pyi_parser import convert_pyi_to_ir, load_pyi_file, parse_pyi_text
from semantics.pyi_printer import emit_module
from tests._shared.fixture_outputs import FORTRAN_DATA_DIR, FORTRAN_SUFFIXES
from x2py import parse_fortran_file


PYI_COMPARE_DIRS = ("general", "blas", "lapack", "scifortran")
FORTRAN_PYI_COMPARE_FIXTURES = sorted(
    path
    for dirname in PYI_COMPARE_DIRS
    for path in (FORTRAN_DATA_DIR / dirname).rglob("*")
    if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
)


def _semantic_modules_for_source(path: Path):
    parsed = parse_fortran_file(
        path.read_text(encoding="utf-8"),
        filename=str(path.relative_to(FORTRAN_DATA_DIR)),
    )
    return fortran_file_to_semantic_modules(parsed, standalone_module_name=path.stem)


def test_parse_pyi_text_allows_user_modified_stub():
    pyi = """
import iso_c_binding

class particle:
    id: Int32

scale: private[Float64]

def touch(
    p: particle
) -> Returns["p", particle]: ...
"""

    module = parse_pyi_text(pyi, module_name="edited")

    assert module.name == "edited"
    assert module.imports == ["iso_c_binding"]
    assert module.classes[0].name == "particle"
    assert module.variables[0].name == "scale"
    assert module.variables[0].visibility == "private"
    assert module.functions[0].arguments[0].intent == "inout"


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


def test_convert_pyi_to_ir_and_import_parser_edge_cases():
    module = convert_pyi_to_ir("from m import a, b as c\n", module_name="edited")
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


def test_parse_pyi_text_class_body_visibility_and_native_call():
    module = parse_pyi_text(
        """
class wrapper:
    pass

class particle:
    @private
    @native_call([Arg(0)])
    def reset(self: particle) -> None: ...
""",
        module_name="edited",
    )

    empty_cls, particle_cls = module.classes
    assert empty_cls.name == "wrapper"
    assert particle_cls.methods[0].visibility == "private"
    assert particle_cls.methods[0].projection[0].python_position == 0


def test_pyi_parser_reports_unsupported_lines_and_invalid_helpers():
    with pytest.raises(ValueError, match="Unsupported .pyi node"):
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


def test_pyi_parser_ignores_unknown_annotation_metadata():
    module = parse_pyi_text(
        """
value: Annotated[Int32, Other("native_value")]
alias: Annotated[Int32, Name("native_alias")]
""",
        module_name="edited",
    )

    assert module.variables[0].name == "value"
    assert module.variables[1].name == "native_alias"


def test_parse_pyi_text_accepts_ast_only_projection_value_refs():
    module = parse_pyi_text(
        """
@native_call([Return(0), Len(Return(0)), Shape(Work("tmp"), 0)])
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
    x: Float64[Shape('1:n'), ORDER_F]
) -> Returns["x", Float64[Shape('1:n'), ORDER_F]]: ...
""",
        module_name="edited",
    )
    right = parse_pyi_text(
        """
def resize(
    extent: Int32,
    values: Float64[Shape('1:extent'), ORDER_F]
) -> Returns["values", Float64[Shape('1:extent'), ORDER_F]]: ...
""",
        module_name="edited",
    )

    assert left == right
    assert left.functions[0].arguments[0] != right.functions[0].arguments[0]


def test_plain_return_type_compares_equal_to_unnamed_output_argument():
    from_pyi = parse_pyi_text(
        """
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
            )
        ],
    )

    assert from_pyi == from_ir


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

    assert from_pyi == from_ir
    assert from_pyi.functions[0].arguments[2].intent == "out"
    assert from_pyi.functions[0].projection[2].native_position == 2


def test_native_call_accepts_hidden_native_values():
    module = parse_pyi_text(
        """
@native_call([
    Arg(0),
    Const(1),
    Len(Arg(0)),
    Shape(Arg(0), 0),
    IsPresent(Arg(1)),
    Work("tmp"),
])
def wrapper(
    x: Float64[Shape("n"), ORDER_F],
    b: Vector | None = None
) -> None: ...
""",
        module_name="edited",
    )

    projection = module.functions[0].projection

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

    assert "@native_call([Arg(0), Const(1), Len(Arg(0)), Shape(Arg(0), 0), IsPresent(Arg(1)), Work('tmp')])" in pyi


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


def test_plain_tuple_return_types_compare_equal_to_unnamed_output_arguments():
    from_pyi = parse_pyi_text(
        """
def split(
    x: Float64
) -> tuple[Float64, Int32]: ...
""",
        module_name="edited",
    )
    from_ir = SemanticModule(
        name="edited",
        functions=[
            SemanticFunction(
                name="split",
                native_name="split",
                arguments=[
                    SemanticArgument("x", SemanticType("Float64", dtype="Float64")),
                    SemanticArgument(
                        "lo",
                        SemanticType("Float64", dtype="Float64"),
                        intent="out",
                    ),
                    SemanticArgument(
                        "hi",
                        SemanticType("Int32", dtype="Int32"),
                        intent="out",
                    ),
                ],
            )
        ],
    )

    assert from_pyi == from_ir


def test_method_equality_treats_argument_names_as_placeholders():
    left = parse_pyi_text(
        """
class vector:
    def scale(
        self,
        n: Int32,
        x: Float64[Shape('1:n'), ORDER_F]
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
        values: Float64[Shape('1:extent'), ORDER_F]
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
        ("value: Int32[foo.bar]\n", "Unsupported semantic type constraint"),
        ("foo.bar: Int32\n", "Unsupported annotation target"),
        ("value: Annotated[Int32, Name('x', 'y')]\n", "Name metadata expects one argument"),
        ("def f(x: Int32): ...\n", "Unsupported function header"),
        ("def f(\n    x: Int32,\n): ...\n", "Unterminated callable starting at line 1"),
        ("def f(*x: Int32) -> None: ...\n", "Unsupported function header"),
        ("def f() -> None:\n    ...\n    ...\n", "Unsupported function header"),
        ("def f() -> None: pass\n", "Unsupported function header"),
        ("@native_call_bad([])\ndef f(x: Int32) -> None: ...\n", "Unsupported .pyi decorator"),
        ("@native_call([])\nclass C:\n    pass\n", "Unsupported class decorator"),
        ("@native_call(Arg(0))\ndef f(x: Int32) -> None: ...\n", "native_call expects a list of projection entries"),
        ("@native_call([Arg(0)], foo=1)\ndef f(x: Int32) -> None: ...\n", "native_call expects a single list argument"),
        ("@native_call([1])\ndef f(x: Int32) -> None: ...\n", "projection entry calls"),
        ("@native_call([Arg(1)])\ndef f(x: Int32) -> None: ...\n", "native_call argument position is out of range"),
        ("@native_call([Arg()])\ndef f(x: Int32) -> None: ...\n", "Arg expects one positional index"),
        ("@native_call([Return()])\ndef f(x: Int32) -> None: ...\n", "Return expects one positional index"),
        ("@native_call([Const()])\ndef f(x: Int32) -> None: ...\n", "Const expects one value"),
        ("@native_call([Len()])\ndef f(x: Int32) -> None: ...\n", "Len expects one value reference"),
        (
            "@native_call([Shape(Arg(0))])\ndef f(x: Int32) -> None: ...\n",
            "Shape expects a value reference and dimension",
        ),
        ("@native_call([IsPresent()])\ndef f(x: Int32) -> None: ...\n", "IsPresent expects one value reference"),
        ("@native_call([Work()])\ndef f(x: Int32) -> None: ...\n", "Work expects one workspace name"),
        ("@native_call([Len(1)])\ndef f(x: Int32) -> None: ...\n", "Expected Arg"),
        (
            "@native_call([Len(Arg(0, 1))])\ndef f(x: Int32) -> None: ...\n",
            "value reference expects one positional argument",
        ),
        ("def f(x: Int32) -> Returns['x']: ...\n", "Returns expects a name and type"),
    ],
)
def test_parse_pyi_text_rejects_invalid_projection_and_type_forms(source: str, message: str):
    with pytest.raises(ValueError, match=message):
        parse_pyi_text(source, module_name="edited")


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

    assert "@native_call([Arg(0), Return(0), Arg(1)])" in pyi
    func = reparsed.functions[0]
    assert func.name == "solve"
    assert [m.native_position for m in func.projection] == [0, 1, 2]
    assert func.projection[0].python_position == 0
    assert func.projection[1].result_position == 0
    assert func.projection[2].python_position == 1


def test_parse_pyi_text_accepts_c_and_fortran_order_constraints():
    module = parse_pyi_text(
        """
def consume(
    a: Float64[Shape(':', ':'), ORDER_C],
    b: Float64[Shape(':', ':'), ORDER_F]
) -> None: ...
""",
        module_name="edited",
    )

    constraint_names = [
        constraint.name
        for arg in module.functions[0].arguments
        for constraint in arg.semantic_type.constraints
    ]
    assert "ORDER_C" in constraint_names
    assert "ORDER_F" in constraint_names


def test_generated_pyi_compares_equal_to_original_ir_for_all_fortran_fixtures(tmp_path: Path):
    assert FORTRAN_PYI_COMPARE_FIXTURES

    checked_modules = 0
    for fixture in FORTRAN_PYI_COMPARE_FIXTURES:
        for module in _semantic_modules_for_source(fixture):
            pyi_path = tmp_path / f"{module.name}.pyi"
            pyi_path.write_text(emit_module(module) + "\n", encoding="utf-8")

            try:
                assert load_pyi_file(pyi_path) == module
            finally:
                pyi_path.unlink(missing_ok=True)

            checked_modules += 1

    assert checked_modules > 0
    assert not list(tmp_path.glob("*.pyi"))
