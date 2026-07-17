"""Install the bundled native runtime used by generated CPython wrappers."""

from pathlib import Path
import shutil

from filelock import FileLock
import numpy as np

import x2py.stdlib as stdlib_folder

from .objects import ObjectFile


_RUNTIME_IMPORT = "x2py_runtime"
_RUNTIME_SOURCE = Path(stdlib_folder.__file__).parent / _RUNTIME_IMPORT


def _numpy_version_header() -> str:
    """Return NumPy API version guards for the bundled native runtime."""
    maximum_supported = [1, 19]
    current = [int(value) for value in np.version.version.split(".")[:2]]
    major, minor = min(maximum_supported, current)
    header = f"#ifndef NPY_NO_DEPRECATED_API\n# define NPY_NO_DEPRECATED_API NPY_{major}_{minor}_API_VERSION\n#endif\n"
    if current[0] >= 2:
        header += "#ifndef NPY_TARGET_VERSION\n# define NPY_TARGET_VERSION NPY_2_0_API_VERSION\n#endif\n"
    return header


def install_runtime_support(imports, *, x2py_dirpath, verbose: bool | int = False) -> tuple[ObjectFile, ...]:
    """Write runtime support and return its explicit compilation inputs."""
    if not any(name == _RUNTIME_IMPORT or name.startswith(f"{_RUNTIME_IMPORT}/") for name in imports):
        return ()

    destination = Path(x2py_dirpath) / _RUNTIME_IMPORT
    if verbose:
        print(f">> Write runtime support: {destination}")
    with FileLock(str(destination.with_suffix(".lock"))):
        shutil.rmtree(destination, ignore_errors=True)
        shutil.copytree(_RUNTIME_SOURCE, destination)

    (destination / "numpy_version.h").write_text(
        _numpy_version_header(),
        encoding="utf-8",
    )
    return (
        ObjectFile(
            source=destination / "python_runtime.c",
            object_path=destination / "python_runtime.o",
            language="c",
            include_dirs=(destination,),
            tools=frozenset({"python"}),
        ),
    )
