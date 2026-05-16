from pathlib import Path

from semantics.fortran2ir import fortran_file_to_semantic_modules
from semantics.models import ProjectionMapping, SemanticArgument, SemanticFunction, SemanticModule, SemanticType
from semantics.pyi_parser import load_pyi_file, parse_pyi_text
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
