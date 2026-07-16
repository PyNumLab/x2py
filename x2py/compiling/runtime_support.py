"""Install the bundled native runtime used by generated CPython wrappers."""

from pathlib import Path
import shutil

from filelock import FileLock
import numpy as np

import x2py.stdlib as stdlib_folder

from .basic import CompileObj


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


def install_runtime_support(imports, *, x2py_dirpath, compiler, wrapper_obj, language, verbose):
    """Copy, register, and compile runtime support imported by one wrapper."""
    if not any(name == _RUNTIME_IMPORT or name.startswith(f"{_RUNTIME_IMPORT}/") for name in imports):
        return

    destination = Path(x2py_dirpath) / _RUNTIME_IMPORT
    with FileLock(str(destination.with_suffix(".lock"))):
        shutil.rmtree(destination, ignore_errors=True)
        if verbose:
            print(f">> Copying {_RUNTIME_SOURCE} to {destination}")
        shutil.copytree(_RUNTIME_SOURCE, destination)

    (destination / "numpy_version.h").write_text(
        _numpy_version_header(),
        encoding="utf-8",
    )
    runtime_obj = CompileObj(
        "python_runtime.c",
        destination,
        include=(destination,),
        extra_compilation_tools=("python",),
    )
    wrapper_obj.add_dependencies(runtime_obj)
    compiler.compile_module(
        compile_obj=runtime_obj,
        output_folder=destination,
        language=language,
        verbose=verbose,
    )
