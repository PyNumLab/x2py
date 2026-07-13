"""Tests for building already-rendered wrapper-plan artifacts."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests._shared.ownership_policy_support import parse_pyi_text
from x2py.compiling.basic import CompileObj
from x2py.pipeline.build import (
    NativeBuildPlan,
    NativeLinkItem,
    _build_rendered_wrapper_extension,
)
from x2py.pipeline.wrapper_artifacts import (
    GeneratedSourceFile,
    GeneratedWrapperArtifacts,
    RenderedGeneratedWrapperArtifacts,
)
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.stage_values import FrozenStageRecordError
from x2py.wrapper_codegen import (
    ModulePlan,
    WrapperCodeGenerator,
    WrapperPlanner,
)


class RecordingCompiler:
    """Compiler test double that records compile/link calls and creates files."""

    def __init__(self):
        self.compiled = []
        self.linked = None

    def compile_module(self, compile_obj, output_folder, language, verbose):
        self.compiled.append((compile_obj, Path(output_folder), language, verbose))
        compile_obj.module_target.parent.mkdir(parents=True, exist_ok=True)
        compile_obj.module_target.write_text(f"{language} object\n", encoding="utf-8")
        if language == "fortran":
            module_file = Path(output_folder) / f"{compile_obj.python_module}.mod"
            module_file.write_text("fortran module\n", encoding="utf-8")

    def compile_shared_library(self, compile_obj, output_folder, language, verbose, sharedlib_modname=None):
        name = sharedlib_modname or compile_obj.python_module
        shared_library = Path(output_folder) / f"{name}.so"
        shared_library.write_text("shared library\n", encoding="utf-8")
        self.linked = (compile_obj, Path(output_folder), language, verbose, sharedlib_modname)
        return str(shared_library)


def _module_plan(source: str, *, module_name: str) -> ModulePlan:
    module = parse_pyi_text(source, module_name=module_name)
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def _rendered_artifacts(source: str, *, module_name: str) -> RenderedGeneratedWrapperArtifacts:
    return WrapperCodeGenerator().generate(_module_plan(source, module_name=module_name))


def test_build_rendered_wrapper_extension_writes_compiles_runtime_and_links(tmp_path: Path):
    rendered = _rendered_artifacts(
        """
@bind("SCALE")
@native_call([Addr(Arg(0))])
def scale(x: Float64) -> Float64: ...
""",
        module_name="plan_scalar_build",
    )
    native_dir = tmp_path / "native"
    native_dir.mkdir()
    native_source = native_dir / "scale_native.f90"
    native_source.write_text("native source placeholder\n", encoding="utf-8")
    native_obj = CompileObj(native_source.name, native_dir)
    native_obj.module_target.write_text("native object\n", encoding="utf-8")
    native_plan = NativeBuildPlan(
        produced_objects=(native_obj.module_target,),
        link_items=(NativeLinkItem("object", native_obj.module_target),),
        module_dirs=(native_dir,),
    )
    compiler = RecordingCompiler()

    result = _build_rendered_wrapper_extension(
        rendered,
        output_dir=tmp_path / "build",
        shared_library_output_dir=tmp_path / "extension",
        sources=(Path("scale_contract.pyi"),),
        native_build_plan=native_plan,
        native_dependencies=(native_obj,),
        native_link_args=(str(native_obj.module_target),),
        wrapper_fortran_flags=("-O2",),
        wrapper_c_flags=("-O3",),
        compiler=compiler,
    )

    build_dir = tmp_path / "build"
    bridge_source = build_dir / "bind_c_plan_scalar_build_wrapper.f90"
    binding_source = build_dir / "plan_scalar_build_wrapper.c"
    header = build_dir / "plan_scalar_build_wrapper.h"
    runtime_source = build_dir / "x2py_runtime" / "python_runtime.c"
    runtime_object = build_dir / "x2py_runtime" / "python_runtime.o"

    assert bridge_source.read_text(encoding="utf-8") == rendered.sources[0].text
    assert binding_source.read_text(encoding="utf-8") == rendered.sources[1].text
    assert header.read_text(encoding="utf-8") == rendered.sources[2].text
    assert runtime_source.exists()
    assert runtime_object.exists()
    assert [language for _obj, _output, language, _verbose in compiler.compiled] == ["fortran", "c", "c"]

    bridge_obj = compiler.compiled[0][0]
    runtime_obj = compiler.compiled[1][0]
    binding_obj = compiler.compiled[2][0]
    assert tuple(bridge_obj.dependencies) == (native_obj,)
    assert native_dir in bridge_obj.include
    assert tuple(binding_obj.dependencies) == (native_obj, bridge_obj, runtime_obj)
    assert binding_obj.link_args == (str(native_obj.module_target),)
    assert binding_obj.extra_compilation_tools == {"python"}
    assert compiler.linked == (binding_obj, tmp_path / "extension", "fortran", False, "plan_scalar_build")

    assert result.sources == (Path("scale_contract.pyi"),)
    assert result.module_name == "plan_scalar_build"
    assert result.output_dir == build_dir
    assert result.shared_library == tmp_path / "extension" / "plan_scalar_build.so"
    assert result.shared_library.exists()
    assert result.compiled is True
    assert result.build_makefile is None
    assert result.native_build_plan == native_plan
    assert result.generated_sources == (bridge_source, binding_source, header)
    assert bridge_obj.module_target in result.generated_files
    assert binding_obj.module_target in result.generated_files
    assert runtime_source in result.generated_files
    assert runtime_object in result.generated_files


def test_build_rendered_wrapper_extension_rejects_unknown_runtime_support_key(tmp_path: Path):
    rendered = RenderedGeneratedWrapperArtifacts(
        artifacts=GeneratedWrapperArtifacts(
            module_name="bad_runtime",
            binding_sources=(Path("bad_runtime_wrapper.c"),),
            runtime_support_keys=("unknown_runtime",),
        ),
        sources=(GeneratedSourceFile(Path("bad_runtime_wrapper.c"), "PyObject *unused;\n"),),
        extension_init_name="PyInit_bad_runtime",
    )

    with pytest.raises(ValueError, match="Unsupported wrapper runtime support key"):
        _build_rendered_wrapper_extension(
            rendered,
            output_dir=tmp_path,
            compiler=RecordingCompiler(),
        )
    with pytest.raises(FrozenStageRecordError):
        rendered.extension_init_name = "PyInit_later"
