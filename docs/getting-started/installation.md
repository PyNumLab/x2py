---
title: Installation
audience: users, contributors
prerequisites: Python 3.10 or newer, repository checkout
related: verification.md, ../troubleshooting/installation-issues.md, ../developer-guide/quality-assurance.md
status: maintained
---

# Installation

x2py is currently installed from a source checkout. A runtime wrapper build
needs both the Python package and a native GNU toolchain.

## Supported Python Versions

The package metadata requires Python 3.10 or newer. GitHub Actions currently
tests Python 3.10, 3.11, and 3.12 on Ubuntu 24.04. A newer Python may satisfy
the package constraint but is not part of the current CI matrix.

Check the interpreter before creating the environment:

```bash
python3 --version
```

## Native Prerequisites

Install these before attempting a wrapper build:

- GNU Fortran (`gfortran`) for preprocessing, type probes, and native builds;
- Python development headers matching the active interpreter;
- NumPy, whose installed package supplies the required development files;
- a native linker supplied by the compiler toolchain.

<!-- X2PY_C_DOCS_START
- GNU C (`gcc`) for the generated CPython binding;
- NumPy, whose Python package supplies the required C headers; and
X2PY_C_DOCS_END -->

GNU Make is optional. Direct builds do not require it. The generated Makefile
workflow is an advanced build mode that expects GNU Make and a POSIX-style
shell.

On Ubuntu or Debian, the prerequisite packages normally come from:

```bash
sudo apt-get update
sudo apt-get install build-essential gfortran python3-dev
```

<!-- X2PY_C_DOCS_START
```bash
sudo apt-get update
sudo apt-get install gcc gfortran python3-dev
```
X2PY_C_DOCS_END -->

The checked CI target uses Ubuntu 24.04 and `gfortran-13`. Package names and
compiler locations differ on other Linux distributions.

## User Installation

Create an isolated environment from the repository root and install the
checkout in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

The installation pulls the runtime Python dependencies declared by the
project, including NumPy, `filelock`, and `immutabledict`.

## Contributor Installation

Contributors should install the optional QA dependencies as well:

```bash
python3 -m pip install -e ".[qa]"
```

The `qa` extra includes pytest, coverage, Hypothesis, Ruff, Bandit, Vulture,
and Radon. These tools are not required merely to import x2py or build a wrapper.

## Header And Compiler Checks

Verify that the active environment can locate its development headers:

```bash
python3 -c "import sysconfig; print(sysconfig.get_path('include'))"
python3 -c "import numpy; print(numpy.get_include())"
```

Verify the compiler executables independently:

```bash
gfortran --version
```

<!-- X2PY_C_DOCS_START
```bash
gfortran &#45;&#45;version
gcc &#45;&#45;version
```
X2PY_C_DOCS_END -->

Continue with [Verification](verification.md) only after these commands succeed
and the printed header directories exist.

## Platform Caveats

| Platform | Current status |
| --- | --- |
| Ubuntu Linux | CI-verified with Ubuntu 24.04, Python 3.10-3.12, and `gfortran-13`. |
| Other Linux distributions | Expected to require equivalent GNU compilers and development headers; package names and ABI details are not CI-verified. |
| macOS | Not in the current wrapper CI matrix. Compiler discovery, extension suffixes, linker flags, and runtime library paths need platform validation. |
| Windows | Not in the current wrapper CI matrix. The direct GNU/POSIX build assumptions and generated Makefile workflow are not established as supported. |

Do not interpret successful contract-generation or diagnostic commands as proof
that the native wrapper toolchain works on an unverified platform.

## Evidence And Troubleshooting

Dependency and version declarations live in
[`pyproject.toml`](../../pyproject.toml). The current CI environment is defined
in [`.github/workflows/quality.yml`](../../.github/workflows/quality.yml), and
the compiler/header configuration is exercised by
[`test_runtime_abi.py`](../../tests/wrapper/fortran/build_from_source/test_runtime_abi.py).

For missing packages, headers, or virtual-environment problems, start with
[Installation Issues](../troubleshooting/installation-issues.md). For compiler
discovery or linking problems, use
[Compiler Issues](../troubleshooting/compiler-issues.md).
