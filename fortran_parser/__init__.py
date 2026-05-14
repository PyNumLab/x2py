# -*- coding: utf-8 -*-
from .models import FortranArgument, FortranBlockData, FortranDerivedType, FortranFile, FortranInterface, FortranModule, FortranParseError, FortranProcedureSignature, FortranProgram, FortranProject, FortranSubmodule
from .parser import FortranParser, parse_fortran_file, parse_fortran_project, collect_signature_shape_symbols, evaluate_signature_shapes

_DEFAULT = FortranParser()

def parse_fortran_signatures(code, filename=None, macro_defines=None):
    return _DEFAULT.parse_signatures(code, filename=filename, macro_defines=macro_defines)

def parse_fortran_project_signatures(files):
    return _DEFAULT.parse_project_signatures(files)

def parse_fortran_signature(code, filename=None, macro_defines=None):
    return _DEFAULT.parse_signature(code, filename=filename, macro_defines=macro_defines)

def parse_fortran_types(code, filename=None):
    return _DEFAULT.parse_types(code, filename=filename)

def parse_fortran_derived_type(code, filename=None):
    return _DEFAULT.parse_derived_type(code, filename=filename)

def parse_fortran_modules(code, filename=None):
    return _DEFAULT.parse_modules(code, filename=filename)

def parse_fortran_module(code, filename=None):
    return _DEFAULT.parse_module(code, filename=filename)

def parse_fortran_interfaces(code, filename=None):
    return _DEFAULT.parse_interfaces(code, filename=filename)

def parse_fortran_interface(code, filename=None):
    return _DEFAULT.parse_interface(code, filename=filename)

def parse_fortran_submodules(code, filename=None):
    return _DEFAULT.parse_submodules(code, filename=filename)

def parse_fortran_submodule(code, filename=None):
    return _DEFAULT.parse_submodule(code, filename=filename)

def parse_fortran_programs(code, filename=None):
    return _DEFAULT.parse_programs(code, filename=filename)

def parse_fortran_program(code, filename=None):
    return _DEFAULT.parse_program(code, filename=filename)

def parse_fortran_block_data(code, filename=None):
    return _DEFAULT.parse_block_data(code, filename=filename)

def parse_fortran_block_data_unit(code, filename=None):
    return _DEFAULT.parse_block_data_unit(code, filename=filename)

def parse_fortran_namespace(root, extensions=(".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08")):
    return _DEFAULT.parse_namespace(root, extensions=extensions)

def assess_wrap_readiness(code, filename=None):
    return _DEFAULT.assess_wrap_readiness(code, filename=filename)

__all__ = [k for k in globals() if k.startswith('Fortran') or k.startswith('parse_fortran') or k in {'assess_wrap_readiness','collect_signature_shape_symbols','evaluate_signature_shapes'}]
