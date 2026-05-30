# Compiler Preprocessing Implementation for x2py

## Summary
Implemented `x2py/preprocessing.py` module that provides compiler-based preprocessing for both Fortran and C code. This solves the issue of handling includes in both parsers by leveraging the actual compiler's preprocessor.

## Key Components

### 1. PreprocessingRecipe (Dataclass)
- Metadata about how a source file was preprocessed
- Tracks: language, compiler, mode, include dirs, defines, undefs, std, compiler args, source file
- Can be serialized to JSON for reporting

### 2. PreprocessingConfig (Dataclass)
- Configuration for preprocessing operations
- Supports both "internal" (lightweight) and "compiler" (full preprocessing) modes
- Methods:
  - `uses_compiler`: Check if compiler preprocessing is enabled
  - `fortran_macro_defines()`: Extract macros for Fortran parser
  - `fortran_internal_recipe()`: Generate recipe metadata for internal mode

### 3. Core Functions

#### `validate_macro_name(macro_str, context)`
- Validates macro definitions have valid identifiers
- Prevents invalid macro syntax

#### `_get_compiler_for_language(language, compiler)`
- Determines which compiler to use (gfortran for Fortran, gcc for C)
- Respects user-specified compiler path

#### `_build_preprocessor_flags(config, language)`
- Builds compiler command-line flags:
  - `-E` flag for preprocessing only
  - Include directories (`-I`)
  - Macro definitions (`-D`)
  - Macro undefs (`-U`)
  - Language standard (`-std`)
  - Custom compiler arguments

#### `run_compiler_preprocessor_with_recipe(source_path, language, config)`
- Main entry point for preprocessing
- Runs the compiler with `-E` flag to:
  - Resolve all `#include` (C) and `include` (Fortran) statements
  - Expand all macros with provided defines/undefs
  - Handle include paths from `-I` flags
- Returns both:
  - Preprocessed source code (ready for parser)
  - Preprocessing recipe (metadata about the operation)
- Error handling:
  - Checks if compiler exists in PATH
  - Validates compiler exit code
  - Provides helpful error messages
  - Timeout protection (60 seconds)

## How It Works

### Workflow for Fortran
1. User calls parser with `--preprocess compiler --compiler gfortran-12 -I include -D USE_MPI`
2. `PreprocessingConfig` is created with these settings
3. `run_compiler_preprocessor_with_recipe()` is called
4. `gfortran-12 -E -I include -D USE_MPI=1 source.f90` is executed
5. Compiler:
   - Resolves all `include "file.inc"` statements
   - Expands `USE_MPI` macro in the code
   - Outputs fully expanded source
6. Preprocessed source is fed to Fortran parser
7. Parser now has complete type information from includes
8. Recipe metadata is attached to the parsed output

### Workflow for C
1. Similar to Fortran but uses `gcc` or `clang`
2. `gcc -E -I include -D API_EXPORT= source.h` is executed
3. Compiler:
   - Resolves all `#include "header.h"` and `#include <system.h>`
   - Expands macros like `API_EXPORT`
   - Outputs fully expanded C code
4. Preprocessed source is fed to C parser
5. Parser has access to all type definitions from headers

## Integration with Existing x2py Code

The module is already imported in `x2py/cli.py` (lines 20-25):
```python
from x2py.preprocessing import (
    PreprocessingConfig,
    PreprocessingError,
    run_compiler_preprocessor_with_recipe,
    validate_macro_name,
)
```

It's actively used in:
- `_fortran_source_for_path()`: Preprocesses Fortran sources
- `_c_source_loader()`: Preprocesses C sources
- `_build_preprocessing_config()`: Validates and builds config
- CLI argument parsing: Handles `--preprocess`, `--compiler`, `-I`, `-D`, `-U`, `--std`

## Example Usage

### Command Line (Fortran)
```bash
python -m x2py mycode.f90 --parse --preprocess compiler --compiler gfortran-12 -I ./include -D USE_MPI
```

### Command Line (C)
```bash
python -m x2py api.h --language c --parse --preprocess compiler --compiler gcc-13 -I ./include -D API_EXPORT=
```

### Programmatic (Python)
```python
from pathlib import Path
from x2py.preprocessing import PreprocessingConfig, run_compiler_preprocessor_with_recipe

config = PreprocessingConfig(
    mode="compiler",
    compiler="gfortran-12",
    include_dirs=["./include"],
    defines=["USE_MPI"],
)

source, recipe = run_compiler_preprocessor_with_recipe(
    Path("mycode.f90"),
    language="fortran",
    config=config,
)

print(f"Preprocessed with: {recipe.compiler}")
print(source)  # Fully expanded source with all includes resolved
```

## Benefits

1. **Complete Macro Expansion**: Uses the compiler's actual preprocessor, ensuring correct macro behavior
2. **Include Resolution**: All `#include` and `include` statements are fully resolved
3. **Standard Compliance**: Respects language standards (C99, C11, F95, F2008, etc.)
4. **Flexible**: Supports custom compiler paths, flags, and compile_commands.json
5. **Metadata Tracking**: Records how preprocessing was done for reproducibility
6. **Error Handling**: Clear error messages when compiler is not found or preprocessing fails
7. **Works with Both Languages**: Same API for Fortran and C preprocessing

## What Happens to Include Files

When the compiler preprocesses code with includes:
- `include "file.inc"` or `#include "file.h"` statements are replaced with the actual contents of those files
- All macros in included files are expanded
- Line markers (`#line` directives) are inserted to track original locations
- The wrapper can now parse the complete, expanded code

## Status
✅ Implementation complete on branch `feature/compiler-preprocessing`
✅ Ready for integration into Fortran and C parsers
✅ Integration already exists in x2py/cli.py
✅ All CLI flags and error handling implemented
