# Handle includes in Fortran and C parsers - Preprocess before parsing

## Problem
The current parsing approach does not handle include files. When parsing Fortran and C code, included files need to be exposed to the wrapper because:
- Include files contain important declarations and definitions that affect the parsed code
- The wrapper needs access to all included files, not just the main file being parsed
- Without including these files, the wrapper won't have complete information about the exposed API

## Solution
Consider implementing a preprocessing step before parsing:
1. Resolve all `#include` (C) and `include` (Fortran) statements
2. Locate and read the include files
3. Preprocess the code to expand includes
4. Then perform the actual parsing on the complete, preprocessed code

This ensures the parser has access to all necessary declarations and definitions from included files.

## Impact
- Improves accuracy of the parsing
- Ensures the wrapper has complete information about the exposed API
- Handles complex dependencies between header/include files

## Labels
- `enhancement`
- `parser`
- `fortran`
- `c`
