"""
This file contains some useful functions to compile the generated fortran code
"""

import os
from pathlib import Path

from filelock import FileLock

from x2py.codegen.printers.fcode import FCodePrinter
from .basic import CompileObj
from .library_config import recognised_libs

# get path to x2py/
x2py_root = Path(__file__).parent.parent

__all__ = ["recompile_object"]


# ==============================================================================
def generate_extension_modules(
    import_key,
    import_node,
    x2py_dirpath,
    compiler,
    include,
    libs,
    libdir,
    dependencies,
    extra_compilation_tools,
    language,
    verbose,
    convert_only,
    installed_libs,
):
    """
    Generate any new modules that describe extensions.

    Generate any new modules that describe extensions. This is the case for lists/
    sets/dicts/etc handled by gFTL.

    Parameters
    ----------
    import_key : str
        The name by which the extension is identified in the import.
    import_node : Import
        The import used in the code generator (this object contains the module to
        be printed).
    x2py_dirpath : str
        The folder where files are being saved.
    compiler : x2py.codegen.compilers.compiling.Compiler
        A compiler that can be used to compile dependencies.
    include : iterable of strs
        Include directories paths.
    libs : iterable of strs
        Required libraries.
    libdir : iterable of strs
        Paths to directories containing the required libraries.
    dependencies : iterable of CompileObjs
        Objects which must also be compiled in order to compile this module/program.
    extra_compilation_tools : iterable of str
        Tools used which require additional compilation flags/include dirs/libs/etc.
    language : str
        The language in which code is being printed.
    verbose : int
        Indicates the level of verbosity.
    convert_only : bool, default=False
        Indicates if the compilation step is required or not.
    installed_libs : dict[str, CompileObj]
        A dictionary containing all the CompileObj objects for all the libraries
        that have already been installed.

    Returns
    -------
    list[CompileObj]
        A list of any new compilation dependencies which are required to compile
        the translated file.
    """
    new_dependencies = []
    lib_name = str(import_key).split("/", 1)[0]
    if lib_name == "gFTL_extensions":
        lib_name = "gFTL"
        mod = import_node.source_module
        filename = os.path.join(x2py_dirpath, import_key) + ".F90"
        folder = os.path.dirname(filename)
        printer = FCodePrinter(filename, verbose=verbose)
        code = printer.doprint(mod)
        if not os.path.exists(folder):
            os.mkdir(folder)
        with FileLock(f"{folder}.lock"), open(filename, "w", encoding="utf-8") as f:
            f.write(code)

        compile_obj = CompileObj(
            os.path.basename(filename),
            folder=folder,
            include=include,
            libs=libs,
            libdir=libdir,
            dependencies=dependencies,
            extra_compilation_tools=extra_compilation_tools,
        )
        new_dependencies.append(compile_obj)
        manage_dependencies(
            {"gFTL": None, "gFTL_functions": None},
            compiler,
            x2py_dirpath,
            new_dependencies[-1],
            language,
            verbose,
            convert_only,
            installed_libs=installed_libs,
        )
        installed_libs.setdefault("gFTL_extensions", {})[import_key] = compile_obj

    return new_dependencies


# ==============================================================================
def recompile_object(compile_obj, compiler, language, verbose=False):
    """
    Compile the provided file if necessary.

    Check if the file has already been compiled, if it hasn't or if the source has
    been modified then compile the file.

    Parameters
    ----------
    compile_obj : CompileObj
        The object to compile.

    compiler : str
        The compiler used.

    language : str
        The language in which code is being printed.

    verbose : int
        Indicates the level of verbosity.
    """

    if not compiler.executes_commands:
        compiler.compile_module(
            compile_obj=compile_obj,
            output_folder=compile_obj.source_folder,
            language=language,
            verbose=verbose,
        )
        return

    # compile library source files
    with compile_obj:
        if os.path.exists(compile_obj.module_target):
            # Check if source file has changed since last compile
            o_file_age = os.path.getmtime(compile_obj.module_target)
            src_file_age = os.path.getmtime(compile_obj.source)
            outdated = o_file_age < src_file_age
        else:
            outdated = True
    if outdated:
        compiler.compile_module(
            compile_obj=compile_obj,
            output_folder=compile_obj.source_folder,
            language=language,
            verbose=verbose,
        )


# ==============================================================================
def manage_dependencies(
    x2py_imports,
    compiler,
    x2py_dirpath,
    mod_obj,
    language,
    verbose,
    convert_only=False,
    installed_libs=None,
):
    """
    Manage dependencies of the code to be compiled.

    Manage dependencies of the code to be compiled.

    Parameters
    ----------
    x2py_imports : dict[str,Import]
        A dictionary describing imports created by X2py that may imply dependencies.
    compiler : x2py.codegen.compilers.compiling.Compiler
        A compiler that can be used to compile dependencies.
    x2py_dirpath : str | Path
        The path in which the X2py output is generated (__x2py__).
    mod_obj : CompileObj | CompileTarget
        The object that we are aiming to copile.
    language : str
        The language in which code is being printed.
    verbose : int
        Indicates the level of verbosity.
    convert_only : bool, default=False
        Indicates if the compilation step is required or not.
    installed_libs : dict[str, CompileObj]
        A dictionary containing all the CompileObj objects for all the libraries
        that have already been installed.
    """
    if installed_libs is None:
        installed_libs = {}

    x2py_dirpath = Path(x2py_dirpath)
    # Iterate over the recognised_libs list and determine if the printer
    # requires a library to be included.
    for lib_name, stdlib in recognised_libs.items():
        if stdlib is None:
            continue
        if any(i == lib_name or i.startswith(f"{lib_name}/") for i in x2py_imports):
            stdlib_obj = stdlib.install_to(x2py_dirpath, installed_libs, verbose, compiler)

            if isinstance(mod_obj, CompileObj):
                mod_obj.add_dependencies(stdlib_obj)

            # stop after copying lib to __x2py__ directory for
            # convert only
            if convert_only:
                continue

    if not convert_only:
        lib_compile_objs = [lib_obj for key, lib_obj in installed_libs.items() if key != "gFTL_extensions"]
        lib_compile_objs.extend(installed_libs.get("gFTL_extensions", {}).values())
        for lib_obj in lib_compile_objs:
            # get the include folder path and library files
            recompile_object(lib_obj, compiler=compiler, language=language, verbose=verbose)

    # Iterate over the imports and determine if the printer
    # requires an extension module to be generated
    for key, import_node in x2py_imports.items():
        deps = generate_extension_modules(
            key,
            import_node,
            x2py_dirpath,
            compiler=compiler,
            include=getattr(mod_obj, "include", ()),
            libs=getattr(mod_obj, "libs", ()),
            libdir=getattr(mod_obj, "libdir", ()),
            dependencies=mod_obj.dependencies,
            extra_compilation_tools=getattr(mod_obj, "extra_compilation_tools", ()),
            language=language,
            verbose=verbose,
            convert_only=convert_only,
            installed_libs=installed_libs,
        )
        if convert_only:
            continue
        if isinstance(mod_obj, CompileObj):
            for d in deps:
                recompile_object(d, compiler=compiler, language=language, verbose=verbose)
                mod_obj.add_dependencies(d)


# ==============================================================================
def get_module_and_compile_dependencies(parser, compile_libs=None, deps=None):
    """
    Get the module (.o files) and compilation dependencies.

    Determine all additional .o files, include folders and libraries required
    to generate the shared library or executable.

    Parameters
    ----------
    parser : Parser
        The parser whose dependencies should be appended.
    compile_libs : list[str], optional
        The libraries (-lX) that should be used for the compilation.
        This argument is used internally but should not be provided
        from an external call to this function.
    deps : dict[str, CompileObj], optional
        A dictionary describing the modules on which this code depends.
        The key is the name of the file containing the module. The value
        is the CompileObj describing the .o file.
        This argument is used internally but should not be provided
        from an external call to this function.

    Returns
    -------
    compile_libs : list[str], optional
        The libraries (-lX) that should be used for the compilation.
    deps : dict[str, CompileObj], optional
        A dictionary describing the modules on which this code depends.
        The key is the name of the file containing the module. The value
        is the CompileObj describing the .o file.
    """
    dep_fname = Path(parser.filename)
    assert compile_libs is None or dep_fname.suffix == ".pyi" or x2py_root in dep_fname.parents
    mod_folder = dep_fname.parent
    mod_base = dep_fname.name

    if compile_libs is None:
        assert deps is None
        compile_libs = []
        deps = {}
    else:
        # Stop conditions
        if parser.metavars.get("module_name", None) == "omp_lib":
            return compile_libs, deps

        if parser.compile_obj:
            deps[dep_fname] = parser.compile_obj
        elif dep_fname not in deps:
            dep_compile_includes = [mod_folder / i for i in parser.metavars.get("includes", "").split(",") if i]
            dep_compile_libdirs = [
                mod_folder / libdir for libdir in parser.metavars.get("libdirs", "").split(",") if libdir
            ]
            dep_compile_libs = [library for library in parser.metavars.get("libraries", "").split(",") if library]
            if not parser.metavars.get("ignore_at_import", False):
                is_header_only = dep_fname.suffix == ".pyi" and parser.original_filename.suffix != ".py"
                deps[dep_fname] = CompileObj(
                    mod_base,
                    folder=mod_folder,
                    include=dep_compile_includes,
                    libs=dep_compile_libs,
                    libdir=dep_compile_libdirs,
                    has_target_file=not is_header_only,
                )
            else:
                compile_libs.extend(dep_compile_libs)

    # Proceed recursively
    for son in parser.sons:
        get_module_and_compile_dependencies(son, compile_libs, deps)

    return compile_libs, deps
