"""Tests split by stable ownership concept from `test_readiness_reports.py`."""

from tests.cli._cli_support import (
    Path,
    PreprocessingConfig,
    _MainParserError,
    _install_main_parser,
    _main_args,
    pytest,
    types,
    x2py_cli,
)


@pytest.mark.parametrize(
    ("stage", "expected_stage_call"),
    [
        ("semantics", "semantic"),
        ("pyi", "semantic"),
        ("wrap_readiness", "readiness"),
    ],
)
def test_x2py_main_passes_c_type_report_to_each_semantic_stage(monkeypatch, stage, expected_stage_call):
    class StopAfterDispatch(Exception):
        pass

    args = _main_args(
        language="c",
        **{stage: True},
        c_type_probe_runner=["qemu"],
        c_type_probe_cache_dir="cache",
        refresh_c_type_probe=True,
    )
    _install_main_parser(monkeypatch, args)
    preprocessing = object()
    report = {"types": {"long": {"kind": "integer", "signed": True, "bits": 32}}}
    calls = []

    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: preprocessing)
    monkeypatch.setattr(
        x2py_cli,
        "_c_standard_type_report",
        lambda active_preprocessing, **kwargs: calls.append(("probe", active_preprocessing, kwargs)) or report,
    )
    monkeypatch.setattr(
        x2py_cli,
        "_semantic_report",
        lambda paths, active_preprocessing, **kwargs: calls.append(("semantic", kwargs)) or {},
    )
    monkeypatch.setattr(
        x2py_cli,
        "_wrap_readiness_report",
        lambda paths, active_preprocessing, **kwargs: calls.append(("readiness", kwargs)) or {},
    )
    monkeypatch.setattr(
        x2py_cli,
        "_attach_wrap_readiness",
        lambda semantic_payload, readiness_payload: (_ for _ in ()).throw(StopAfterDispatch),
    )

    with pytest.raises(StopAfterDispatch):
        x2py_cli.main()

    assert calls == [
        (
            "probe",
            preprocessing,
            {
                "report_path": None,
                "runner": ["qemu"],
                "cache_dir": "cache",
                "refresh": True,
            },
        ),
        (expected_stage_call, {"language": "c", "c_standard_type_report": report}),
    ]


def test_x2py_main_rejects_c_parse_wrap_readiness_combination(monkeypatch):
    args = _main_args(language="c", parse=True, wrap_readiness=True, print_limit=1)
    _install_main_parser(monkeypatch, args)
    monkeypatch.setattr(x2py_cli, "_resolve_language", lambda paths, language, parser: language)
    monkeypatch.setattr(x2py_cli, "_build_preprocessing_config", lambda active_args, parser: object())

    with pytest.raises(_MainParserError) as exc_info:
        x2py_cli.main()

    assert str(exc_info.value) == "Choose exactly one stage flag; cannot combine --parse, --wrap-readiness"


def test_x2py_readiness_formatting_and_compiler_without_requirements():
    assert (
        x2py_cli._format_semantic_blocker_item(
            "unresolved_semantic_types",
            {"owner": "module.api", "type": "external_t"},
        )
        == "module.api uses unresolved type external_t"
    )
    assert (
        x2py_cli._format_semantic_blocker_item(
            "unresolved_shape_symbols",
            {"owner": "module.api", "expression": "n + 1", "symbol": "n"},
        )
        == "module.api shape 'n + 1' uses unresolved symbol n"
    )
    assert (
        x2py_cli._format_semantic_blocker_item(
            "missing_compile_time_values",
            {"owner": "module.api", "symbol": "dp"},
        )
        == "module.api needs literal value for Final constant dp"
    )
    assert (
        x2py_cli._format_semantic_blocker_item(
            "callback_signature_incomplete",
            {"owner": "handler", "needs": ["arguments", "return type"]},
        )
        == "handler needs Callable[[...], ...] metadata (arguments, return type)"
    )
    assert x2py_cli._format_semantic_blocker_item("c_unknown_type", {"owner": "api", "type": "widget"}) == "api: widget"
    assert x2py_cli._format_semantic_blocker_item("c_unknown_type", {"type": "widget"}) == "<c-source>: widget"
    assert x2py_cli._format_semantic_blocker_item("c_macro_value", {"owner": "api", "source": "SIZE"}) == "api: SIZE"
    assert (
        x2py_cli._format_semantic_blocker_item("c_function_pointer", {"owner": "api", "function": "callback"})
        == "api: callback"
    )
    assert (
        x2py_cli._format_semantic_blocker_item("c_parameter_type", {"owner": "api", "parameter": "arg"}) == "api: arg"
    )
    assert x2py_cli._format_semantic_blocker_item("c_unresolved_type", {"owner": "api", "type": "missing_t"}) == (
        "api: missing_t"
    )
    assert (
        x2py_cli._format_semantic_blocker_item("no_public_api", {"owner": "module", "needs": ["function", "class"]})
        == "module needs function, class"
    )
    assert x2py_cli._format_semantic_blocker_item("unknown", {"value": 1}) == "{'value': 1}"

    semantic_payload = {"source": {"semantic_modules": []}}
    x2py_cli._attach_wrap_readiness(semantic_payload, {"other": {"wrap_readiness": {"wrappable": True}}})
    assert "wrap_readiness" not in semantic_payload["source"]

    parsed = x2py_cli.FortranParser().parse_file("module empty\nend module empty\n", filename="empty.f90")
    config = x2py_cli.PreprocessingConfig(mode="compiler", compiler="gfortran")
    assert x2py_cli._fortran_compile_time_values(parsed, config) is None


def test_x2py_fortran_readiness_helpers_attach_and_compile(monkeypatch):
    ready = {"wrappable": True, "n_functions": 1}
    payload = {"missing.f90": {}, "api.f90": {}}
    x2py_cli._attach_wrap_readiness(payload, {"api.f90": {"wrap_readiness": ready}})
    assert payload == {"missing.f90": {}, "api.f90": {"wrap_readiness": ready}}

    x2py_cli._attach_wrap_readiness(None, {"api.f90": {"wrap_readiness": ready}})
    x2py_cli._attach_wrap_readiness({"api.f90": {}}, None)

    parsed = x2py_cli.FortranParser().parse_file(
        "module api_mod\n  type :: Widget_T\n  end type Widget_T\nend module api_mod\n",
        filename="api.f90",
    )
    assert x2py_cli._fortran_wrapped_derived_types([parsed]) == {("api_mod", "widget_t")}

    calls = []
    requirements = {"api_mod": {"dp": "kind(1.0d0)"}}
    values = {"api_mod.dp": 8}
    storage_requirements = [{"base_type": "real", "kind": "8", "expression": "storage_size(real(0.0,kind=8))"}]
    facts = {("real", "8"): {"base_type": "real", "kind": "8", "bits": 64}}

    def collect_requirements(received):
        assert received is parsed
        calls.append(("collect", received))
        return requirements

    def evaluate_requirements(received_config, received_requirements):
        assert received_config is compiler_config
        assert received_requirements is requirements
        calls.append(("evaluate", received_config, received_requirements))
        return values

    def collect_storage(received, *, compile_time_values):
        assert received is parsed
        assert compile_time_values is values
        calls.append(("collect_storage", received))
        return storage_requirements

    def evaluate_facts(received_config, received_requirements):
        assert received_config is compiler_config
        assert received_requirements is storage_requirements
        calls.append(("evaluate_facts", received_config, received_requirements))
        return facts

    monkeypatch.setattr("x2py.semantics.fortran2ir.collect_semantic_compile_time_requirements", collect_requirements)
    monkeypatch.setattr("x2py.semantics.fortran2ir.collect_fortran_type_storage_requirements", collect_storage)
    monkeypatch.setattr("x2py.probes.fortran_types.evaluate_fortran_type_requirements", evaluate_requirements)
    monkeypatch.setattr("x2py.probes.fortran_types.evaluate_fortran_type_facts", evaluate_facts)

    raw_config_with_compiler = x2py_cli.PreprocessingConfig(compiler="gfortran")
    assert x2py_cli._fortran_compile_time_values(parsed, raw_config_with_compiler) is None
    assert calls == []

    compiler_config = x2py_cli.PreprocessingConfig(mode="compiler", compiler="gfortran")
    assert x2py_cli._fortran_compile_time_values(parsed, compiler_config) == values
    assert calls == [("collect", parsed), ("evaluate", compiler_config, requirements)]
    assert x2py_cli._fortran_type_facts(parsed, compiler_config, compile_time_values=values) == facts
    assert calls[-2:] == [("collect_storage", parsed), ("evaluate_facts", compiler_config, storage_requirements)]


def test_x2py_parse_report_preserves_fortran_parser_and_recipe_contracts(monkeypatch):
    path = Path("api.F90")
    explicit_config = object()
    default_config = object()
    recipe = {"mode": "compiler"}
    nodes = {
        "signature": object(),
        "type": object(),
        "module": object(),
        "submodule": object(),
        "program": object(),
        "block_data": object(),
    }
    labels = {node: {"node": label} for label, node in nodes.items()}
    parsed = types.SimpleNamespace(
        procedures=[nodes["signature"]],
        derived_types=[nodes["type"]],
        modules=[nodes["module"]],
        submodules=[nodes["submodule"]],
        programs=[nodes["program"]],
        block_data_units=[nodes["block_data"]],
    )
    calls = []

    def make_config():
        calls.append(("config",))
        return default_config

    def expand(paths):
        assert paths == ["api"]
        calls.append(("expand", paths))
        return [path]

    def source(received_path, config):
        assert received_path == path
        assert config in {explicit_config, default_config}
        calls.append(("source", received_path, config))
        if config is explicit_config:
            return "explicit source", recipe
        return "default source", None

    class Parser:
        def parse_file(self, code, *, filename):
            assert code in {"explicit source", "default source"}
            assert filename == str(path)
            calls.append(("visit", code, filename))
            return parsed

    def serialize(node):
        assert node in labels
        calls.append(("serialize", node))
        return labels[node]

    payload = {
        "signatures": [labels[nodes["signature"]]],
        "types": [labels[nodes["type"]]],
        "modules": [labels[nodes["module"]]],
        "submodules": [labels[nodes["submodule"]]],
        "programs": [labels[nodes["program"]]],
        "block_data": [labels[nodes["block_data"]]],
    }

    monkeypatch.setattr(x2py_cli, "PreprocessingConfig", make_config)
    monkeypatch.setattr(x2py_cli, "FortranParser", Parser)
    monkeypatch.setattr(x2py_cli, "_expand_paths", expand)
    monkeypatch.setattr(x2py_cli, "_fortran_source_for_path", source)
    monkeypatch.setattr(x2py_cli, "_to_dict_no_parent", serialize)

    assert x2py_cli._parse_report(["api"], explicit_config) == {str(path): {**payload, "preprocessing_recipe": recipe}}
    assert ("config",) not in calls

    calls.clear()
    assert x2py_cli._parse_report(["api"]) == {str(path): payload}
    assert calls[0] == ("config",)


def test_x2py_semantic_report_preserves_c_module_and_dependency_contracts(monkeypatch):
    path = Path("api.h")
    config = object()
    project = object()
    standard_type_report = {"types": {"long": {"kind": "integer", "signed": True, "bits": 32}}}
    module = types.SimpleNamespace(name="api", origin=types.SimpleNamespace(native_name=str(path)))
    stubs = {
        "api": "def api() -> None: ...",
        "shared": "class Shared:\n    pass",
    }

    def parse_project(paths, preprocessing):
        assert paths == ["api"]
        assert preprocessing is config
        return project

    def convert(received, *, standard_type_report: object):
        assert received is project
        assert standard_type_report == {"types": {"long": {"kind": "integer", "signed": True, "bits": 32}}}
        return [module]

    def expand(paths):
        assert paths == ["api"]
        return [path]

    def emit(modules, *, available_modules):
        assert modules == [module]
        assert available_modules == [module]
        return stubs

    def serialize(received):
        assert received is module
        return {"name": "api"}

    monkeypatch.setattr(x2py_cli, "_parse_c_project", parse_project)
    monkeypatch.setattr(x2py_cli, "c_project_to_semantic_modules", convert)
    monkeypatch.setattr(x2py_cli, "expand_c_paths", expand)
    monkeypatch.setattr("x2py.wrapper_codegen.printers.emit_module_stubs", emit)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)

    assert x2py_cli._semantic_report(
        ["api"],
        config,
        language="c",
        c_standard_type_report=standard_type_report,
    ) == {
        str(path): {
            "semantic_modules": [{"name": "api"}],
            "pyi": "def api() -> None: ...",
            "pyi_modules": {"api": "def api() -> None: ..."},
            "pyi_dependencies": {"shared": "class Shared:\n    pass"},
        }
    }


def test_x2py_c_standard_type_report_uses_cached_direct_probe_and_rejects_ambiguous_recipe(monkeypatch):
    config = PreprocessingConfig(mode="compiler", compiler="cc", compiler_args=["-m32"])
    expected = {"types": {"long": {"kind": "integer", "signed": True, "bits": 32}}}
    calls = []

    class Report:
        def to_dict(self):
            return expected

    def probe(received, *, runner, cache_dir, refresh):
        calls.append((received, runner, cache_dir, refresh))
        return Report()

    monkeypatch.setattr(x2py_cli, "probe_c_standard_types_cached", probe)

    assert (
        x2py_cli._c_standard_type_report(
            config,
            runner=["qemu"],
            cache_dir="cache",
            refresh=True,
        )
        == expected
    )
    assert calls == [(config, ["qemu"], "cache", True)]

    with pytest.raises(ValueError, match="--c-type-report"):
        x2py_cli._c_standard_type_report(
            PreprocessingConfig(mode="compiler", compiler="cc", compile_commands="compile_commands.json")
        )


def test_x2py_semantic_report_preserves_fortran_conversion_and_stub_contracts(monkeypatch):
    path = Path("api.f90")
    config = object()
    wrapped_types = {("types_mod", "widget")}
    expected_compile_time_values = {"api.dp": 8}
    native_left = object()
    native_right = object()
    left = types.SimpleNamespace(name="left")
    right = types.SimpleNamespace(name="right")
    parsed = types.SimpleNamespace(modules=[native_left, native_right])
    stubs = {
        "left": "class Left:\n    pass",
        "right": "class Right:\n    pass",
        "shared": "class Shared:\n    pass",
    }

    class Parser:
        def parse_file(self, code, *, filename):
            assert code == "fortran source"
            assert filename == str(path)
            return parsed

    def expand(paths):
        assert paths == ["api"]
        return [path]

    def source(received_path, preprocessing):
        assert received_path == path
        assert preprocessing is config
        return "fortran source", None

    def wrapped(parsed_files):
        assert list(parsed_files) == [parsed]
        return wrapped_types

    def compile_values(received, preprocessing):
        assert received is parsed
        assert preprocessing is config
        return expected_compile_time_values

    def convert(
        received,
        *,
        standalone_module_name,
        compile_time_values: object,
        wrapped_derived_types,
    ):
        assert received is parsed
        assert standalone_module_name == "api"
        assert compile_time_values is expected_compile_time_values
        assert wrapped_derived_types is wrapped_types
        return [left, right]

    def emit(modules, *, available_modules):
        assert modules == [left, right]
        assert available_modules == [left, right]
        return stubs

    def serialize(module):
        assert module is left or module is right
        return {"name": module.name}

    monkeypatch.setattr(x2py_cli, "FortranParser", Parser)
    monkeypatch.setattr(x2py_cli, "_expand_paths", expand)
    monkeypatch.setattr(x2py_cli, "_fortran_source_for_path", source)
    monkeypatch.setattr(x2py_cli, "_fortran_wrapped_derived_types", wrapped)
    monkeypatch.setattr(x2py_cli, "_fortran_compile_time_values", compile_values)
    monkeypatch.setattr(x2py_cli, "fortran_file_to_semantic_modules", convert)
    monkeypatch.setattr("x2py.wrapper_codegen.printers.emit_module_stubs", emit)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)

    assert x2py_cli._semantic_report(["api"], config) == {
        str(path): {
            "semantic_modules": [{"name": "left"}, {"name": "right"}],
            "pyi": "class Left:\n    pass\n\nclass Right:\n    pass",
            "pyi_modules": {
                "left": "class Left:\n    pass",
                "right": "class Right:\n    pass",
            },
            "pyi_dependencies": {"shared": "class Shared:\n    pass"},
        }
    }


def test_x2py_wrap_readiness_report_preserves_c_and_pyi_contracts(monkeypatch):
    path = Path("api.h")
    stub = Path("api.pyi")
    config = object()
    project = object()
    module = types.SimpleNamespace(name="api", origin=types.SimpleNamespace(native_name=str(path)))
    readiness = {"wrappable": True, "source": str(path)}
    pyi_report = {str(stub): {"source_kind": "pyi"}}

    def expand(paths):
        assert paths == ["api"]
        return [path, stub]

    def parse_project(paths, preprocessing):
        assert paths == [str(path)]
        assert preprocessing is config
        return project

    def convert(received):
        assert received is project
        return [module]

    def serialize(received):
        assert received is module
        return {"name": "api"}

    def assess(modules, *, source):
        assert modules == [module]
        assert source == str(path)
        return readiness

    def pyi(paths):
        assert paths == ["api"]
        return pyi_report

    monkeypatch.setattr(x2py_cli, "expand_c_paths", expand)
    monkeypatch.setattr(x2py_cli, "_parse_c_project", parse_project)
    monkeypatch.setattr(x2py_cli, "c_project_to_semantic_modules", convert)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)
    monkeypatch.setattr(x2py_cli, "assess_semantic_wrap_readiness", assess)
    monkeypatch.setattr(x2py_cli, "_pyi_readiness_report", pyi)

    assert x2py_cli._wrap_readiness_report(["api"], config, language="c") == {
        str(path): {
            "source_kind": "c",
            "semantic_modules": [{"name": "api"}],
            "wrap_readiness": readiness,
        },
        **pyi_report,
    }


def test_x2py_wrap_readiness_report_preserves_fortran_and_pyi_contracts(monkeypatch):
    path = Path("api.f90")
    stub = Path("api.pyi")
    config = object()
    parsed = object()
    wrapped_types = {("types_mod", "widget")}
    compile_time_values = {"api.dp": 8}
    module = types.SimpleNamespace(name="api")
    readiness = {"wrappable": True, "source": str(path)}
    pyi_report = {str(stub): {"source_kind": "pyi"}}

    class Parser:
        def parse_file(self, code, *, filename):
            assert code == "fortran source"
            assert filename == str(path)
            return parsed

    def expand(paths):
        assert paths == ["api"]
        return [path, stub]

    def source(received_path, preprocessing):
        assert received_path == path
        assert preprocessing is config
        return "fortran source", None

    def wrapped(parsed_files):
        assert list(parsed_files) == [parsed]
        return wrapped_types

    def compile_values(received, preprocessing):
        assert received is parsed
        assert preprocessing is config
        return compile_time_values

    def convert(received, *, standalone_module_name, compile_time_values: object, wrapped_derived_types):
        assert received is parsed
        assert standalone_module_name == "api"
        assert compile_time_values is expected_compile_time_values
        assert wrapped_derived_types is wrapped_types
        return [module]

    def serialize(received):
        assert received is module
        return {"name": "api"}

    def assess(modules, *, source):
        assert modules == [module]
        assert source == str(path)
        return readiness

    def pyi(paths):
        assert paths == ["api"]
        return pyi_report

    expected_compile_time_values = compile_time_values
    monkeypatch.setattr(x2py_cli, "FortranParser", Parser)
    monkeypatch.setattr(x2py_cli, "_expand_readiness_paths", expand)
    monkeypatch.setattr(x2py_cli, "_fortran_source_for_path", source)
    monkeypatch.setattr(x2py_cli, "_fortran_wrapped_derived_types", wrapped)
    monkeypatch.setattr(x2py_cli, "_fortran_compile_time_values", compile_values)
    monkeypatch.setattr(x2py_cli, "fortran_file_to_semantic_modules", convert)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)
    monkeypatch.setattr(x2py_cli, "assess_semantic_wrap_readiness", assess)
    monkeypatch.setattr(x2py_cli, "_pyi_readiness_report", pyi)

    assert x2py_cli._wrap_readiness_report(["api"], config) == {
        str(path): {
            "source_kind": "fortran",
            "semantic_modules": [{"name": "api"}],
            "wrap_readiness": readiness,
        },
        **pyi_report,
    }


def test_x2py_readiness_path_helpers_include_fortran_and_pyi(tmp_path: Path):
    source = tmp_path / "mini.f90"
    stub = tmp_path / "api.pyi"
    ignored = tmp_path / "notes.txt"
    source.write_text("module mini\nend module mini\n", encoding="utf-8")
    stub.write_text("def work() -> None: ...\n", encoding="utf-8")
    ignored.write_text("ignore", encoding="utf-8")

    assert set(x2py_cli._collect_readiness_extensions(tmp_path)) == {source, stub}
    assert set(x2py_cli._expand_readiness_paths([str(tmp_path), str(source), str(ignored)])) == {
        source,
        stub,
        ignored,
    }


def test_x2py_pyi_readiness_report_preserves_loading_and_assessment_contracts(tmp_path: Path, monkeypatch):
    package = tmp_path / "package"
    package.mkdir()
    stub = tmp_path / "api.pyi"
    ignored = tmp_path / "notes.txt"
    module = object()
    readiness = {"wrappable": True, "source": str(stub)}
    calls = []

    def expand(paths):
        assert paths == [str(package), str(stub), str(ignored)]
        calls.append(("expand", paths))
        return [stub]

    def load(paths):
        assert paths == [str(package), str(stub)]
        calls.append(("load", paths))
        return [module]

    def serialize(received):
        assert received is module
        calls.append(("asdict", received))
        return {"name": "api"}

    def assess(modules, *, source, require_native_contract):
        assert modules == [module]
        assert source == str(stub)
        assert require_native_contract is True
        calls.append(("assess", modules, source))
        return readiness

    monkeypatch.setattr(x2py_cli, "_expand_pyi_paths", expand)
    monkeypatch.setattr(x2py_cli, "pyi_paths_to_semantic_modules", load)
    monkeypatch.setattr(x2py_cli, "asdict", serialize)
    monkeypatch.setattr(x2py_cli, "assess_semantic_wrap_readiness", assess)

    assert x2py_cli._pyi_readiness_report([str(package), str(stub), str(ignored)]) == {
        str(stub): {
            "source_kind": "pyi",
            "semantic_modules": [{"name": "api"}],
            "wrap_readiness": readiness,
        }
    }
    assert calls == [
        ("expand", [str(package), str(stub), str(ignored)]),
        ("load", [str(package), str(stub)]),
        ("asdict", module),
        ("assess", [module], str(stub)),
    ]

    calls.clear()
    monkeypatch.setattr(x2py_cli, "_expand_pyi_paths", lambda _paths: [])
    assert x2py_cli._pyi_readiness_report([str(ignored)]) == {}
    assert calls == []


def test_x2py_format_semantic_readiness_reports_wrappable_and_blocked_sources():
    report = {
        "api.f90": {
            "source_kind": "fortran",
            "semantic_modules": [{"name": "api_mod"}],
            "wrap_readiness": {
                "wrappable": False,
                "n_functions": 1,
                "n_classes": 0,
                "n_variables": 2,
                "wrappability_blockers": [
                    {
                        "code": "unresolved_semantic_types",
                        "message": "unresolved external type",
                        "items": [{"owner": "api_mod.solve", "type": "external_t"}],
                    },
                    {
                        "code": "callback_signature_incomplete",
                        "message": "callback metadata incomplete",
                        "items": [{"owner": "api_mod.apply", "needs": ["arguments"]}],
                    },
                ],
            },
        },
        "interface.pyi": {
            "source_kind": "pyi",
            "semantic_modules": [],
            "wrap_readiness": {
                "wrappable": True,
                "n_functions": 0,
                "n_classes": 1,
                "n_variables": 0,
                "wrappability_blockers": [],
            },
        },
        "partial.f90": {
            "semantic_modules": [{}],
        },
    }

    text = x2py_cli._format_semantic_readiness(report)
    assert (
        text
        == """File: api.f90
  Source: fortran
  Semantic modules: api_mod
  Wrappable: no
  Public functions: 1
  Public classes: 0
  Public variables: 2
  Why not wrappable:
    - unresolved_semantic_types: unresolved external type
      * api_mod.solve uses unresolved type external_t
    - callback_signature_incomplete: callback metadata incomplete
      * api_mod.apply needs Callable[[...], ...] metadata (arguments)

File: interface.pyi
  Source: pyi
  Semantic modules: <none>
  Wrappable: yes
  Public functions: 0
  Public classes: 1
  Public variables: 0
  No semantic readiness blockers detected.

File: partial.f90
  Source: <unknown>
  Semantic modules: <unknown>
  Wrappable: no
  Public functions: 0
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected."""
    )

    assert "File: api.f90" in text
    assert "  Source: fortran" in text
    assert "  Semantic modules: api_mod" in text
    assert "  Wrappable: no" in text
    assert "  Public functions: 1" in text
    assert "  Public classes: 0" in text
    assert "  Public variables: 2" in text
    assert "  Why not wrappable:" in text
    assert "    - unresolved_semantic_types: unresolved external type" in text
    assert "      * api_mod.solve uses unresolved type external_t" in text
    assert "      * api_mod.apply needs Callable[[...], ...] metadata (arguments)" in text
    assert "File: interface.pyi" in text
    assert "  Source: pyi" in text
    assert "  Semantic modules: <none>" in text
    assert "  Wrappable: yes" in text
    assert "  No semantic readiness blockers detected." in text
    assert "File: partial.f90" in text
    assert "  Source: <unknown>" in text
    assert "  Semantic modules: <unknown>" in text


def test_x2py_format_semantic_readiness_defaults_and_multiple_modules():
    report = {
        "missing.f90": {
            "wrap_readiness": {
                "wrappable": False,
                "wrappability_blockers": [
                    {
                        "message": "missing code",
                        "items": [{"value": 2}],
                    }
                ],
            },
        },
        "multi.f90": {
            "source_kind": "fortran",
            "semantic_modules": [{"name": "left"}, {"name": "right"}],
            "wrap_readiness": {
                "wrappable": True,
                "n_functions": 2,
                "n_classes": 1,
                "n_variables": 3,
                "wrappability_blockers": [],
            },
        },
    }

    assert (
        x2py_cli._format_semantic_readiness(report)
        == """File: missing.f90
  Source: <unknown>
  Semantic modules: <none>
  Wrappable: no
  Public functions: 0
  Public classes: 0
  Public variables: 0
  Why not wrappable:
    - None: missing code
      * {'value': 2}

File: multi.f90
  Source: fortran
  Semantic modules: left, right
  Wrappable: yes
  Public functions: 2
  Public classes: 1
  Public variables: 3
  No semantic readiness blockers detected."""
    )
