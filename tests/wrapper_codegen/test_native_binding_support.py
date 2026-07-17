"""Public native-binding support surface checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUPPORT_HEADER = ROOT / "x2py" / "binding_support" / "x2py_binding.h"
SUPPORT_SOURCE = ROOT / "x2py" / "binding_support" / "x2py_binding.c"


def test_native_binding_support_exposes_only_the_small_x2py_api():
    header = SUPPORT_HEADER.read_text(encoding="utf-8")
    source = SUPPORT_SOURCE.read_text(encoding="utf-8")

    expected_api = (
        "x2py_scalar_matches",
        "x2py_scalar_unpack",
        "x2py_scalar_to_python",
        "x2py_scalar_to_numpy",
        "x2py_release_owned_memory",
    )
    for name in expected_api:
        assert name in header
        assert name in source

    removed_compatibility_names = (
        "PyInt32_to_Int32",
        "Double_to_PyDouble",
        "Complex128_to_PyComplex",
        "capsule_cleanup",
        "pyarray_check",
        "to_pyarray",
    )
    for name in removed_compatibility_names:
        assert name not in header
        assert name not in source
