"""Tests split by stable ownership concept from `test_properties.py`."""

from tests._shared.parser_property_support import (
    CParseError,
    FortranParseError,
    Path,
    PreprocessingConfig,
    TemporaryDirectory,
    _C_IDENTIFIERS,
    _FORTRAN_IDENTIFIER_STEMS,
    given,
    parse_c_file,
    parse_fortran_file,
    patch,
    preprocess_source,
    preprocessing,
    pytest,
    st,
    sys,
)


@pytest.mark.property
@given(include_stem=_FORTRAN_IDENTIFIER_STEMS)
def test_generated_fortran_native_includes_do_not_change_public_signature(include_stem):
    target = f"{include_stem}.inc"
    baseline = "subroutine generated_include(value)\n  integer, intent(in) :: value\nend subroutine generated_include\n"
    with_include = (
        f"subroutine generated_include(value)\n"
        f"  include '{target}'\n"
        "  integer, intent(in) :: value\n"
        "end subroutine generated_include\n"
    )

    baseline_parsed = parse_fortran_file(baseline, filename="generated_include.f90")
    included_parsed = parse_fortran_file(with_include, filename="generated_include.f90")

    assert included_parsed.diagnostics == []
    assert included_parsed.procedures == baseline_parsed.procedures


@pytest.mark.property
@given(feature_stem=_FORTRAN_IDENTIFIER_STEMS)
def test_generated_fortran_raw_preprocessor_directives_require_preprocessing(feature_stem):
    feature = f"feature_{feature_stem}"
    source = f"#ifdef {feature}\nsubroutine generated_conditional()\nend subroutine generated_conditional\n#endif\n"

    with pytest.raises(FortranParseError, match="require compiler preprocessing") as exc_info:
        parse_fortran_file(source, filename="generated_conditional.F90")

    assert exc_info.value.code == "PARSE_PREPROCESSING_REQUIRED"


@pytest.mark.property
@given(feature_stem=_FORTRAN_IDENTIFIER_STEMS, select_feature=st.booleans())
def test_generated_fortran_compiler_preprocessing_selects_macro_branch(feature_stem, select_feature):
    feature = f"feature_{feature_stem}"
    with TemporaryDirectory() as tmp_dir:
        source_path = Path(tmp_dir) / "generated_conditional.F90"
        source_path.write_text(
            f"#ifdef {feature}\n"
            "subroutine selected_path()\n"
            "end subroutine selected_path\n"
            "#else\n"
            "subroutine fallback_path()\n"
            "end subroutine fallback_path\n"
            "#endif\n",
            encoding="utf-8",
        )
        captured_argv = []

        def run_compiler(argv, **_kwargs):
            captured_argv.extend(argv)
            selected = f"-D{feature}" in argv
            procedure_name = "selected_path" if selected else "fallback_path"
            stdout = f"subroutine {procedure_name}()\nend subroutine {procedure_name}\n"
            return type("Done", (), {"returncode": 0, "stdout": stdout, "stderr": ""})()

        defines = [feature] if select_feature else []
        with patch.object(preprocessing.subprocess, "run", run_compiler):
            result = preprocess_source(
                source_path,
                language="fortran",
                config=PreprocessingConfig(mode="compiler", compiler=sys.executable, defines=defines),
            )
        parsed = parse_fortran_file(result.source, filename=str(source_path))

    assert "-cpp" in captured_argv
    assert (f"-D{feature}" in captured_argv) is select_feature
    assert result.recipe["defines"] == defines
    assert [procedure.name for procedure in parsed.procedures] == [
        "selected_path" if select_feature else "fallback_path"
    ]


@pytest.mark.property
@given(
    feature=_C_IDENTIFIERS,
    function_names=st.lists(_C_IDENTIFIERS, min_size=2, max_size=2, unique=True),
)
def test_generated_c_raw_conditionals_require_preprocessing(feature, function_names):
    source = f"#ifdef {feature}\nint {function_names[0]}(void);\n#else\nint {function_names[1]}(void);\n#endif\n"

    with pytest.raises(CParseError, match="require compiler preprocessing") as exc_info:
        parse_c_file(source, filename="conditional.h", preprocessing="raw")

    assert exc_info.value.code == "CPARSE_PREPROCESSING_REQUIRED"


@pytest.mark.property
@given(line_number=st.integers(min_value=1, max_value=100_000), stem=_C_IDENTIFIERS)
def test_generated_c_linemarkers_map_function_origin(line_number, stem):
    mapped_filename = f"{stem}.h"
    source = f'#line {line_number} "{mapped_filename}"\nint exported(void);\n'

    parsed = parse_c_file(source, filename="generated.i", preprocessing="preprocessed")

    assert parsed.diagnostics == []
    assert len(parsed.functions) == 1
    assert parsed.functions[0].source_location is not None
    assert parsed.functions[0].source_location.filename == mapped_filename
    assert parsed.functions[0].source_location.line == line_number


@pytest.mark.property
@given(local_stem=_C_IDENTIFIERS, system_stem=_C_IDENTIFIERS)
def test_generated_c_raw_includes_record_local_and_system_targets(local_stem, system_stem):
    local_target = f"hypothesis_missing_{local_stem}.h"
    system_target = f"{system_stem}.h"
    source = f'#include "{local_target}"\n#include <{system_target}>\nint exported(void);\n'

    parsed = parse_c_file(source, filename="generated_api.h", preprocessing="raw")

    assert [(include.target, include.kind) for include in parsed.includes] == [
        (local_target, "local"),
        (system_target, "system"),
    ]
    assert [diagnostic.code for diagnostic in parsed.diagnostics] == ["C_UNRESOLVED_INCLUDE"]
