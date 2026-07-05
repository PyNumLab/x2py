import ast
import re
from dataclasses import asdict
from pathlib import Path

import pytest

import x2py.pyi_pipeline as pyi_pipeline
from x2py.contracts import CONTRACT_SYMBOLS
from x2py.semantic_metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    BIND_TARGET_METADATA,
    PROJECTED_OUTPUT_METADATA,
    SNAPSHOT_TYPE_METADATA,
    SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA,
    USER_PRIVATE_METADATA,
)
from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules
from x2py.semantics.models import (
    CALLBACK_DECLARATION_ACCESS_METADATA,
    ProjectionMapping,
    PYTHON_VALUE_IMMUTABLE,
    PYTHON_VALUE_MUTABILITY_METADATA,
    SemanticArgument,
    SemanticConstraint,
    SemanticField,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticModule,
    SemanticType,
    SemanticVariable,
)
from x2py.semantics.pyi2ir import (
    _PyiAstParser,
    _node_text,
    convert_pyi_to_ir,
)
from x2py.pyi_pipeline import pyi_file_to_semantic_module, pyi_paths_to_semantic_modules, pyi_text_to_semantic_module
from x2py.pyi_parser import parse_pyi_text as parse_pyi_ast_text
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast as _semantic_ir_to_codegen_ast
from x2py.semantics.native_contract import native_contract_issues
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.readiness import assess_semantic_wrap_readiness
from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator
from x2py.codegen.printers.pyi_printer import emit_module
from x2py.codegen.scope import Scope
from tests._shared.fixture_outputs import FORTRAN_DATA_DIR, FORTRAN_SUFFIXES
from x2py import parse_fortran_file


PYI_COMPARE_DIRS = ("general", "blas", "lapack", "scifortran")
_ALL_FORTRAN_PYI_COMPARE_FIXTURES = sorted(
    path
    for dirname in PYI_COMPARE_DIRS
    for path in (FORTRAN_DATA_DIR / dirname).rglob("*")
    if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
)


def semantic_ir_to_codegen_ast(node, *args, **kwargs):
    if isinstance(node, SemanticModule):
        complete_semantic_policies(node)
    return _semantic_ir_to_codegen_ast(node, *args, **kwargs)


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
CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def parse_pyi_text(source: str, *args, **kwargs):
    if "x2py.contracts" in source:
        return pyi_text_to_semantic_module(source, *args, **kwargs)
    return pyi_text_to_semantic_module(f"{CONTRACT_IMPORT}{source}", *args, **kwargs)


def test_pyi_parser_returns_python_ast_only():
    tree = parse_pyi_ast_text("def scale(value: Float64) -> Float64: ...\n", filename="scale.pyi")

    assert isinstance(tree, ast.Module)
    assert isinstance(tree.body[0], ast.FunctionDef)
    assert tree.body[0].name == "scale"


def test_convert_pyi_to_ir_accepts_parsed_pyi_ast_only():
    source = f"{CONTRACT_IMPORT}value: Int32\n"
    tree = parse_pyi_ast_text(source, filename="contract.pyi")

    module = convert_pyi_to_ir(tree, module_name="parsed", source=source)

    assert module.name == "parsed"
    assert module.variables[0].name == "value"
    with pytest.raises(TypeError, match=r"expects a Python ast\.Module"):
        convert_pyi_to_ir(source)


def _semantic_modules_for_source(path: Path):
    parsed = parse_fortran_file(
        path.read_text(encoding="utf-8"),
        filename=str(path.relative_to(FORTRAN_DATA_DIR)),
    )
    return fortran_file_to_semantic_modules(parsed, standalone_module_name=path.stem)


def test_convert_pyi_to_ir_dispatches_nested_and_qualified_semantic_types():
    module = parse_pyi_text(
        """
public_value: Int32
bounded: Final[Annotated[Int32, Bounded(1, 8)]]
callback: Callable
pointer: Addr(Float64)
raw_pointer: Addr(Float64)
""",
        module_name="dispatch",
    )

    public_value, bounded, callback, pointer, raw_pointer = module.variables
    assert isinstance(public_value, SemanticVariable)
    assert public_value.visibility == "public"
    assert bounded.semantic_type.constraints == [
        SemanticConstraint("Bounded", [1, 8]),
        SemanticConstraint("Constant"),
    ]
    assert callback.semantic_type.name == "Callable"
    assert pointer.semantic_type.storage.kind == "address"
    assert pointer.semantic_type.storage.metadata[ADDRESS_ROLE_METADATA] == ADDRESS_ROLE_RAW
    assert raw_pointer.semantic_type.storage.read_only is False


def test_convert_pyi_to_ir_requires_imported_contract_types():
    with pytest.raises(ValueError, match="Contract type 'Float64' must be imported"):
        pyi_text_to_semantic_module("value: Float64\n", module_name="bare")

    module = pyi_text_to_semantic_module(
        """
class Float64:
    pass

value: Float64
""",
        module_name="user_type",
    )

    assert module.classes[0].name == "Float64"
    assert module.variables[0].semantic_type.name == "Float64"


def test_convert_pyi_to_ir_follows_arbitrary_contract_aliases():
    module = pyi_text_to_semantic_module(
        """
from x2py.contracts import Addr as AddressOf, Arg as PythonArg, Final as Frozen
from x2py.contracts import Flat as Layout, Float64 as F64, Int32 as I32, native_call as call

Flat: Frozen[I32] = 10

@call([AddressOf(PythonArg(0))])
def inspect(values: F64[Layout], dense: F64[Flat]) -> None: ...
""",
        module_name="aliases",
    )

    assert module.variables[0].name == "Flat"
    assert module.functions[0].arguments[0].semantic_type.storage.array.category == "assumed_size"
    assert module.functions[0].arguments[1].semantic_type.shape == ["Flat"]


def test_convert_pyi_to_ir_preserves_immutable_python_value_metadata():
    module = parse_pyi_text(
        """
def scale(
    values: Annotated[Float64[:], Immutable]
) -> Returns["values", Float64[:]]: ...
""",
        module_name="immutable_values",
    )

    values = module.functions[0].arguments[0].semantic_type
    assert values.metadata[PYTHON_VALUE_MUTABILITY_METADATA] == PYTHON_VALUE_IMMUTABLE

    emitted = emit_module(module)
    assert "Immutable" in emitted
    reparsed = parse_pyi_text(emitted, module_name="immutable_values")
    reparsed_values = reparsed.functions[0].arguments[0].semantic_type
    assert reparsed_values.metadata[PYTHON_VALUE_MUTABILITY_METADATA] == PYTHON_VALUE_IMMUTABLE


def test_convert_pyi_to_ir_rejects_immutable_writable_borrowed_view_argument():
    with pytest.raises(ValueError, match="Immutable values cannot request"):
        parse_pyi_text(
            """
def normalize(
    values: Annotated[Float64[:], Immutable, Transfer("borrowed_view")]
) -> None: ...
""",
            module_name="invalid_immutable_view",
        )


def test_convert_pyi_to_ir_allows_user_modified_stub():
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


def test_convert_pyi_to_ir_accepts_mutable_module_literal_defaults():
    source = """counter: Int32 = 41
scale: Float64 = 2.5
label: String[8] = "ready"
"""

    module = parse_pyi_text(source, module_name="runtime_state")

    assert [variable.default_value for variable in module.variables[:2]] == ["41", "2.5"]
    assert ast.literal_eval(module.variables[2].default_value) == "ready"


@pytest.mark.parametrize(
    "source",
    [
        "counter: Int32 = f(42)\n",
        "counter: Int32 = x + 1\n",
        "counter: Int32 = SOME_NAME\n",
    ],
)
def test_convert_pyi_to_ir_rejects_mutable_module_expression_defaults(source):
    with pytest.raises(ValueError, match="Mutable defaults must be literal values"):
        parse_pyi_text(source, module_name="runtime_state")


def test_convert_pyi_to_ir_round_trips_enum_like_integer_constants():
    source = """STATUS_OK: Final[Int] = 0
STATUS_NEXT: Final[Int] = STATUS_OK + 1

def set_status(
    value: Int
) -> None: ...
"""

    module = parse_pyi_text(source, module_name="status_api")

    assert module.classes == []
    assert [item.name for item in module.variables] == ["STATUS_OK", "STATUS_NEXT"]
    assert module.variables[1].default_value == "STATUS_OK + 1"
    assert module.functions[0].arguments[0].semantic_type.name == "Int"
    emitted = emit_module(module)
    assert "STATUS_NEXT: Final[Int] = STATUS_OK + 1" in emitted
    assert parse_pyi_text(emitted, module_name="status_api") == module


def test_convert_pyi_to_ir_rejects_enum_classes():
    source = """class status(Enum[Int]):
    pass
"""

    with pytest.raises(ValueError, match=r"Enum declarations are not supported"):
        parse_pyi_text(source, module_name="status_api")


def test_convert_pyi_to_ir_preserves_callable_signature_metadata():
    module = parse_pyi_text(
        """
from x2py.contracts import Callable, Float64, Int32

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


def test_convert_pyi_to_ir_preserves_callback_argument_abi_wrappers():
    module = parse_pyi_text(
        """
class particle:
    mass: Float64

def register(
    callback: Callable[
        [
            Int32,
            Float64[:],
            Float64[()],
            PassByRef(Float64),
            In(Int32),
            Out(Float64[:]),
            InOut(Float64[()]),
        ],
        None,
    ]
) -> None: ...
""",
        module_name="callbacks",
    )

    callback_type = module.functions[0].arguments[0].semantic_type
    callback_arguments = callback_type.metadata["callback_arguments"]

    assert [arg.metadata[CALLBACK_DECLARATION_ACCESS_METADATA] for arg in callback_arguments] == [
        "unspecified",
        "unspecified",
        "unspecified",
        "unspecified",
        "read",
        "write",
        "readwrite",
    ]
    assert [arg.origin.metadata["value"] for arg in callback_arguments] == [
        True,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
    assert callback_arguments[0].semantic_type.storage is None
    assert callback_arguments[1].semantic_type.storage.kind == "array"
    assert callback_arguments[2].semantic_type.storage.kind == "array"
    assert callback_arguments[3].semantic_type.storage.kind == "reference"
    assert callback_arguments[4].semantic_type.storage.read_only is True
    assert callback_arguments[5].semantic_type.storage.mutable is True
    assert callback_arguments[6].semantic_type.storage.mutable is True


@pytest.mark.parametrize(
    "annotation",
    [
        "Callable[[Out(String[8])], None]",
        "Callable[[InOut(String[8])], None]",
        "Callable[[PassByRef(String[8])], None]",
    ],
)
def test_callback_writable_plain_string_requires_scalar_storage(annotation: str):
    module = parse_pyi_text(
        f"def register(callback: {annotation}) -> None: ...",
        module_name="callbacks",
    )

    with pytest.raises(ValueError, match="Writable callback strings require mutable scalar character storage"):
        complete_semantic_policies(module)


@pytest.mark.parametrize(
    "annotation",
    [
        "Callable[[In(String[8])], None]",
        "Callable[[Out(String[8][()])], None]",
        "Callable[[InOut(String[8][()])], None]",
    ],
)
def test_callback_string_storage_contracts_complete(annotation: str):
    module = parse_pyi_text(
        f"def register(callback: {annotation}) -> None: ...",
        module_name="callbacks",
    )

    complete_semantic_policies(module)
    callback_type = module.functions[0].arguments[0].semantic_type
    callback_argument = callback_type.metadata["callback_arguments"][0]
    assert callback_argument.semantic_type.name == "String"


def test_convert_pyi_to_ir_infers_callback_dimension_argument_names():
    module = parse_pyi_text(
        """
def apply_transform(
    callback: Callable[[PassByRef(Int32), Float64[count]], Float64[count]]
) -> None: ...
""",
        module_name="callbacks",
    )

    callback_type = module.functions[0].arguments[0].semantic_type
    callback_arguments = callback_type.metadata["callback_arguments"]
    assert [arg.name for arg in callback_arguments] == ["count", "arg_1"]
    assert callback_type.metadata["return"].shape == ["count"]


def test_convert_pyi_to_ir_accepts_import_aliases():
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


def test_convert_pyi_to_ir_accepts_relative_imports():
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


def test_convert_pyi_to_ir_annotates_types_from_each_import_statement():
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


def test_pyi_paths_to_semantic_modules_reconciles_opaque_and_edited_external_types(tmp_path: Path):
    physics = tmp_path / "physics.pyi"
    types_mod = tmp_path / "types_mod.pyi"
    physics.write_text(
        f"""
{CONTRACT_IMPORT}
from types_mod import particle

answer: Int32

def create_particle() -> particle: ...

def move(p: Annotated[particle, CompatibleHandle]) -> None: ...
""",
        encoding="utf-8",
    )
    types_mod.write_text(
        f"""
{CONTRACT_IMPORT}
class particle(Opaque):
    pass
""",
        encoding="utf-8",
    )

    modules = {module.name: module for module in pyi_paths_to_semantic_modules(tmp_path)}
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
        f"""
{CONTRACT_IMPORT}
class particle:
    mass: Float64
""",
        encoding="utf-8",
    )
    edited_modules = {module.name: module for module in pyi_paths_to_semantic_modules([physics, types_mod])}
    edited_ref = edited_modules["physics"].functions[0].return_type.metadata["external_type_ref"]

    assert edited_ref["wrapped"] is True
    assert edited_ref["representation"] == "wrapped"
    assert edited_modules["types_mod"].classes[0].fields[0].name == "mass"


def test_pyi_paths_to_semantic_modules_preserves_dotted_module_names_from_directory(tmp_path: Path):
    package = tmp_path / "shared"
    package.mkdir()
    (tmp_path / "physics.pyi").write_text(
        """
from shared.types_mod import particle

def move(p: particle) -> None: ...
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

    modules = {module.name: module for module in pyi_paths_to_semantic_modules(tmp_path)}
    particle_ref = modules["physics"].functions[0].arguments[0].semantic_type.metadata["external_type_ref"]

    assert "shared.types_mod" in modules
    assert particle_ref["origin_module"] == "shared.types_mod"
    assert particle_ref["representation"] == "opaque"


def test_pyi_paths_to_semantic_modules_handles_duplicate_roots_and_ambiguous_module_names(tmp_path: Path):
    package = tmp_path / "shared"
    package.mkdir()
    pyi_path = package / "types_mod.pyi"
    pyi_path.write_text("class particle:\n    pass\n", encoding="utf-8")

    assert [module.name for module in pyi_paths_to_semantic_modules([tmp_path, tmp_path])] == ["shared.types_mod"]
    with pytest.raises(ValueError) as error:
        pyi_paths_to_semantic_modules([tmp_path, package])
    assert str(error.value) == f"Ambiguous module name for {pyi_path}: 'shared.types_mod' or 'types_mod'"


def test_pyi_paths_to_semantic_modules_ignores_directories_with_pyi_suffix(tmp_path: Path):
    (tmp_path / "ignored.pyi").mkdir()
    (tmp_path / "types_mod.pyi").write_text("class particle:\n    pass\n", encoding="utf-8")

    assert [module.name for module in pyi_paths_to_semantic_modules(tmp_path)] == ["types_mod"]


def test_pyi_file_to_semantic_module_and_modules_forward_module_name_encoding_and_filename(tmp_path: Path):
    pyi_path = tmp_path / "types_mod.pyi"
    pyi_path.write_bytes("# caf\xe9\nclass particle:\n    pass\n".encode("latin-1"))

    module = pyi_file_to_semantic_module(pyi_path, module_name="custom.types_mod", encoding="latin-1")
    assert module.name == "custom.types_mod"
    assert module.classes[0].name == "particle"
    assert pyi_paths_to_semantic_modules(pyi_path, encoding="latin-1")[0].name == "types_mod"

    invalid_path = tmp_path / "invalid.pyi"
    invalid_path.write_text("from broken import\n", encoding="utf-8")
    with pytest.raises(SyntaxError) as error:
        pyi_file_to_semantic_module(invalid_path)
    assert error.value.filename == str(invalid_path)

    semantic_invalid_path = tmp_path / "semantic_invalid.pyi"
    semantic_invalid_path.write_text("def f(x) -> None: ...\n", encoding="utf-8")
    with pytest.raises(ValueError) as semantic_error:
        pyi_file_to_semantic_module(semantic_invalid_path)
    message = str(semantic_error.value)
    assert message.startswith(f"{semantic_invalid_path}: ")
    assert "Expected typed argument: 'x'" in message


def test_pyi_conversion_cache_reuses_file_parse_for_same_module_key(monkeypatch, tmp_path: Path):
    pyi_path = tmp_path / "types_mod.pyi"
    pyi_path.write_text(f"{CONTRACT_IMPORT}value: Int32\n", encoding="utf-8")

    original_parse = pyi_pipeline.parse_pyi_text
    parsed_filenames: list[str] = []

    def parse_once(source: str, *, filename: str = "<pyi>"):
        parsed_filenames.append(filename)
        return original_parse(source, filename=filename)

    monkeypatch.setattr(pyi_pipeline, "parse_pyi_text", parse_once)
    cache = pyi_pipeline._PyiSemanticModuleCache()

    first = cache.file_to_semantic_module(pyi_path)
    second = cache.file_to_semantic_module(pyi_path, module_name="types_mod")
    renamed = cache.file_to_semantic_module(pyi_path, module_name="renamed_types")

    assert first is second
    assert renamed is not first
    assert [Path(filename) for filename in parsed_filenames] == [pyi_path, pyi_path]


def test_convert_pyi_to_ir_and_import_parser_edge_cases():
    module = pyi_text_to_semantic_module("from m import a, b as c\n", module_name="edited")
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
        pyi_text_to_semantic_module("from m import\n", module_name="edited")


def test_convert_pyi_to_ir_forwards_filename_to_syntax_errors():
    with pytest.raises(SyntaxError) as error:
        parse_pyi_text("from broken import\n", filename="custom.pyi")
    assert error.value.filename == "custom.pyi"


def test_convert_pyi_to_ir_class_body_visibility_and_native_call():
    module = parse_pyi_text(
        """
class wrapper:
    pass

class particle:
    @private
    @native_call([Pass()])
    def reset(self) -> Int32: ...
""",
        module_name="edited",
    )

    empty_cls, particle_cls = module.classes
    assert empty_cls.name == "wrapper"
    assert particle_cls.methods[0].name == "reset"
    assert particle_cls.methods[0].native_name == "reset"
    assert particle_cls.methods[0].visibility == "private"
    assert particle_cls.methods[0].origin.metadata[USER_PRIVATE_METADATA] is True
    assert [arg.name for arg in particle_cls.methods[0].arguments] == ["self"]
    assert particle_cls.methods[0].return_type.name == "Int32"
    assert asdict(particle_cls.methods[0].projection[0]) == {
        "python_name": "self",
        "native_name": "self",
        "native_position": 0,
        "python_position": 0,
        "result_position": None,
        "value_kind": None,
        "value": None,
    }
    emitted = emit_module(module)
    assert "    @private\n    def reset(self) -> Int32: ..." in emitted
    reparsed = parse_pyi_text(emitted, module_name="edited")
    assert reparsed.classes[1].methods[0].visibility == "private"
    assert reparsed.classes[1].methods[0].origin.metadata[USER_PRIVATE_METADATA] is True
    assert emit_module(reparsed) == emitted


def test_convert_pyi_to_ir_distinguishes_generated_and_linked_constructors():
    generated = parse_pyi_text(
        """
class state:
    def __init__(
        self,
        *,
        id: Int32 = 7,
        scale: Float64 = 2.5
    ) -> None: ...

    id: Int32 = 7
    scale: Float64 = 2.5
""",
        module_name="generated",
    )

    generated_cls = generated.classes[0]
    assert generated_cls.origin.source_language == "fortran"
    assert generated_cls.methods == []

    linked = parse_pyi_text(
        """
@private
@native_call([Arg(0), Addr(Arg(1)), Addr(Arg(2))])
def init_state(
    self: state,
    seed: Int32,
    scale: Float64 = ...
) -> None: ...

class state:
    def __init__(
        self,
        *,
        id: Int32 = 7,
        scale: Float64 = 2.5
    ) -> None: ...

    @overload("init_state")
    def __init__(
        self,
        seed: Int32,
        scale: Float64 = ...
    ) -> None: ...

    id: Int32 = 7
    scale: Float64 = 2.5
""",
        module_name="edited",
    )

    linked_cls = linked.classes[0]
    assert linked_cls.origin.source_language == "fortran"
    assert linked_cls.methods == []
    assert [overload.name for overload in linked_cls.overload_sets] == ["__init__"]
    init = linked_cls.overload_sets[0].procedures[0]
    assert init.name == "init_state"
    assert init.metadata["overload_target"] == "init_state"
    assert init.metadata["overload_kind"] == "constructor"
    assert init.metadata["python_method_name"] == "__init__"
    assert init.metadata["python_bound_position"] == 0
    assert [arg.name for arg in init.arguments] == ["self", "seed", "scale"]
    assert [arg.optional for arg in init.arguments] == [False, False, True]

    emitted = emit_module(linked)
    assert "def __init__(\n        self,\n        *,\n        id: Int32 = 7," in emitted
    assert (
        '    @overload("init_state")\n    @native_call([Pass(), Addr(Arg(0)), Addr(Arg(1))])\n    def __init__('
    ) in emitted
    assert parse_pyi_text(emitted, module_name="edited") == linked

    with pytest.raises(ValueError, match="Constructor overload dispatch is not mapped"):
        semantic_ir_to_codegen_ast(
            linked,
            Scope(name=linked.name, scope_type="module"),
        )


def test_convert_pyi_to_ir_removed_constructor_suppresses_keyword_initializer():
    module = parse_pyi_text(
        """
class state:
    id: Int32 = 7
    scale: Float64 = 2.5
""",
        module_name="edited",
    )

    cls = module.classes[0]
    assert cls.origin.source_language is None
    assert cls.origin.metadata[SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA] is True
    assert "def __init__" not in emit_module(module)

    codegen_module = semantic_ir_to_codegen_ast(
        module,
        Scope(name=module.name, scope_type="module"),
    )
    codegen_cls = codegen_module.classes[0]
    assert codegen_cls.decorators[SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA] is True
    assert CPythonBindingGenerator._suppresses_default_class_initialiser(codegen_cls) is True


def test_convert_pyi_to_ir_self_only_generated_constructor_keeps_default_initializer():
    module = parse_pyi_text(
        """
class state:
    def __init__(self) -> None: ...

    values: Annotated[Float64[:], Allocatable]
""",
        module_name="edited",
    )

    cls = module.classes[0]
    assert cls.origin.source_language == "fortran"
    assert SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA not in cls.origin.metadata
    assert cls.methods == []
    assert "    def __init__(self) -> None: ..." in emit_module(module)

    codegen_module = semantic_ir_to_codegen_ast(
        module,
        Scope(name=module.name, scope_type="module"),
    )
    codegen_cls = codegen_module.classes[0]
    assert CPythonBindingGenerator._suppresses_default_class_initialiser(codegen_cls) is False


def test_convert_pyi_to_ir_bound_constructor_replaces_generated_keyword_initializer():
    module = parse_pyi_text(
        """
class state:
    @private
    def init_state(
        self,
        seed: Addr(Int32),
        scale: Addr(Float64) = ...
    ) -> None: ...

    @bind("init_state")
    def __init__(
        self,
        seed: Addr(Int32),
        scale: Addr(Float64) = ...
    ) -> None: ...

    id: Int32 = 7
    scale: Float64 = 2.5
""",
        module_name="edited",
    )

    cls = module.classes[0]
    assert cls.origin.metadata[SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA] is True
    assert [method.name for method in cls.methods] == ["init_state", "__init__"]
    target = cls.methods[0]
    assert target.visibility == "private"
    init = cls.methods[1]
    assert init.native_name == "init_state"
    assert init.metadata[BIND_TARGET_METADATA] == "init_state"
    assert [arg.name for arg in init.arguments] == ["seed", "scale"]

    emitted = emit_module(module)
    assert "    @private\n    def init_state(" in emitted
    assert '    @bind("init_state")\n    def __init__(' in emitted
    assert "def __init__(\n        self,\n        *," not in emitted
    assert parse_pyi_text(emitted, module_name="edited") == module

    codegen_module = semantic_ir_to_codegen_ast(
        module,
        Scope(name=module.name, scope_type="module"),
    )
    codegen_cls = codegen_module.classes[0]
    assert codegen_cls.decorators[SUPPRESS_DEFAULT_CONSTRUCTOR_METADATA] is True
    assert CPythonBindingGenerator._suppresses_default_class_initialiser(codegen_cls) is True
    codegen_init = next(
        method for method in codegen_cls.methods if codegen_cls.scope.get_python_name(method.name) == "__init__"
    )
    assert codegen_cls.scope.get_python_name(codegen_init.name) == "__init__"
    assert codegen_init.arguments[0].bound_argument is True
    assert codegen_init.arguments[0].bound_argument_position == 0
    assert [str(arg.name) for arg in codegen_init.arguments[1:]] == ["seed", "scale"]


def test_convert_pyi_to_ir_bound_constructor_allows_public_target_method():
    module = parse_pyi_text(
        """
class state:
    def init_state(self, seed: Int32) -> None: ...

    @bind("init_state")
    def __init__(self, seed: Int32) -> None: ...
""",
        module_name="edited",
    )

    cls = module.classes[0]
    assert [(method.name, method.visibility) for method in cls.methods] == [
        ("init_state", "public"),
        ("__init__", "public"),
    ]
    emitted = emit_module(module)
    assert "    def init_state(" in emitted
    assert '    @bind("init_state")\n    def __init__(' in emitted


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            """
class state:
    def __init__(self, seed: Int32) -> None: ...
""",
            'Non-generated __init__ declarations must use @bind("specific_name")',
        ),
        (
            """
class state:
    def __init__(self, *, id: Int32 = 7) -> None: ...

    @bind("init_state")
    def __init__(self, seed: Int32) -> None: ...
""",
            "Direct constructor bindings replace the generated field constructor",
        ),
        (
            """
class state:
    @bind("init_state")
    def __init__(self, seed: Int32) -> None: ...
""",
            "Bound constructor references missing class method 'init_state'",
        ),
        (
            """
class state:
    def init_state(self, seed: Int32, scale: Float64) -> None: ...

    @bind("init_state")
    def __init__(self, seed: Int32) -> None: ...
""",
            "Bound constructor declaration is incompatible with class method 'init_state'",
        ),
    ],
)
def test_convert_pyi_to_ir_rejects_ambiguous_constructor_declarations(source: str, message: str):
    with pytest.raises(ValueError, match=re.escape(message)):
        parse_pyi_text(source, module_name="edited")


def test_convert_pyi_to_ir_applies_decorators_after_native_call():
    module = parse_pyi_text(
        """
@native_call([])
@private
def hidden() -> None: ...
""",
        module_name="edited",
    )

    assert module.functions[0].visibility == "private"


def test_convert_pyi_to_ir_resolves_x2py_overload_by_explicit_specific_name():
    module = parse_pyi_text(
        """
def convert_integer(value: Int32) -> Int32: ...

@overload("convert_integer")
def convert(value: Int32) -> Int32: ...
""",
        module_name="generic_mod",
    )

    assert [function.name for function in module.functions] == ["convert_integer"]
    assert [(item.name, [procedure.name for procedure in item.procedures]) for item in module.overload_sets] == [
        ("convert", ["convert_integer"])
    ]
    assert module.overload_sets[0].procedures[0].metadata["overload_target"] == "convert_integer"


def test_convert_pyi_to_ir_renames_module_generic_and_round_trips_native_name():
    module = parse_pyi_text(
        """
@bind("convert")
def convert_integer(value: Int32) -> Int32: ...

@overload("convert_integer", generic="convert")
def convert_number(value: Int32) -> Int32: ...
""",
        module_name="generic_mod",
    )

    overload = module.overload_sets[0]
    assert overload.name == "convert_number"
    assert overload.procedures[0].metadata["fortran_generic_name"] == "convert"
    emitted = emit_module(module)
    assert '@overload("convert_integer", generic="convert")' in emitted


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "@overload\ndef convert(value: Int32) -> Int32: ...\n",
            "overload expects one specific procedure name",
        ),
        (
            "from typing import overload\n",
            "typing.overload is not supported",
        ),
        (
            """
def compare(left: item, right: item) -> Bool: ...
class item:
    @overload("compare", generic="operator(.eqv.)")
    def __add__(self, right: item) -> Bool: ...
""",
            "generic 'operator\\(\\.eqv\\.\\)' is incompatible with method '__add__'",
        ),
        (
            '@overload("missing")\ndef convert(value: Int32) -> Int32: ...\n',
            "missing specific procedure 'missing'",
        ),
        (
            """
def convert_integer(value: Int32) -> Int32: ...
def convert_integer(value: Int32) -> Int32: ...
@overload("convert_integer")
def convert(value: Int32) -> Int32: ...
""",
            "target 'convert_integer' is ambiguous",
        ),
        (
            """
def convert_integer(value: Int32) -> Int32: ...
@overload("convert_integer")
def convert(value: Float64) -> Int32: ...
""",
            "declaration 'convert' is incompatible",
        ),
        (
            """
def convert_integer(value: Int32) -> Int32: ...
@overload("convert_integer")
def convert(value: Int32) -> Int32: ...
@overload("convert_integer")
def convert(value: Int32) -> Int32: ...
""",
            "references specific procedure 'convert_integer' more than once",
        ),
    ],
)
def test_convert_pyi_to_ir_rejects_invalid_x2py_overload_links(source: str, message: str):
    with pytest.raises(ValueError, match=message):
        parse_pyi_text(source, module_name="generic_mod")


def test_pyi_parser_reports_unsupported_lines_and_invalid_helpers():
    with pytest.raises(ValueError, match=r"Unsupported .pyi node"):
        parse_pyi_text("bare_name\n", module_name="edited")

    with pytest.raises(ValueError, match="Unsupported class body node"):
        parse_pyi_text("class C:\n    bare_name\n", module_name="edited")

    with pytest.raises(ValueError, match="Expected typed argument"):
        parse_pyi_text("def f(x) -> None: ...\n", module_name="edited")

    with pytest.raises(ValueError, match="expects positional arguments only"):
        parse_pyi_text("@native_call([Arg(0, name='x')])\ndef f(x: Int32) -> None: ...\n", module_name="edited")

    with pytest.raises(ValueError, match="Expected imported x2py contract helper"):
        parse_pyi_text("@native_call([Unknown(0)])\ndef f(x: Int32) -> None: ...\n", module_name="edited")

    with pytest.raises(ValueError, match="Expected imported x2py contract helper"):
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


def test_convert_pyi_to_ir_round_trips_snapshot_type_wrapper():
    module = parse_pyi_text(
        """
class box:
    value: Float64

current: Snapshot[box]
""",
        module_name="snapshots",
    )

    current = module.variables[0]
    assert current.name == "current"
    assert current.semantic_type.name == "box"
    assert current.semantic_type.metadata[SNAPSHOT_TYPE_METADATA] is True

    emitted = emit_module(module)
    assert "current: Snapshot[box]" in emitted
    assert parse_pyi_text(emitted, module_name="snapshots") == module


def test_convert_pyi_to_ir_accepts_aliased_contract_wrapper_names():
    module = pyi_text_to_semantic_module(
        """
from x2py.contracts import Annotated as Metadata, Float64 as F64, Name as NativeName
from x2py.contracts import Returns as Gives

alias: Metadata[F64[1:n], NativeName("native_alias")]

def f() -> tuple[F64, Gives["y", F64]]: ...
""",
        module_name="edited",
    )

    assert module.variables[0].name == "native_alias"
    assert module.variables[0].semantic_type.shape == ["1:n"]
    assert module.functions[0].return_type is not None
    assert module.functions[0].return_type.name == "Float64"
    assert module.functions[0].arguments[0].name == "y"


def test_convert_pyi_to_ir_accepts_ast_only_projection_value_refs():
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


def test_convert_pyi_to_ir_accepts_plain_return_type():
    pyi = """
def make_value(
    x: Float64
) -> Float64: ...
"""

    module = parse_pyi_text(pyi, module_name="edited")

    func = module.functions[0]
    assert func.return_type is not None
    assert func.return_type.name == "Float64"


def test_native_call_address_argument_projection_records_native_address_storage():
    module = parse_pyi_text(
        """
@native_call([Addr(Arg(0))])
def add_one(value: Int32) -> Int32: ...
""",
        module_name="scalar_refs",
    )

    function = module.functions[0]
    value = function.arguments[0]

    assert value.semantic_type.name == "Int32"
    assert value.semantic_type.storage is None
    assert function.projection[0].value_kind == "addr"
    assert function.projection[0].value == {"kind": "arg", "position": 0}

    complete_semantic_policies(module)

    assert value.semantic_type.storage.kind == "address"
    assert value.semantic_type.storage.read_only is False
    assert value.semantic_type.storage.mutable is True
    assert value.semantic_type.storage.metadata[ADDRESS_ROLE_METADATA] == ADDRESS_ROLE_PROJECTION
    assert (
        emit_module(module)
        .strip()
        .endswith("@native_call([Addr(Arg(0))])\ndef add_one(\n    value: Int32\n) -> Int32: ...")
    )


def test_rank_zero_scalar_storage_round_trips_as_empty_tuple_array():
    module = parse_pyi_text(
        """
def update_storage(value: Float64[()]) -> None: ...
def inspect_storage(value: Int32[()]) -> None: ...
""",
        module_name="scalar_storage",
    )

    update, inspect = module.functions
    update_type = update.arguments[0].semantic_type
    inspect_type = inspect.arguments[0].semantic_type

    assert update_type.rank == 0
    assert update_type.storage.kind == "array"
    assert update_type.storage.array.category == "scalar_storage"
    assert inspect_type.storage.read_only is False
    assert inspect_type.storage.mutable is True

    emitted = emit_module(module)
    assert "value: Float64[()]" in emitted
    assert "value: Int32[()]" in emitted
    assert parse_pyi_text(emitted, module_name="scalar_storage") == module


def test_rank_zero_string_storage_round_trips_as_empty_tuple_array():
    module = parse_pyi_text(
        """
def rewrite_label(label: String[8][()]) -> None: ...
""",
        module_name="string_storage",
    )

    label_type = module.functions[0].arguments[0].semantic_type

    assert label_type.name == "String"
    assert label_type.rank == 0
    assert label_type.shape == []
    assert label_type.metadata["fortran_character_length"] == "8"
    assert label_type.storage.kind == "array"
    assert label_type.storage.array.category == "scalar_storage"

    emitted = emit_module(module)
    assert "label: String[8][()]" in emitted
    assert parse_pyi_text(emitted, module_name="string_storage") == module


def test_string_length_and_shape_axes_round_trip():
    module = parse_pyi_text(
        """
def scalar_unknown(value: String) -> None: ...
def scalar_fixed(value: String[8]) -> None: ...
def array_unknown(values: String[:][:]) -> None: ...
def array_fixed(values: String[8][:]) -> None: ...
def scalar_storage(value: String[8][()]) -> None: ...
""",
        module_name="string_axes",
    )

    scalar_unknown, scalar_fixed, array_unknown, array_fixed, scalar_storage = module.functions

    assert "fortran_character_length" not in scalar_unknown.arguments[0].semantic_type.metadata
    assert scalar_fixed.arguments[0].semantic_type.metadata["fortran_character_length"] == "8"

    array_unknown_type = array_unknown.arguments[0].semantic_type
    assert array_unknown_type.metadata["fortran_character_length"] == ":"
    assert array_unknown_type.rank == 1
    assert array_unknown_type.shape == [":"]
    assert array_unknown_type.storage.kind == "array"

    array_fixed_type = array_fixed.arguments[0].semantic_type
    assert array_fixed_type.metadata["fortran_character_length"] == "8"
    assert array_fixed_type.rank == 1
    assert array_fixed_type.shape == [":"]

    scalar_storage_type = scalar_storage.arguments[0].semantic_type
    assert scalar_storage_type.metadata["fortran_character_length"] == "8"
    assert scalar_storage_type.storage.array.category == "scalar_storage"

    emitted = emit_module(module)
    assert "value: String" in emitted
    assert "value: String[8]" in emitted
    assert "values: String[:][:]" in emitted
    assert "values: String[8][:]" in emitted
    assert "value: String[8][()]" in emitted
    assert parse_pyi_text(emitted, module_name="string_axes") == module


def test_bare_string_slice_is_rejected_as_ambiguous():
    with pytest.raises(ValueError, match=r"String\[:\] is ambiguous.*String\[:\]\[:\].*String\[n\]"):
        parse_pyi_text(
            """
def invalid(value: String[:]) -> None: ...
""",
            module_name="string_axes",
        )


def test_public_raw_address_contract_round_trips():
    module = parse_pyi_text(
        """
def update_raw(value: Addr(Float64)) -> None: ...
def inspect_raw(value: Addr(Float64)) -> None: ...
def raw_values(n: Int32, values: Addr(Float64[n])) -> None: ...
def raw_label(label: Addr(String[8])) -> None: ...
""",
        module_name="raw_address",
    )

    update, inspect, raw_values, raw_label = module.functions
    update_storage = update.arguments[0].semantic_type.storage
    inspect_storage = inspect.arguments[0].semantic_type.storage
    values_type = raw_values.arguments[1].semantic_type
    label_type = raw_label.arguments[0].semantic_type

    assert update_storage.kind == "address"
    assert update_storage.metadata[ADDRESS_ROLE_METADATA] == ADDRESS_ROLE_RAW
    assert inspect_storage.read_only is False
    assert inspect_storage.mutable is True
    assert values_type.rank == 1
    assert values_type.shape == ["n"]
    assert values_type.storage.kind == "address"
    assert values_type.storage.metadata[ADDRESS_ROLE_METADATA] == ADDRESS_ROLE_RAW
    assert label_type.name == "String"
    assert label_type.metadata["fortran_character_length"] == "8"
    assert label_type.storage.kind == "address"
    assert label_type.storage.metadata[ADDRESS_ROLE_METADATA] == ADDRESS_ROLE_RAW

    emitted = emit_module(module)
    assert "value: Addr(Float64)" in emitted
    assert "value: Addr(Float64)" in emitted
    assert "values: Addr(Float64[n])" in emitted
    assert "label: Addr(String[8])" in emitted
    assert parse_pyi_text(emitted, module_name="raw_address") == module


def test_wrapped_type_raw_address_is_rejected_during_policy_completion():
    module = parse_pyi_text(
        """
class particle:
    value: Float64

def move(value: Addr(particle)) -> None: ...
""",
        module_name="wrapped_address",
    )

    storage = module.functions[0].arguments[0].semantic_type.storage
    assert storage.kind == "address"
    assert storage.metadata[ADDRESS_ROLE_METADATA] == ADDRESS_ROLE_RAW
    assert (
        emit_module(module)
        .strip()
        .endswith("class particle:\n    value: Float64\n\ndef move(\n    value: Addr(particle)\n) -> None: ...")
    )
    with pytest.raises(ValueError, match=r"Addr\(WrappedType\) is not allowed"):
        complete_semantic_policies(module)


def test_raw_address_policy_accepts_only_complete_primitive_layouts():
    module = parse_pyi_text(
        """
def raw_access(
    n: Int32,
    scalar: Addr(Float64),
    label: Addr(String[8]),
    values: Addr(Float64[n])
) -> Addr(Int32): ...

def raw_access_with_storage_extent(
    n: Int32[()],
    values: Addr(Float64[n])
) -> None: ...
""",
        module_name="raw_addresses",
    )

    complete_semantic_policies(module)

    assert module.metadata["policy_completion_prepared"] is True


@pytest.mark.parametrize(
    ("annotation", "message"),
    [
        ("Addr(particle)", r"Addr\(WrappedType\) is not allowed"),
        ("Addr(String)", "raw strings require a fixed length"),
        ("Addr(Float64[:])", "raw arrays require a fully resolved rank and shape"),
        ("Addr(Float64[missing])", "raw arrays require a fully resolved rank and shape"),
        ("Addr[2](Float64)", r"callable Addr\(T\) supports depth one only"),
    ],
)
def test_raw_address_policy_rejects_incomplete_or_wrapped_pointees(annotation: str, message: str):
    module = parse_pyi_text(
        f"""
class particle:
    value: Float64

def invalid(n: Int32, value: {annotation}) -> None: ...
""",
        module_name="invalid_raw_address",
    )

    with pytest.raises(ValueError, match=message):
        complete_semantic_policies(module)


@pytest.mark.parametrize(
    ("annotation", "message"),
    [
        ("Callable[[In(Addr(Int32))], None]", r"Addr\(\.\.\.\) is not valid inside Callable"),
        ("Callable[[Out(Addr(Float64))], None]", r"Addr\(\.\.\.\) is not valid inside Callable"),
        ("Callable[[InOut(Addr(Float64))], None]", r"Addr\(\.\.\.\) is not valid inside Callable"),
        ("Callable[[Addr(Float64)], None]", r"Addr\(\.\.\.\) is not valid inside Callable"),
        ("Callable[[Addr(Float64[n])], None]", r"Addr\(\.\.\.\) is not valid inside Callable"),
        ("Callable[[Addr[2](Float64)], None]", r"Addr\(\.\.\.\) is not valid inside Callable"),
    ],
)
def test_convert_pyi_to_ir_rejects_invalid_callback_reference_wrappers(annotation: str, message: str):
    with pytest.raises(ValueError, match=message):
        parse_pyi_text(f"def register(callback: {annotation}) -> None: ...", module_name="callbacks")


def test_identity_returns_reconstruct_native_projection_without_decorator():
    source = """
def fill(values: Float64[3]) -> Returns["values", Float64[3]]: ...
"""
    module = parse_pyi_text(source, module_name="identity_returns")
    function = module.functions[0]

    assert len(function.projection) == 1
    assert function.projection[0].native_position == 0
    assert function.projection[0].python_position == 0
    assert function.projection[0].result_position == 0
    assert (
        emit_module(module)
        .strip()
        .endswith('def fill(\n    values: Float64[3]\n) -> Returns["values", Float64[3]]: ...')
    )


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


def test_convert_pyi_to_ir_preserves_explicit_array_source_dimensions():
    module = parse_pyi_text(
        """
def apply(
    A: Annotated[Float64[LDA, N], ORDER_F],
    work: Float64[::],
    scratch: Float64[:]
) -> None: ...
""",
        module_name="explicit_dims",
    )

    args = {arg.name: arg.semantic_type.storage.array for arg in module.functions[0].arguments}
    assert args["A"].source_shape == ["LDA", "N"]
    assert args["A"].lower_bounds == [None, None]
    assert args["A"].upper_bounds == [None, None]
    assert args["work"].shape == ["::Strided"]
    assert args["work"].axes == ["strided"]
    assert args["work"].contiguous is False
    assert args["work"].source_shape == []
    assert args["scratch"].shape == [":"]
    assert args["scratch"].axes == ["dense"]
    assert args["scratch"].contiguous is True
    assert args["scratch"].source_shape == []


def test_convert_pyi_to_ir_accepts_explicit_strided_marker_for_edited_contracts():
    module = parse_pyi_text(
        """
current: Float64[::]
explicit: Float64[::Strided]
bounded: Float64[0:n:]
explicit_bounded: Float64[0:n:Strided]
""",
        module_name="strided_axes",
    )

    arrays = [variable.semantic_type.storage.array for variable in module.variables]
    assert [array.shape for array in arrays] == [["::Strided"], ["::Strided"], ["0:n:Strided"], ["0:n:Strided"]]
    assert [array.axes for array in arrays] == [["strided"], ["strided"], ["strided"], ["strided"]]
    assert [array.contiguous for array in arrays] == [False, False, False, False]


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
                    ),
                ],
                projection=[
                    ProjectionMapping(
                        native_name="c",
                        native_position=2,
                        result_position=0,
                    )
                ],
            )
        ],
    )

    assert from_pyi != from_ir
    assert from_pyi.functions[0].projection[2].native_position == 2


def test_native_call_return_entry_can_preserve_output_name():
    from_pyi = parse_pyi_text(
        """
@native_call([Arg(0), Arg(1), Return("c", 0)])
def add(
    a: Float64,
    b: Float64
) -> Float64: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]

    assert [arg.name for arg in func.arguments] == ["a", "b", "c"]
    assert func.projection[2].native_name == "c"
    assert func.projection[2].python_name == "c"
    assert func.projection[2].result_position == 0


def test_projected_replacement_without_native_call_keeps_writable_argument_storage():
    from_pyi = parse_pyi_text(
        """
def fixed_inout(
    name: String[8]
) -> Returns["name", String[8]]: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]

    assert func.arguments[0].metadata[PROJECTED_OUTPUT_METADATA] is True
    assert len(func.projection) == 1
    assert func.projection[0].native_position == 0
    assert func.projection[0].python_position == 0
    assert func.projection[0].result_position == 0


@pytest.mark.parametrize(
    "annotation",
    [
        "String[8]",
        "Float64[()]",
        "Float64[:]",
        "particle",
        "Addr(Float64)",
    ],
)
def test_native_call_addr_arg_rejects_non_primitive_scalar_values(annotation: str):
    module = parse_pyi_text(
        f"""
class particle:
    value: Float64

@native_call([Addr(Arg(0))])
def invalid(value: {annotation}) -> None: ...
""",
        module_name="edited",
    )

    with pytest.raises(ValueError, match="only valid for primitive scalar values"):
        complete_semantic_policies(module)


@pytest.mark.parametrize(
    ("projection", "return_type"),
    [
        ("Addr(Return(0))", "Float64"),
        ('Addr(Work("scratch"))', "None"),
    ],
)
def test_native_call_address_projection_rejects_non_argument_storage(projection: str, return_type: str):
    module = parse_pyi_text(
        f"""
@native_call([{projection}])
def invalid() -> {return_type}: ...
""",
        module_name="edited",
    )

    with pytest.raises(ValueError, match=r"only Addr\(Arg\(i\)\) is supported"):
        complete_semantic_policies(module)


def test_native_call_projected_output_keeps_visible_storage_writable():
    from_pyi = parse_pyi_text(
        """
@native_call([Arg(0), Arg(1)])
def fill(
    n: Addr(Int32),
    values: Float64[n]
) -> Returns["values", Float64[n]]: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]

    assert func.projection[1].result_position == 0


def test_native_call_compact_array_output_marks_projection_without_direction_label():
    from_pyi = parse_pyi_text(
        """
@native_call([Arg(0), Arg(1)])
def fill(
    n: Addr(Int32),
    values: Float64[n]
) -> Returns["values", Float64[n]]: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]

    assert func.arguments[1].metadata[PROJECTED_OUTPUT_METADATA] is True
    assert func.projection[1].result_position == 0

    codegen_module = semantic_ir_to_codegen_ast(
        from_pyi,
        Scope(name=from_pyi.name, scope_type="module"),
    )
    assert codegen_module.funcs[0].arguments[1].var.projected_output is True


def test_native_order_outputs_do_not_get_projected_without_native_call():
    from_pyi = parse_pyi_text(
        """
def solve(
    x: Addr(Float64),
    status: Addr(Int32)
) -> tuple[Float64, Returns["message", String]]: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]

    assert [arg.name for arg in func.arguments] == ["x", "status", "message"]
    assert PROJECTED_OUTPUT_METADATA not in func.arguments[1].metadata
    assert func.arguments[2].metadata[PROJECTED_OUTPUT_METADATA] is True


def test_compact_assignment_overload_projects_visible_destination_without_direction_label():
    from_pyi = parse_pyi_text(
        """
class vector:
    value: Float64

    @overload("assign_vector_real")
    def assign(
        self,
        right: Float64
    ) -> vector: ...

@private
@native_call([Arg(0), Addr(Arg(1))])
def assign_vector_real(
    left: vector,
    right: Float64
) -> Returns["left", vector]: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]

    assert func.arguments[0].metadata[PROJECTED_OUTPUT_METADATA] is True
    assert func.projection[0].result_position == 0
    assert from_pyi.classes[0].overload_sets[0].procedures[0].metadata["overload_kind"] == "assignment"

    codegen_module = semantic_ir_to_codegen_ast(
        from_pyi,
        Scope(name=from_pyi.name, scope_type="module"),
    )
    assign = next(item for item in codegen_module.classes[0].overload_sets if item.name == "assign")
    assert assign.functions[0].arguments[0].var.projected_output is True


def test_type_bound_method_declarations_restore_root_target_metadata():
    from_pyi = parse_pyi_text(
        """
class vector:
    def scale(
        self,
        factor: Addr(Float64)
    ) -> None: ...

    @bind("shift_vector")
    @native_call([Arg(0), Pass(), Arg(1)])
    def shift(
        self,
        dx: Addr(Float64),
        dy: Addr(Float64)
    ) -> None: ...

def scale(
    self: Annotated[vector, Polymorphic],
    factor: Addr(Float64)
) -> None: ...

def shift_vector(
    dx: Addr(Float64),
    owner: Annotated[vector, Polymorphic],
    dy: Addr(Float64)
) -> None: ...
""",
        module_name="edited",
    )
    functions = {func.name: func for func in from_pyi.functions}

    assert functions["scale"].metadata["fortran_type_bound_target"] is True
    assert functions["scale"].metadata["fortran_passed_object_name"] == "self"
    assert functions["scale"].metadata["fortran_passed_object_position"] == 0
    assert functions["shift_vector"].metadata["fortran_type_bound_target"] is True
    assert functions["shift_vector"].metadata["fortran_passed_object_name"] == "owner"
    assert functions["shift_vector"].metadata["fortran_passed_object_position"] == 1


def test_pyi_codegen_imports_public_generic_not_private_specific_targets():
    module = parse_pyi_text(
        """
@private
def convert_integer(
    value: Addr(Int32)
) -> Int32: ...

@overload("convert_integer")
def convert(
    value: Addr(Int32)
) -> Int32: ...
""",
        module_name="foverloads_f90",
    )

    codegen_module = semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    imported = {
        (str(target.name), str(target.local_alias))
        for native_import in codegen_module.imports
        for target in native_import.target
    }

    assert ("convert", "convert") in imported
    assert all("convert_integer" not in item for names in imported for item in names)


def test_pyi_codegen_keyword_normalized_type_bound_method_uses_native_binding_name():
    module = parse_pyi_text(
        """
class visible_t:
    @bind("visible_from")
    def from_(self) -> Int32: ...
""",
        module_name="fnaming_f90",
    )

    codegen_module = semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    method = codegen_module.classes[0].methods_as_dict["from_"]

    assert method.name == "visible_from"
    assert method.type_bound_name == "from"


def test_native_call_return_entry_preserves_optional_pointer_return():
    from_pyi = parse_pyi_text(
        """
@native_call([Arg(0), Return("status", 0)])
def maybe_status(
    base: Addr(Int32)
) -> Addr(Int32) | None: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]
    returned = func.arguments[1]

    assert returned.name == "status"
    assert returned.optional is True
    assert returned.semantic_type.name == "Int32"
    assert returned.semantic_type.storage is not None
    assert returned.semantic_type.storage.kind == "address"
    assert func.projection[1].python_name == "status"


def test_native_call_later_return_entry_preserves_native_position_and_name():
    from_pyi = parse_pyi_text(
        """
@native_call([Arg(0), Return("status", 1), Arg(1)])
def fill(
    values: Float64[n],
    n: Addr(Int32)
) -> tuple[Returns["values", Float64[n]], Addr(Int32)]: ...
""",
        module_name="edited",
    )
    func = from_pyi.functions[0]

    assert [arg.name for arg in func.arguments] == ["values", "status", "n"]
    assert func.projection[1].python_name == "status"
    assert func.projection[1].native_name == "status"
    assert func.projection[1].result_position == 1


def test_native_call_accepts_hidden_native_values():
    module = parse_pyi_text(
        """
@native_call([
    Arg(0),
    Int32(1),
    Float64(0.5),
    Bool(False),
    String[1]("N"),
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
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 1,
            "python_position": None,
            "result_position": None,
            "value_kind": "literal",
            "value": {"type": "Int32", "value": 1},
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 2,
            "python_position": None,
            "result_position": None,
            "value_kind": "literal",
            "value": {"type": "Float64", "value": 0.5},
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 3,
            "python_position": None,
            "result_position": None,
            "value_kind": "literal",
            "value": {"type": "Bool", "value": False},
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 4,
            "python_position": None,
            "result_position": None,
            "value_kind": "literal",
            "value": {"type": "String[1]", "value": "N"},
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 5,
            "python_position": None,
            "result_position": None,
            "value_kind": "len",
            "value": {"kind": "arg", "position": 0},
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 6,
            "python_position": None,
            "result_position": None,
            "value_kind": "shape",
            "value": {"value": {"kind": "arg", "position": 0}, "dim": 0},
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 7,
            "python_position": None,
            "result_position": None,
            "value_kind": "is_present",
            "value": {"kind": "arg", "position": 1},
        },
        {
            "python_name": None,
            "native_name": "",
            "native_position": 8,
            "python_position": None,
            "result_position": None,
            "value_kind": "work",
            "value": "tmp",
        },
    ]
    assert projection[1].value_kind == "literal"
    assert projection[1].value == {"type": "Int32", "value": 1}
    assert projection[4].value == {"type": "String[1]", "value": "N"}
    assert projection[5].value_kind == "len"
    assert projection[5].value == {"kind": "arg", "position": 0}
    assert projection[6].value_kind == "shape"
    assert projection[6].value == {"value": {"kind": "arg", "position": 0}, "dim": 0}
    assert projection[7].value_kind == "is_present"
    assert projection[7].value == {"kind": "arg", "position": 1}
    assert projection[8].value_kind == "work"
    assert projection[8].value == "tmp"
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
                    ProjectionMapping(
                        native_position=1,
                        value_kind="literal",
                        value={"type": "Int32", "value": 1},
                    ),
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

    assert "@native_call([Arg(0), Int32(1), Len(Arg(0)), Arg(0).shape[0], IsPresent(Arg(1)), Work('tmp')])" in pyi


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
                    ),
                ],
                projection=[
                    ProjectionMapping(
                        native_name="c",
                        native_position=2,
                        result_position=0,
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


def test_return_projection_preserves_multiple_plain_output_components():
    parser = _PyiAstParser(module_name="internal")
    parser._contract_bindings.update({name: name for name in CONTRACT_SYMBOLS})

    return_type, returned = parser.return_projection(ast.parse("tuple[Float64, Int32, Logical]", mode="eval").body)

    assert return_type.name == "Float64"
    assert [asdict(arg) for arg in returned] == [
        asdict(
            SemanticArgument(
                "__return_1",
                SemanticType("Int32", dtype="Int32"),
                metadata={"return_position": 1},
            )
        ),
        asdict(
            SemanticArgument(
                "__return_2",
                SemanticType("Logical", dtype="Logical"),
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
        ("def f(\n    x: Int32,\n): ...\n", "Unterminated callable starting at line 2"),
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
        (
            "@native_call([1])\ndef f(x: Int32) -> None: ...\n",
            'native_call hidden literals require typed calls such as Int32(1) or String[1]("N")',
        ),
        ("@native_call([Arg(1)])\ndef f(x: Int32) -> None: ...\n", "native_call argument position is out of range: 1"),
        ("@native_call([Arg()])\ndef f(x: Int32) -> None: ...\n", "Arg expects one positional index"),
        (
            "@native_call([Return()])\ndef f(x: Int32) -> None: ...\n",
            "Return expects one positional index or a name and index",
        ),
        (
            '@native_call([String("N")])\ndef f(x: Int32) -> None: ...\n',
            'native_call string literals require String[length](value), for example String[1]("N")',
        ),
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
            "Expected imported x2py contract helper: 'Unknown'",
        ),
        ("def f(x: Int32) -> Returns['x']: ...\n", "Returns expects a name and type: \"Returns['x']\""),
        ("value: Final[Int32, Float64]\n", "Final expects exactly one type: 'Final[Int32, Float64]'"),
        ("value: Unknown\n", "Unknown semantic type is not allowed in .pyi annotations"),
        ("value: Annotated[()]\n", "Annotated type is empty: 'Annotated[()]'"),
    ],
)
def test_convert_pyi_to_ir_rejects_invalid_projection_and_type_forms(source: str, message: str):
    with pytest.raises(ValueError) as error:
        parse_pyi_text(source, module_name="edited")
    assert str(error.value) == message


def test_convert_pyi_to_ir_accepts_multiline_native_call_decorator():
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

    assert "@native_call([Addr(Arg(0)), Return('x', 0), Addr(Arg(1))])" in pyi
    func = reparsed.functions[0]
    assert func.name == "solve"
    assert [arg.name for arg in func.arguments] == ["a", "x", "b"]


def test_convert_pyi_to_ir_accepts_c_and_fortran_order_constraints():
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


def test_convert_pyi_to_ir_accepts_flat_array_dimension():
    module = parse_pyi_text(
        """
flat: Float64[Flat]
matrix: Float64[3, Flat]
tensor: Float64[3, 4, Flat]
c_matrix: Annotated[Float64[Flat, 3], ORDER_C]
c_tensor: Annotated[Float64[Flat, 3, 4], ORDER_C]
""",
        module_name="flat_arrays",
    )

    arrays = [variable.semantic_type.storage.array for variable in module.variables]
    assert [variable.semantic_type.shape for variable in module.variables] == [
        [":"],
        ["3", ":"],
        ["3", "4", ":"],
        [":", "3"],
        [":", "3", "4"],
    ]
    assert [array.category for array in arrays] == [
        "assumed_size",
        "assumed_size",
        "assumed_size",
        "assumed_size",
        "assumed_size",
    ]
    assert [array.source_shape for array in arrays] == [
        ["*"],
        ["3", "*"],
        ["3", "4", "*"],
        ["*", "3"],
        ["*", "3", "4"],
    ]
    assert [array.upper_bounds for array in arrays] == [
        ["*"],
        [None, "*"],
        [None, None, "*"],
        ["*", None],
        ["*", None, None],
    ]
    assert [array.order for array in arrays] == [None, "ORDER_F", "ORDER_F", "ORDER_C", "ORDER_C"]


def test_convert_pyi_to_ir_preserves_extended_array_metadata_and_nested_selector():
    module = parse_pyi_text(
        """
value: Annotated[Float64, ORDER_F, Allocatable, Pointer, Contiguous, ArrayCategory("deferred_shape"), SourceDims("1:n", "*", "extent"), LowerBounds(None, "0"), UpperBounds("n", None)]
nested: Float64[:, :][rank, kind]
name: Annotated[String[16], FortranAllocatable]

def fill(x: Float64[:]) -> None: ...
""",
        module_name="metadata",
    )

    value_type = module.variables[0].semantic_type
    value = value_type.storage.array
    nested = module.variables[1].semantic_type
    name = module.variables[2].semantic_type
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


def test_convert_pyi_to_ir_handles_callable_and_pointer_storage_variants():
    module = parse_pyi_text(
        """
plain_callback: Callable
second_callback: Callable
opaque_callback: Callable[..., Float64]
constant: Int32
deep: Addr[3](Float64)
rank_any: Float64[...]
strided: Float64[0:n:]
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
    assert constant.storage is None
    assert deep.storage.kind == "pointer"
    assert deep.storage.pointer_depth == 3
    assert deep.storage.read_only is False
    assert deep.storage.mutable is True
    assert rank_any.storage.array.rank == 1
    assert rank_any.storage.array.category == "assumed_rank"
    assert rank_any.storage.array.source_shape == [".."]
    assert rank_any.rank == 1
    assert strided.shape == ["0:n:Strided"]
    assert strided.storage.array.contiguous is False
    assert computed.shape == ["size(xl)"]
    assert bounded.constraints == [
        SemanticConstraint("Bounded", [1, 8]),
        SemanticConstraint("Constant"),
    ]
    assert nested.constraints == [SemanticConstraint("Constant")]


def test_convert_pyi_to_ir_preserves_module_fields_and_private_callable_arguments():
    module = parse_pyi_text(
        """
output: Float64[:] = ...

def consume(value: private[Int32]) -> None: ...
""",
        module_name="fields",
    )

    assert module.variables[0].optional is True
    assert module.functions[0].arguments[0].visibility == "private"


def test_convert_pyi_to_ir_preserves_user_private_bound_function_contract():
    module = parse_pyi_text(
        """
@private
@bind("native_helper")
def helper(value: Int32) -> None: ...
""",
        module_name="edited",
    )

    helper = module.functions[0]
    assert native_contract_issues(module) == []
    assert helper.visibility == "private"
    assert helper.origin.source_language == "fortran"
    assert helper.origin.metadata[USER_PRIVATE_METADATA] is True

    emitted = emit_module(module)
    assert '@private\n@bind("native_helper")\ndef helper(' in emitted
    assert "    value: Int32" in emitted
    assert parse_pyi_text(emitted, module_name="edited") == module


@pytest.mark.parametrize(
    "source, message",
    [
        ("value: Addr(Int32, Float64)\n", "Addr type expects one argument: 'Addr(Int32, Float64)'"),
        ("value: Addr[1](Int32)\n", "Addr[1](...) is invalid; use Addr(...)"),
        ("value: Callable[Int32]\n", "Callable expects argument types and a return type: 'Callable[Int32]'"),
        ("value: Callable[Int32, Float64]\n", "Callable arguments must be a list: 'Callable[Int32, Float64]'"),
        (
            "value: Float64[ORDER_F]\n",
            "Non-dimensional type subscriptions are not supported; use Final[...] for constants and "
            "Annotated[...] for constraints or array metadata",
        ),
        (
            "value: Float64[3, Flat, 4]\n",
            "Flat must appear exactly once at the first or final concrete array dimension",
        ),
        (
            "value: Float64[3, Flat, Flat]\n",
            "Flat must appear exactly once at the first or final concrete array dimension",
        ),
        (
            "value: Annotated[Float64[Flat, 3], ORDER_F]\n",
            "ORDER_F conflicts with ORDER_C implied by Flat placement",
        ),
        (
            "value: Annotated[Float64[3, Flat], ORDER_C]\n",
            "ORDER_C conflicts with ORDER_F implied by Flat placement",
        ),
        (
            "value: Annotated[Int32, Bounded(lower=1)]\n",
            "Constraint metadata expects positional arguments only: 'Bounded(lower=1)'",
        ),
        ("value: Annotated[Int32, 'bad']\n", "Unsupported Annotated metadata: \"'bad'\""),
        ("value: Float64[:, foo.bar]\n", "Unsupported array dimension expression: 'foo.bar'"),
        (
            "@native_call([Arg(0).other[0]])\ndef f(x: Int32) -> None: ...\n",
            "native_call expects projection entry calls",
        ),
    ],
)
def test_convert_pyi_to_ir_rejects_additional_invalid_storage_forms(source: str, message: str):
    with pytest.raises(ValueError) as error:
        parse_pyi_text(source, module_name="invalid")
    assert str(error.value) == message


def test_pyi_parser_internal_projection_helpers_preserve_native_names():
    parser = _PyiAstParser(module_name="internal")
    parser._contract_bindings.update({name: name for name in CONTRACT_SYMBOLS})
    return_type, returned_values = parser.return_projection(
        ast.parse("tuple[Float64, Returns['extra', Int32, Optional], Returns['other', Float64]]", mode="eval").body
    )
    pointer = parser.semantic_type(ast.parse("Addr(Float64)", mode="eval").body)
    returned = SemanticArgument("result", SemanticType("Float64"), metadata={"return_position": 1})
    mapping = ProjectionMapping(native_name="native_result", result_position=1)
    _, values = parser._apply_native_call_returns(None, [returned], [mapping])
    native_arg = SemanticArgument("python_name", SemanticType("Int32"))
    arg_mapping = ProjectionMapping(native_name="native_name", python_position=0)
    parser._apply_native_call_argument_names([native_arg], {}, [arg_mapping])

    assert return_type.name == "Float64"
    assert returned_values[0].name == "extra"
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


def test_generated_pyi_loads_and_reemits_for_all_fortran_fixtures(tmp_path: Path):
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
            generated_pyi = emit_module(module)
            pyi_path.write_text(generated_pyi + "\n", encoding="utf-8")

            try:
                loaded = pyi_file_to_semantic_module(pyi_path)
                assert parse_pyi_text(emit_module(loaded), module_name=loaded.name) == loaded
                issues = native_contract_issues(loaded)
                assert issues == []
            finally:
                pyi_path.unlink(missing_ok=True)

            checked_modules += 1

    assert checked_modules > 0
    assert skipped_unresolved_types > 0
    assert not list(tmp_path.glob("*.pyi"))


def test_generated_native_scope_comes_from_contract_filename():
    parsed = parse_fortran_file(
        """
module solver_mod
contains
  subroutine solve(value)
    real(8), intent(in) :: value
  end subroutine solve
end module solver_mod
"""
    )
    module = fortran_file_to_semantic_modules(parsed)[0]
    loaded = parse_pyi_text(emit_module(module), module_name="renamed_contract")

    assert loaded.name == "renamed_contract"
    assert native_contract_issues(loaded) == []
    assert loaded.origin.native_name == "renamed_contract"
    assert loaded.functions[0].origin.native_scope == "renamed_contract"


def test_generated_standalone_contract_retains_external_native_placement():
    parsed = parse_fortran_file(
        """
subroutine solve(value)
  real(8), intent(in) :: value
end subroutine solve
"""
    )
    module = fortran_file_to_semantic_modules(parsed, standalone_module_name="root_contract")[0]
    generated = emit_module(module)
    loaded = parse_pyi_text(generated, module_name="renamed_root_contract")

    assert "@external" in generated
    assert loaded.functions[0].origin.native_scope is None
    assert native_contract_issues(loaded) == []
    assert loaded.origin.native_name == "renamed_root_contract"
    assert loaded.functions[0].origin.native_scope is None


def test_native_contract_structurally_accepts_declared_type_and_constraint_edits():
    parsed = parse_fortran_file(
        """
module solver_mod
contains
  function solve(value) result(result)
    real(8), intent(in) :: value
    real(8) :: result
  end function solve
end module solver_mod
"""
    )
    generated = emit_module(fortran_file_to_semantic_modules(parsed)[0])
    constrained = generated.replace(
        "from x2py.contracts import ",
        "from x2py.contracts import Annotated, Finite, ",
        1,
    ).replace("value: Float64", "value: Annotated[Float64, Finite]", 1)
    changed_abi = generated.replace(
        "from x2py.contracts import ",
        "from x2py.contracts import Int32, ",
        1,
    ).replace("value: Float64", "value: Int32", 1)

    assert native_contract_issues(parse_pyi_text(constrained, module_name="solver_mod")) == []
    assert native_contract_issues(parse_pyi_text(changed_abi, module_name="solver_mod")) == []


def test_readiness_uses_source_free_contract_filename_as_native_scope():
    module = parse_pyi_text("def solve(value: Float64) -> Float64: ...\n", module_name="missing")
    report = assess_semantic_wrap_readiness(module, require_native_contract=True)

    assert report["wrappable"] is True
    assert module.origin.native_name == "missing"
