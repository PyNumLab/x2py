"""Tests split by stable ownership concept from `test_wrap_readiness.py`."""

from tests._shared.semantic_readiness_support import (
    CONTRACT_IMPORT,
    Path,
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticModule,
    SemanticStorageContract,
    SemanticType,
    _blocker_codes,
    _readiness_from_pyi,
    assess_pyi_wrap_readiness,
    assess_semantic_wrap_readiness,
    x2py_cli,
)


def test_completed_pyi_interface_is_semantically_ready():
    report = _readiness_from_pyi(
        """
from x2py.contracts import Final, Float64, Int32, Returns, prototype

rk: Final[Int32] = 8
nmax: Final[Int32] = 32

class sim_state:
    n: Int32
    values: Float64[n]

@prototype
def score_callback(state: sim_state, t: Float64) -> Float64: ...

def step(
    state: sim_state,
    t: Float64,
    objective: score_callback,
    scratch: Float64[nmax]
) -> tuple[Returns["state", sim_state], Returns["score", Float64]]: ...
"""
    )

    assert report["wrappable"] is True
    assert report["wrappability_blockers"] == []


def test_imported_type_can_complete_semantic_readiness():
    report = _readiness_from_pyi(
        """
from state_mod import sim_state

def step(state: sim_state) -> Returns["state", sim_state]: ...
"""
    )

    assert report["wrappable"] is True


def test_callback_placeholder_blocks_until_named_prototype_is_supplied():
    report = _readiness_from_pyi(
        """
def integrate(objective: Procedure, x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is False
    assert "callback_signature_incomplete" in _blocker_codes(report)
    blocker = report["wrappability_blockers"][0]["items"][0]
    assert blocker["needs"] == [
        "callback argument order",
        "callback argument types",
        "callback return type",
    ]


def test_named_prototype_makes_callback_ready():
    report = _readiness_from_pyi(
        """
from x2py.contracts import Float64, prototype

@prototype
def objective(value: Float64) -> Float64: ...

def integrate(callback: objective, x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is True


def test_assess_pyi_wrap_readiness_expands_directory_and_uses_leaf_filenames(tmp_path: Path):
    nested = tmp_path / "nested"
    nested.mkdir()
    first = tmp_path / "first.pyi"
    second = nested / "second.pyi"
    ignored = nested / "ignored.txt"
    first.write_text(f"{CONTRACT_IMPORT}def first(x: Int32) -> None: ...\n", encoding="utf-8")
    second.write_text(f"{CONTRACT_IMPORT}def second(x: Int32) -> None: ...\n", encoding="utf-8")
    ignored.write_text("not a stub", encoding="utf-8")

    report = assess_pyi_wrap_readiness([tmp_path, first])

    assert report["wrappable"] is True
    assert report["n_modules"] == 2
    assert report["source"] == [str(first), str(second)]
    assert _blocker_codes(report) == set()


def test_assess_pyi_wrap_readiness_honors_explicit_encoding(tmp_path: Path):
    pyi = tmp_path / "latin1.pyi"
    pyi.write_bytes(f'{CONTRACT_IMPORT}label: Final[String] = "caf\xe9"\n'.encode("latin-1"))

    report = assess_pyi_wrap_readiness(pyi, encoding="latin-1")

    assert report["wrappable"] is True
    assert report["source"] == [str(pyi)]
    assert _blocker_codes(report) == set()


def test_readiness_accepts_qualified_types_from_imported_modules_and_aliases():
    report = _readiness_from_pyi(
        """
import state_mod
import mesh_mod as mesh
from values_mod import value_t as imported_value

def step(a: state_mod.state_t, b: mesh.mesh_t, c: imported_value) -> None: ...
"""
    )

    assert report["wrappable"] is True


def test_readiness_reports_incomplete_prototype_payload():
    module = SemanticModule(
        "callbacks",
        functions=[
            SemanticFunction(
                "run",
                arguments=[
                    SemanticArgument(
                        "cb",
                        SemanticType(
                            "incomplete_prototype",
                            metadata={"return": SemanticType("Int32")},
                            storage=SemanticStorageContract(kind="callback"),
                        ),
                    )
                ],
            )
        ],
    )

    report = assess_semantic_wrap_readiness(module)

    assert report["wrappability_blockers"] == [
        {
            "code": "callback_signature_incomplete",
            "message": "Some callback or procedure arguments need a complete named prototype in the .pyi file.",
            "items": [
                {
                    "owner": "callbacks.run.cb",
                    "item": "cb",
                    "type": "incomplete_prototype",
                    "needs": [
                        "callback argument order",
                        "callback argument types",
                        "callback return type",
                    ],
                }
            ],
        }
    ]
    assert report["unit_blockers"] == [
        {
            "unit": "callbacks.run",
            "kind": "function",
            "blockers": report["wrappability_blockers"],
        }
    ]


def test_readiness_propagates_context_through_imports_callbacks_and_class_fields():
    nested_callback = SemanticType(
        "nested_prototype",
        metadata={
            "arguments": [
                SemanticType("MissingCallbackArg"),
                SemanticType("Float64", shape=["a + zmissing"]),
                SemanticType("Float64", shape=["n + zmissing"]),
            ],
            "return": SemanticType("types_mod.callback_result_t"),
        },
        storage=SemanticStorageContract(kind="callback"),
    )
    module = SemanticModule(
        "edge",
        imports=["types_mod"],
        variables=[
            SemanticArgument("imported", SemanticType("types_mod.variable_t")),
            SemanticArgument(
                "typed_policy",
                SemanticType(
                    "Int32",
                    metadata={"readiness_blockers": [{"code": "type_policy_only", "message": "type policy"}]},
                ),
            ),
            SemanticArgument("n", SemanticType("Int32", constraints=[SemanticConstraint("Constant")])),
        ],
        classes=[SemanticClass("State", fields=[SemanticArgument("missing", SemanticType("MissingField"))])],
        functions=[
            SemanticFunction("placeholder", arguments=[SemanticArgument("cb", SemanticType("Procedure"))]),
            SemanticFunction("imported_result", return_type=SemanticType("types_mod.result_t")),
            SemanticFunction(
                "missing_constant",
                arguments=[SemanticArgument("x", SemanticType("Float64", shape=["n"]))],
            ),
            SemanticFunction(
                "nested",
                arguments=[
                    SemanticArgument("a", SemanticType("Int32")),
                    SemanticArgument("cb", nested_callback),
                ],
            ),
        ],
    )

    report = assess_semantic_wrap_readiness(module)
    blockers = {blocker["code"]: blocker for blocker in report["wrappability_blockers"]}
    units = {unit["unit"]: unit for unit in report["unit_blockers"]}

    assert blockers["unresolved_semantic_types"]["items"] == [
        {"owner": "edge.State.missing", "item": "missing", "type": "MissingField"},
        {"owner": "edge.nested.cb.callback_arg_0", "item": "cb[0]", "type": "MissingCallbackArg"},
    ]
    assert blockers["missing_compile_time_values"]["items"] == [
        {"owner": "edge.missing_constant.x", "item": "x", "symbol": "n", "expression": "n"},
        {"owner": "edge.nested.cb.callback_arg_2", "item": "cb[2]", "symbol": "n", "expression": "n + zmissing"},
    ]
    assert blockers["unresolved_shape_symbols"]["items"] == [
        {
            "owner": "edge.nested.cb.callback_arg_1",
            "item": "cb[1]",
            "symbol": "zmissing",
            "expression": "a + zmissing",
        },
        {
            "owner": "edge.nested.cb.callback_arg_2",
            "item": "cb[2]",
            "symbol": "zmissing",
            "expression": "n + zmissing",
        },
    ]
    assert units["edge.typed_policy"]["kind"] == "variable"
    assert units["edge.State"]["kind"] == "class"
    assert units["edge.placeholder"]["kind"] == "function"
    assert units["edge.missing_constant"]["kind"] == "function"
    assert units["edge.nested"]["kind"] == "function"


def test_wrap_readiness_report_reconciles_edited_pyi_file_set(tmp_path: Path):
    physics = tmp_path / "physics.pyi"
    types_mod = tmp_path / "types_mod.pyi"
    physics.write_text(
        f"""
{CONTRACT_IMPORT}
from types_mod import particle

def create_particle() -> particle: ...
""",
        encoding="utf-8",
    )
    types_mod.write_text(
        f"""
{CONTRACT_IMPORT}
class particle:
    mass: Float64
""",
        encoding="utf-8",
    )

    payload = x2py_cli._wrap_readiness_report([str(tmp_path)])
    modules = {module["name"]: module for module in payload[str(physics)]["semantic_modules"]}
    particle_ref = modules["physics"]["functions"][0]["return_type"]["metadata"]["external_type_ref"]

    assert particle_ref["origin_module"] == "types_mod"
    assert particle_ref["wrapped"] is True
    assert particle_ref["representation"] == "wrapped"
    assert payload[str(physics)]["wrap_readiness"]["n_modules"] == 2
