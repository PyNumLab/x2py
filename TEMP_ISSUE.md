# Handle includes in Fortran and C parsers - Use compiler preprocessing

## Problem
The current parsing approach does not handle include files. When parsing Fortran and C code, included files need to be exposed to the wrapper because:
- Include files contain important declarations and definitions that affect the parsed code
- The wrapper needs access to all included files, not just the main file being parsed
- Without including these files, the wrapper won't have complete information about the exposed API

## Solution
Use the compiler's preprocessing step before parsing:
1. Call the compiler (e.g., `gcc -E` for C, `gfortran -E` for Fortran) with all necessary compilation flags
2. The compiler will preprocess the code, resolving all `#include` (C) and `include` (Fortran) statements
3. Capture the preprocessed output
4. Parse the preprocessed result, which now contains all expanded includes and definitions

This approach ensures we have complete information without reimplementing the preprocessor logic.

## Implementation Details
- For **C**: Use `gcc -E` or `clang -E` with appropriate flags (include paths, defines, etc.)
- For **Fortran**: Use `gfortran -E` or similar with appropriate flags
- Pass user-provided compiler flags to ensure correct preprocessing (e.g., `-I`, `-D`, etc.)
- Capture and parse the preprocessed output

## Impact
- Improves accuracy of the parsing
- Ensures the wrapper has complete information about the exposed API
- Handles complex dependencies between header/include files
- Leverages existing compiler preprocessing (no need to reimplement)

## Labels
- `enhancement`
- `parser`
- `fortran`
- `c`
