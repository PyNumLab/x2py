"""
Module containing the `create_shared_library` function which creates a CPython
extension module. This is a shared library which can be called from Python. It
is created from a `CodePrinter` object describing code which has been printed
in a target language.
"""

import os
import time

from .basic import CompileObj
from .runtime_support import install_runtime_support
from x2py.codegen.binding_pipeline import BindingPipeline

__all__ = ["create_shared_library"]


def _print_verbose_timing(verbose, label, elapsed):
    """Print one elapsed build-stage timing when verbose output is enabled."""
    if verbose:
        print(f">> Timing :: {label}: {elapsed:.3f}s")


# ==============================================================================
def create_shared_library(
    codegen,
    main_obj,
    *,
    language,
    wrapper_flags,
    x2py_dirpath,
    output_dirpath,
    compiler,
    sharedlib_modname=None,
    dependencies=(),
    verbose,
):
    """
    Create a shared library which can be called from X2py.

    From a CodePrinter object describing code which has been printed
    in a target language, create a shared library which can be
    called from X2py. In order to do this the code must be wrapped.
    First, if the code is not written in C, it must be wrapped to
    make it callable from C. This intermediary code is printed
    and compiled. From the C-compatible code a second (first for C)
    wrapper is created which exposes the C code to Python. This
    is done via the CWrapper. Finally this new code is compiled
    to generate the required shared language.

    Parameters
    ----------
    codegen : x2py.codegen.printing.codeprinter.CodePrinter
        The printer which was used to print the translated code.

    main_obj : x2py.codegen.compiling.basic.CompileObj
        The compile object which describes the translated code.

    language : str
        The language which X2py translated to.

    wrapper_flags : iterable
        Any additional flags which should be used to compile the wrapper.

    x2py_dirpath : str
        The path to the directory where the files are created and compiled.

    output_dirpath : str
        Path to the directory where the shared library should be outputted.

    compiler : x2py.codegen.compiling.compilers.Compiler
        The compiler which should be used to compile the library.

    sharedlib_modname : str, default: None
        The name of the shared library. The default is the name of the
        module printed by the printer.

    verbose : int
        Indicates the level of verbosity.

    Returns
    -------
    sharedlib_filepath : str
        The absolute path to the shared library which was created.

    timings : dict
        The time spent in the different parts of the library creation.
    """
    timings = {}

    # Get module name
    module_name = codegen.name

    # Name of shared library
    if sharedlib_modname is None:
        sharedlib_modname = module_name

    gen = BindingPipeline(codegen, module_name, language, verbose)

    # -------------------------------------------
    #               Wrap code
    # -------------------------------------------

    start_wrapper_creation = time.perf_counter()
    gen.generate(os.path.dirname(x2py_dirpath))
    timings["Wrapper creation"] = time.perf_counter() - start_wrapper_creation
    _print_verbose_timing(verbose, "Wrapper creation", timings["Wrapper creation"])

    # -------------------------------------------
    #           Print wrapper code
    # -------------------------------------------

    start_wrapper_printing = time.perf_counter()
    wrapper_files = gen.write(x2py_dirpath)
    timings["Wrapper printing"] = time.perf_counter() - start_wrapper_printing
    _print_verbose_timing(verbose, "Wrapper printing", timings["Wrapper printing"])

    printed_languages = gen.generated_languages

    # -------------------------------------------
    #         Prepare the compile objects
    # -------------------------------------------

    wrapper_compile_objs = [
        CompileObj(
            filepath.name,
            x2py_dirpath,
            flags=main_obj.flags,
            dependencies=(main_obj,),
        )
        for filepath in wrapper_files[:-1]
    ] + [
        CompileObj(
            wrapper_files[-1].name,
            x2py_dirpath,
            flags=wrapper_flags,
            link_args=main_obj.link_args,
            dependencies=(main_obj, *dependencies),
            extra_compilation_tools=("python",),
        )
    ]

    for i, (obj, lang, imports) in enumerate(
        zip(
            wrapper_compile_objs,
            printed_languages,
            gen.get_additional_imports(),
            strict=True,
        )
    ):
        obj.add_dependencies(*wrapper_compile_objs[:i])
        install_runtime_support(
            imports,
            x2py_dirpath=x2py_dirpath,
            compiler=compiler,
            wrapper_obj=obj,
            language=lang,
            verbose=verbose,
        )

    # -------------------------------------------
    #               Compile code
    # -------------------------------------------

    start_compile_wrapper = time.perf_counter()
    for obj, wrapper_language in zip(wrapper_compile_objs, printed_languages, strict=True):
        compiler.compile_module(
            compile_obj=obj,
            output_folder=x2py_dirpath,
            language=wrapper_language,
            verbose=verbose,
        )

    sharedlib_filepath = compiler.compile_shared_library(
        wrapper_compile_objs[-1],
        output_folder=output_dirpath,
        sharedlib_modname=sharedlib_modname,
        language=language,
        verbose=verbose,
    )

    timings["Wrapper compilation"] = time.perf_counter() - start_compile_wrapper
    _print_verbose_timing(verbose, "Wrapper compilation", timings["Wrapper compilation"])

    # Return absolute path of shared library
    return sharedlib_filepath, timings
