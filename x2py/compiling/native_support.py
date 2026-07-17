"""Install bundled native binding support for generated CPython wrappers."""

from pathlib import Path
import shutil

from filelock import FileLock
import numpy as np

import x2py.binding_support as binding_support_folder

from .objects import ObjectFile


_NATIVE_SUPPORT_IMPORT = "binding_support"
_NATIVE_SUPPORT_SOURCE = Path(binding_support_folder.__file__).parent


def _numpy_version_header() -> str:
    """Return NumPy API version guards for the bundled native support."""
    maximum_supported = [1, 19]
    current = [int(value) for value in np.version.version.split(".")[:2]]
    major, minor = min(maximum_supported, current)
    header = f"#ifndef NPY_NO_DEPRECATED_API\n# define NPY_NO_DEPRECATED_API NPY_{major}_{minor}_API_VERSION\n#endif\n"
    if current[0] >= 2:
        header += "#ifndef NPY_TARGET_VERSION\n# define NPY_TARGET_VERSION NPY_2_0_API_VERSION\n#endif\n"
    return header


def install_native_support(imports, *, x2py_dirpath, verbose: bool | int = False) -> tuple[ObjectFile, ...]:
    """Write native binding support and return its explicit compilation inputs."""
    if not any(name == _NATIVE_SUPPORT_IMPORT or name.startswith(f"{_NATIVE_SUPPORT_IMPORT}/") for name in imports):
        return ()

    destination = Path(x2py_dirpath) / _NATIVE_SUPPORT_IMPORT
    if verbose:
        print(f">> Write native support: {destination}")
    with FileLock(str(destination.with_suffix(".lock"))):
        shutil.rmtree(destination, ignore_errors=True)
        shutil.copytree(_NATIVE_SUPPORT_SOURCE, destination)

    (destination / "numpy_version.h").write_text(
        _numpy_version_header(),
        encoding="utf-8",
    )
    return (
        ObjectFile(
            source=destination / "x2py_binding.c",
            object_path=destination / "x2py_binding.o",
            language="c",
            include_dirs=(destination,),
            tools=frozenset({"python"}),
        ),
    )
