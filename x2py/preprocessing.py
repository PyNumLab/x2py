"""Compiler preprocessing module for x2py.

This module provides compiler-based preprocessing for both Fortran and C code,
resolving includes and expanding macros using the actual compiler preprocessor.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class PreprocessingError(Exception):
    """Raised when preprocessing configuration or execution fails."""
    pass


@dataclass
class PreprocessingRecipe:
    """Metadata about how a source file was preprocessed."""
    language: str
    compiler: str
    mode: str = "compiler"
    include_dirs: list[str] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)
    undefs: list[str] = field(default_factory=list)
    std: Optional[str] = None
    compiler_args: list[str] = field(default_factory=list)
    source_file: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "language": self.language,
            "compiler": self.compiler,
            "mode": self.mode,
            "include_dirs": self.include_dirs,
            "defines": self.defines,
            "undefs": self.undefs,
            "std": self.std,
            "compiler_args": self.compiler_args,
            "source_file": self.source_file,
        }


@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing operations."""
    mode: str = "internal"  # "internal" or "compiler"
    compiler: Optional[str] = None
    compile_commands: Optional[str] = None
    include_dirs: list[str] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)
    undefs: list[str] = field(default_factory=list)
    std: Optional[str] = None
    compiler_args: list[str] = field(default_factory=list)
    
    @property
    def uses_compiler(self) -> bool:
        """True if compiler-based preprocessing is configured."""
        return self.mode == "compiler"
    
    def fortran_macro_defines(self) -> dict[str, int | str] | None:
        """Extract macro defines for Fortran parser (internal mode only)."""
        if self.uses_compiler:
            return None
        
        if not self.defines and not self.undefs:
            return None
        
        result = {}
        for define in self.defines:
            if "=" in define:
                name, value = define.split("=", 1)
                result[name] = value
            else:
                result[define] = 1
        return result if result else None
    
    def fortran_internal_recipe(self, path: Path) -> dict[str, object] | None:
        """Generate a recipe dict for Fortran internal preprocessing."""
        if self.uses_compiler:
            return None
        
        recipe = PreprocessingRecipe(
            language="fortran",
            compiler="internal",
            mode="internal",
            defines=self.defines,
            undefs=self.undefs,
            source_file=str(path),
        )
        return recipe.to_dict()


def validate_macro_name(macro_str: str, context: str) -> None:
    """Validate that a macro definition has a valid name."""
    if not macro_str:
        raise PreprocessingError(f"{context}: empty macro definition")
    
    # Extract name part (before = if present)
    name = macro_str.split("=", 1)[0]
    
    # Check valid C/Fortran identifier
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        raise PreprocessingError(
            f"{context}: invalid macro name '{name}'; must be a valid identifier"
        )


def _get_compiler_for_language(language: str, compiler: Optional[str]) -> str:
    """Determine the compiler to use based on language."""
    if compiler:
        return compiler
    
    if language == "fortran":
        return "gfortran"
    elif language == "c":
        return "gcc"
    else:
        raise PreprocessingError(f"Unknown language: {language}")


def _build_preprocessor_flags(
    config: PreprocessingConfig,
    language: str,
) -> list[str]:
    """Build compiler preprocessor flags from configuration."""
    flags = []
    
    # Add preprocessing flag first
    flags.append("-E")  # Preprocess only, no compilation
    
    # Add include directories
    for include_dir in config.include_dirs:
        flags.append(f"-I{include_dir}")
    
    # Add defines
    for define in config.defines:
        if "=" in define:
            flags.append(f"-D{define}")
        else:
            flags.append(f"-D{define}=1")
    
    # Add undefs
    for undef in config.undefs:
        flags.append(f"-U{undef}")
    
    # Add standard flag if provided
    if config.std:
        flags.append(f"-std={config.std}")
    
    # Add raw compiler args
    flags.extend(config.compiler_args)
    
    return flags


def run_compiler_preprocessor_with_recipe(
    source_path: Path,
    language: str,
    config: PreprocessingConfig,
) -> tuple[str, PreprocessingRecipe]:
    """Run compiler preprocessor on a source file, returning preprocessed code and recipe.
    
    Args:
        source_path: Path to the source file
        language: "fortran" or "c"
        config: Preprocessing configuration
        
    Returns:
        Tuple of (preprocessed_source_code, preprocessing_recipe)
        
    Raises:
        PreprocessingError: If preprocessing fails
    """
    if not config.uses_compiler:
        raise PreprocessingError("Compiler preprocessing not configured")
    
    compiler = _get_compiler_for_language(language, config.compiler)
    
    # Build preprocessor command
    flags = _build_preprocessor_flags(config, language)
    command = [compiler] + flags + [str(source_path)]
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        raise PreprocessingError(
            f"Compiler not found: {compiler}\n"
            f"Ensure {compiler} is installed and in your PATH"
        )
    except subprocess.TimeoutExpired:
        raise PreprocessingError(f"Compiler preprocessing timed out after 60 seconds")
    except Exception as e:
        raise PreprocessingError(f"Failed to run preprocessor: {e}")
    
    if result.returncode != 0:
        raise PreprocessingError(
            f"Compiler preprocessing failed with exit code {result.returncode}\n"
            f"Command: {' '.join(command)}\n"
            f"Error output:\n{result.stderr}"
        )
    
    # Create recipe for this preprocessing operation
    recipe = PreprocessingRecipe(
        language=language,
        compiler=compiler,
        mode="compiler",
        include_dirs=config.include_dirs,
        defines=config.defines,
        undefs=config.undefs,
        std=config.std,
        compiler_args=config.compiler_args,
        source_file=str(source_path),
    )
    
    return result.stdout, recipe
