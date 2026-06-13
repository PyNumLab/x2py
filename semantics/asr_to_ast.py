import os
import argparse
import subprocess
import numpy as np

from codegen.printers.fcode    import FCodePrinter
from codegen.printers.ccode    import CCodePrinter
from codegen.printers.pycode   import PythonCodePrinter
from codegen.models.core       import FunctionDef, Interface, ClassDef, Module, EmptyNode, FunctionDefArgument, ModuleHeader, FunctionDefResult, Nil
from codegen.models.datatypes  import PrimitiveComplexType
from codegen.models.datatypes  import original_type_to_pyccel_type
from codegen.models.datatypes  import typenames_to_dtypes
from codegen.models.core       import Variable
from codegen.scope             import Scope
from compiling.basic           import CompileObj
from compiling.compilers       import Compiler, get_condaless_search_path
from compiling.python_wrapper  import create_shared_library
from compiling.utilities       import manage_dependencies
from semantics                 import models
from x2py                      import SEMANTIC_DTYPE_TO_NUMPY_DTYPE

conda_warnings = 'verbose'
Compiler.acceptable_bin_paths = get_condaless_search_path(conda_warnings)
src_compiler = Compiler('GNU', 'fortran')
wrapper_compiler = Compiler('GNU', 'c')



#==============================================================
#==============================================================
#==============================================================

_extension_registry = {'fortran': 'f90', 'c':'c',  'python':'py'}
_header_extension_registry = {'fortran': None, 'c':'h',  'python':None}
printer_registry    = {
                        'fortran':FCodePrinter,
                        'c':CCodePrinter,
                        'python':PythonCodePrinter
                      }

class Codegen(object):

    """Abstract class for code generator."""

    def __init__(self, name, ast, scope):
        """Constructor for Codegen.

        parser: pyccel parser


        name: str
            name of the generated module or program.
        """

        self._name     = name
        self._scope    = scope
        self._ast      = ast
        self._printer  = None
        self._language = None

        #TODO verify module name != function name
        #it generates a compilation error

        self._stmts = {}
        _structs = [
            'imports',
            'body',
            'routines',
            'classes',
            'modules',
            'variables',
            'interfaces',
            ]
        for key in _structs:
            self._stmts[key] = []

        self._collect_statements()
        self._is_program = self.ast.program is not None


    @property
    def name(self):
        """Returns the name associated to the source code"""

        return self._name

    @property
    def scope(self):
        """Returns the name associated to the source code"""

        return self._scope

    @property
    def imports(self):
        """Returns the imports of the source code."""

        return self._stmts['imports']

    @property
    def variables(self):
        """Returns the variables of the source code."""

        return self._stmts['variables']

    @property
    def body(self):
        """Returns the body of the source code, if it is a Program or Module."""

        return self._stmts['body']

    @property
    def routines(self):
        """Returns functions/subroutines."""

        return self._stmts['routines']

    @property
    def classes(self):
        """Returns the classes if Module."""

        return self._stmts['classes']

    @property
    def interfaces(self):
        """Returns the interfaces."""

        return self._stmts['interfaces']

    @property
    def modules(self):
        """Returns the modules if Program."""

        return self._stmts['modules']

    @property
    def is_program(self):
        """Returns True if a Program."""

        return self._is_program

    @property
    def ast(self):
        """Returns the AST."""

        return self._ast

    @property
    def language(self):
        """Returns the used language"""

        return self._language

    def set_printer(self, **settings):
        """ Set the current codeprinter instance"""
        # Get language used (default language used is fortran)
        language = settings.pop('language', 'fortran')

        # Set language
        if not language in ['fortran', 'c', 'python']:
            raise ValueError('{} language is not available'.format(language))
        self._language = language

        # instantiate codePrinter
        code_printer = printer_registry[language]
        # set the code printer
        self._printer = code_printer(self.name, **settings)

    def get_printer_imports(self):
        """return the imports of the current codeprinter"""
        return self._printer.get_additional_imports()

    def _collect_statements(self):
        """Collects statements and split them into routines, classes, etc."""

        scope  = self.scope

        funcs      = []
        interfaces = []


        for i in scope.functions.values():
            if isinstance(i, FunctionDef) and not i.is_header:
                funcs.append(i)
            elif isinstance(i, Interface):
                interfaces.append(i)

        self._stmts['imports'   ] = list(scope.imports['imports'].values())
        self._stmts['variables' ] = list(self.scope.variables.values())
        self._stmts['routines'  ] = funcs
        self._stmts['classes'   ] = list(scope.classes.values())
        self._stmts['interfaces'] = interfaces
        self._stmts['body']       = self.ast

    def doprint(self, **settings):
        """Prints the code in the target language."""
        if not self._printer:
            self.set_printer(**settings)
        return self._printer.doprint(self.ast)


    def export(self, **settings):
        """Export code in filename"""
        self.set_printer(**settings)
        ext = _extension_registry[self._language]
        header_ext = _header_extension_registry[self._language]

        filename = self.name
        header_filename = '{name}.{ext}'.format(name=filename, ext=header_ext)
        filename = '{name}.{ext}'.format(name=filename, ext=ext)

        # print module header
        if header_ext is not None:
            code = self._printer.doprint(ModuleHeader(self.ast))
            with open(header_filename, 'w') as f:
                for line in code:
                    f.write(line)

        # print module
        code = self._printer.doprint(self.ast)
        with open(filename, 'w') as f:
            for line in code:
                f.write(line)

        # print program
        prog_filename = None
        if self.is_program and self.language != 'python':
            folder = os.path.dirname(filename)
            fname  = os.path.basename(filename)
            prog_filename = os.path.join(folder,"prog_"+fname)
            code = self._printer.doprint(self.ast.program)
            with open(prog_filename, 'w') as f:
                for line in code:
                    f.write(line)

        return filename, prog_filename

#==============================================================
#==============================================================
#==============================================================
np_type = lambda dtype: getattr(np, dtype.removeprefix("numpy."))

def compile_module(comp, compile_obj, output_folder, verbose = False):
    """
    Compile a module.

    Compile a file containing a module to a .o file.

    Parameters
    ----------
    compile_obj : CompileObj
        Object containing all information about the object to be compiled.

    output_folder : str
        The folder where the result should be saved.

    verbose : bool
        Indicates whether additional output should be shown.
    """

    comp._language_info = comp._compiler_info['fortran']
    accelerators = compile_obj.extra_compilation_tools

    # Get flags
    flags = comp._get_flags(compile_obj.flags, accelerators)
    flags.append('-c')

    # Get includes
    includes  = comp._get_include(compile_obj.include, accelerators)
    inc_flags = comp._insert_prefix_to_list(includes, '-I')

    # Get executable
    exec_cmd = comp.get_exec(accelerators)

    cmd = [exec_cmd, *flags, *inc_flags,
            compile_obj.source, '-o', compile_obj.module_target]

    with compile_obj:
        p = run_command(cmd, verbose)
    return p

def run_command(cmd, verbose):
    """
    Run the provided command and collect the output.

    Run the provided compilation command, collect the output and raise any
    necessary errors if the file does not compile.

    Parameters
    ----------
    cmd : list of str
        The command to run.
    verbose : bool
        Indicates whether additional output should be shown.

    Returns
    -------
    str
        The exact command that was run.

    Raises
    ------
    RuntimeError
        Raises `RuntimeError` if the file does not compile.
    """
    cmd = [os.path.expandvars(c) for c in cmd]
    if verbose:
        print(' '.join(cmd))

    process =  subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return process

def terminat(process, verbose):
    out, err = process.communicate()

    if verbose and out:
        print(out)
    if p.returncode != 0:
        err_msg = "Failed to build module"
        err_msg += "\n" + err
        raise RuntimeError(err_msg)
    if err:
        warnings.warn(UserWarning(err))

#==============================================================

def asr_to_ast(node, scope, legacy):
    if isinstance(node, models.SemanticModule):
        funcs = [asr_to_ast(a, scope, legacy) for a in node.functions]
        decs = [asr_to_ast(a, scope, legacy) for a in node.variables]
        name = node.name
        name  = scope.get_new_name(name)
        return Module(name, decs, funcs, scope=scope)
    elif isinstance(node, models.SemanticFunction):
        func_scope = scope.new_child_scope(name=node.name, scope_type='function')
        decls    = [asr_to_ast(a, func_scope, legacy) for a in node.arguments]
        if node.return_type:
            return_dtype = node.return_type
            return_rank  = return_dtype.rank
            return_dtype = original_type_to_pyccel_type[np_type(SEMANTIC_DTYPE_TO_NUMPY_DTYPE[return_dtype.dtype])]        
            results  = Variable(return_dtype, node.name)
            scope.insert_variable(results, name=node.name)
            result   = FunctionDefResult(results)
        else:
            result = FunctionDefResult(Nil())

        args     = [FunctionDefArgument(i) for i in decls]
        name     = scope.get_new_name(node.name)
        func     = FunctionDef(name, args, [], result, scope=func_scope, is_external=legacy)
        scope._locals['functions'][name] = func
        return func
    elif isinstance(node, models.SemanticVariable):
        dtype = node.semantic_type
        rank  = dtype.rank
        dtype = original_type_to_pyccel_type[np_type(SEMANTIC_DTYPE_TO_NUMPY_DTYPE[dtype.dtype])]
        name  = node.name
#        shape = asr_to_ast(node.shape, scope) if node.shape else None
        var   = Variable(dtype, name)
        scope.insert_variable(var, name=name)
        return var
    else:
        raise NotImplementedError(type(node))

#==============================================================
if __name__ == '__main__':
    verbose = True

    from pathlib import Path

    from x2py import parse_fortran_file
    from semantics.fortran2ir import fortran_file_to_semantic_modules
    from x2py.preprocessing import PreprocessingConfig, preprocess_source

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    filename = args.filename
    path     = Path(filename)
    preprocessed = preprocess_source(
        path,
        language="fortran",
        config=PreprocessingConfig(
            mode="compiler",
            compiler="gfortran",
            defines=[],
            include_dirs=[],
        ),
    )

    parsed = parse_fortran_file(preprocessed.source, filename=str(path))
    modules = fortran_file_to_semantic_modules(parsed)
    assert len(modules) == 1
    module = modules[0]
    name   = module.name

    scope  = Scope(name=name, scope_type='module')
    mod    = asr_to_ast(module, scope, legacy=str(path).endswith('f'))

    dependency = CompileObj(file_name=os.path.basename(filename), folder=os.path.dirname(filename), has_target_file=True)
    p          = compile_module(src_compiler, compile_obj=dependency, output_folder=os.getcwd(), verbose=verbose)

    terminat(p, verbose=verbose)

    codegen = Codegen(name, mod, mod.scope)
    mod_obj = CompileObj(file_name=name, folder=os.path.dirname(filename), has_target_file=False)

    # Create shared library
    generated_filepath, shared_lib_timers = create_shared_library(codegen,
                                                                  mod_obj,
                                                                  language='fortran',
                                                                  wrapper_flags ='',
                                                                  pyccel_dirpath=os.getcwd(),
                                                                  output_dirpath=os.getcwd(),
                                                                  compiler=src_compiler,
                                                                  sharedlib_modname=name,
                                                                  dependencies=(dependency,),
                                                                  verbose=True)

