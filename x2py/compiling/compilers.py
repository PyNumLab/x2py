#!/usr/bin/python
"""
Module handling everything related to the compilers used to compile the various generated files
"""

import json
import os
import pathlib
import platform
import shlex
import shutil
import subprocess
import time
import warnings

from .default_compilers import available_compilers, vendors

if platform.system() == "Darwin":
    # Collect version using mac tools to avoid unexpected results on Big Sur
    # https://developer.apple.com/documentation/macos-release-notes/macos-big-sur-11_0_1-release-notes#Third-Party-Apps
    with subprocess.Popen([shutil.which("sw_vers"), "-productVersion"], stdout=subprocess.PIPE) as p:
        result, err = p.communicate()
    mac_version_tuple = result.decode("utf-8").strip().split(".")
    mac_target = ".".join(mac_version_tuple[:2])
    os.environ["MACOSX_DEPLOYMENT_TARGET"] = mac_target


def get_condaless_search_path(conda_warnings="basic"):
    """
    Get a list of paths excluding the conda paths.

    Get the value of the PATH variable to be set when searching for the compiler
    This is the same as the environment PATH variable but without any conda paths.

    Parameters
    ----------
    conda_warnings : str, optional
        Specify the level of Conda warnings to display (choices: off, basic, verbose), Default is 'basic'.

    Returns
    -------
    str
        A list of paths excluding the conda paths.
    """
    path_sep = ";" if platform.system() == "Windows" else ":"
    current_path = os.environ["PATH"]
    folders = {f: f.split(os.sep) for f in current_path.split(path_sep)}
    conda_folder_names = (
        "conda",
        "anaconda",
        "miniconda",
        "Conda",
        "Anaconda",
        "Miniconda",
    )
    conda_folders = [p for p, f in folders.items() if any(con in f for con in conda_folder_names)]
    if conda_folders and conda_warnings in ("basic", "verbose"):
        message_warning = "Conda paths are ignored. See https://github.com/x2py/x2py/blob/devel/docs/compiler.md#utilising-x2py-within-anaconda-environment for details"
        if conda_warnings == "verbose":
            message_warning = message_warning + "\nConda ignored PATH:\n"
            message_warning = message_warning + ":".join(conda_folders)
        warnings.warn(UserWarning(message_warning), stacklevel=2)
    return path_sep.join(p for p in folders if p not in conda_folders and os.path.exists(p))


# ------------------------------------------------------------
class Compiler:
    """
    Class which handles all compiler options.

    This class uses the compiler vendor or a json file to collect
    all compiler configuration parameters. These are then used to
    correctly print compiler commands such as shared library
    compilation commands or executable creation commands.

    Parameters
    ----------
    vendor : str
               Name of the family of compilers.
    debug : bool
               Indicates whether we are compiling in debug mode.
    execute_commands : bool
               Execute prepared commands immediately. If false, retain them in
               ``command_log`` for an external build system.
    """

    __slots__ = (
        "_command_log",
        "_compiler_family",
        "_compiler_info",
        "_debug",
        "_execute_commands",
        "_language_info",
    )
    acceptable_bin_paths = None

    def __init__(self, vendor: str, debug=False, *, execute_commands=True):
        if vendor.endswith(".json") and os.path.exists(vendor):
            self._compiler_family = pathlib.Path(vendor).stem
            with open(vendor, encoding="utf-8") as vendor_file:
                self._compiler_info = json.load(vendor_file)
        else:
            self._compiler_family = vendor
            if vendor in vendors:
                try:
                    self._compiler_info = available_compilers[vendor]
                except KeyError as e:
                    raise NotImplementedError("Compiler not available") from e
            else:
                installed_compiler = (
                    pathlib.Path(os.environ.get("X2PY_CONFIG_HOME", pathlib.Path.home() / ".x2py")) / vendor
                )
                if installed_compiler.exists():
                    with open(installed_compiler / "config.json", encoding="utf-8") as vendor_file:
                        self._compiler_info = json.load(vendor_file)
                else:
                    raise NotImplementedError(f"Unrecognised compiler vendor : {vendor}")

        self._debug = debug
        self._execute_commands = execute_commands
        self._command_log = []
        self._language_info = None

    @property
    def command_log(self):
        """Exact expanded compiler commands prepared by this instance."""
        return tuple(tuple(command) for command in self._command_log)

    def _run_or_record_command(self, cmd, verbose):
        expanded = [os.path.expandvars(str(part)) for part in cmd]
        self._command_log.append(expanded)
        if self._execute_commands:
            return self.run_command(expanded, verbose)
        return expanded

    def get_exec(self, extra_compilation_tools, language=None):
        """
        Obtain the path of the executable based on the specified compilation tools.

        The `get_exec` method is responsible for retrieving the path of the executable based on
        the specified compilation tools. It is used internally in the X2py module. In particular
        the executable depends on whether MPI is used.

        Parameters
        ----------
        extra_compilation_tools : str
            Specifies the compilation tools to be used.
        language : str, optional
            The language being compiled. This argument should be provided unless this method
            is called from a method of this class after setting self._language_info.

        Returns
        -------
        str
            The path of the executable corresponding to the specified compilation tools.

        Raises
        ------
        X2pyError
            If the compiler executable cannot be found.
        """
        language_info = self._language_info if language is None else self._compiler_info[language]
        # Get executable
        exec_cmd = language_info["mpi_exec"] if "mpi" in extra_compilation_tools else language_info["exec"]

        # Clean conda paths out of the PATH variable
        current_path = os.environ["PATH"]
        os.environ["PATH"] = self.acceptable_bin_paths

        # Find the exact path of the executable
        exec_loc = shutil.which(exec_cmd)

        # Reset PATH variable
        os.environ["PATH"] = current_path

        if exec_loc is None:
            raise FileNotFoundError(f"Could not find compiler ({exec_cmd})")

        return exec_loc

    def _get_flags(self, flags=(), extra_compilation_tools=()):
        """
        Collect necessary compile flags.

        Collect necessary compile flags, e.g. those relevant to the
        language or compilation mode (debug/release).

        Parameters
        ----------
        flags : iterable of str
            Any additional flags requested by the user / required by
            the file.
        extra_compilation_tools : iterable or str
            Tools used which require additional compilation flags/include dirs/libs/etc.

        Returns
        -------
        list[str]
            A list containing the flags.
        """
        user_flags = list(flags)
        flags = []

        if self._debug:
            flags.extend(self._language_info.get("debug_flags", ()))
        else:
            flags.extend(self._language_info.get("release_flags", ()))

        flags.extend(self._language_info.get("general_flags", ()))
        # M_PI is not in the standard
        # if 'python' not in extra_compilation_tools:
        #    # Python sets its own standard
        #    flags.extend(self._language_info.get('standard_flags',()))

        for a in extra_compilation_tools:
            tool_flags = self._language_info.get(a, {}).get("flags", ())
            if a == "python":
                tool_flags = self._without_python_profile_flags(tool_flags)
            flags.extend(tool_flags)

        flags.extend(user_flags)

        return flags

    @staticmethod
    def _without_python_profile_flags(flags):
        """Drop Python sysconfig optimization/debug flags in favor of x2py's profile."""
        return [flag for flag in flags if not (flag.startswith("-O") or flag.startswith("-g") or flag == "-DNDEBUG")]

    def _get_property(self, key, properties=(), extra_compilation_tools=()):
        """
        Collect necessary compile property.

        Collect necessary compile properties such as include folders
        or library directories.

        Parameters
        ----------
        key : str
            A key describing the property of interest.
        properties : iterable of str
            Any additional values of the property requested by the
            user / required by the file.
        extra_compilation_tools : iterable or str
            Tools used which require additional compilation flags/include dirs/libs/etc.

        Returns
        -------
        iterable[str]
            An iterable containing the relevant information from the
            requested property.

        Examples
        --------
        >> self._get_property("libs", ("-lmy_lib",), ())
        dict_keys(['-lmy_lib', '-lm'])

        >> self._get_property("libs", ("-lmy_lib",), ("openmp",))
        dict_keys(['-lmy_lib', '-lm', 'gomp'])

        >> self._get_property("include", ("/home/user/homemade-install-dir/",), ("mpi",))
        dict_keys(['/home/user/homemade-install-dir/'])
        """
        # Use a dictionary instead of a set to ensure properties are ordered by insertion
        # The keys of the dictionary contain the values for the property of interest.
        properties = dict.fromkeys(properties)

        properties.update(dict.fromkeys(self._language_info.get(key, ())))

        for a in extra_compilation_tools:
            properties.update(dict.fromkeys(self._language_info.get(a, {}).get(key, ())))

        return properties.keys()

    def _get_include(self, include=(), extra_compilation_tools=()):
        """
        Collect necessary compile include directories.

        Collect necessary compile include directories.

        Parameters
        ----------
        include : iterable of str
                       Any additional include directories requested by the user
                       / required by the file.
        extra_compilation_tools : iterable or str
            Tools used which require additional compilation flags/include dirs/libs/etc.

        Returns
        -------
        list[str]
            A list of the include folders.
        """
        return self._get_property("include", include, extra_compilation_tools)

    def _get_libs(self, libs=(), extra_compilation_tools=()):
        """
        Collect necessary compile libraries.

        Collect necessary compile libraries.

        Parameters
        ----------
        libs : iterable of str
            Any additional libraries requested by the user / required
            by the file.
        extra_compilation_tools : iterable or str
            Tools used which require additional compilation flags/include dirs/libs/etc.

        Returns
        -------
        list[str]
            A list of the libraries.
        """
        return self._get_property("libs", libs, extra_compilation_tools)

    def _get_libdir(self, libdir=(), extra_compilation_tools=()):
        """
        Collect necessary compile library directories.

        Collect necessary compile library directories.

        Parameters
        ----------
        libdir : iterable of str
            Any additional library directories requested by the user
            / required by the file.
        extra_compilation_tools : iterable or str
            Tools used which require additional compilation flags/include dirs/libs/etc.

        Returns
        -------
        list[str]
            A list of the folders containing libraries.
        """
        return self._get_property("libdir", libdir, extra_compilation_tools)

    def _get_dependencies(self, dependencies=(), extra_compilation_tools=()):
        """
        Collect necessary dependencies.

        Collect necessary object or static libraries that should be included to compile
        this object.

        Parameters
        ----------
        dependencies : iterable of str
            Any additional dependencies required by the file.
        extra_compilation_tools : iterable or str
            Tools used which require additional compilation flags/include dirs/libs/etc.

        Returns
        -------
        list[str]
            A list of the necessary dependencies.
        """
        return self._get_property("dependencies", dependencies, extra_compilation_tools)

    @staticmethod
    def _insert_prefix_to_list(lst, prefix):
        """
        Add a prefix into a list.

        Add a prefix into a list. E.g:
        >>> lst = [1, 2, 3]
        >>> _insert_prefix_to_list(lst, 'num:')
        ['num:', 1, 'num:', 2, 'num:', 3]

        Parameters
        ----------
        lst : iterable
            This sequence is copied to a new list with `prefix` before each element.
        prefix : Any
            The prefix to be placed before each element of `lst`.

        Returns
        -------
        list
            The list with the prefix inserted.
        """
        lst = [(prefix, i) for i in lst]
        return [f for fi in lst for f in fi]

    def _get_compile_components(self, compile_obj, extra_compilation_tools=()):
        """
        Provide all components required for compiling.

        Provide all the different components (include directories, libraries, etc)
        which are needed in order to compile any file.

        Parameters
        ----------
        compile_obj : CompileObj
            Object containing all information about the object to be compiled.
        extra_compilation_tools : iterable of str
            Tools used which require additional compilation flags/include dirs/libs/etc.

        Returns
        -------
        exec_cmd : str
            The command required to run the executable.
        inc_flags : iterable of strs
            The include directories required to compile.
        libs_flags : iterable of strs
            The libraries required to compile.
        libdir_flags : iterable of strs
            The directories containing libraries required to compile.
        m_code : iterable of strs
            The objects required to compile.
        """

        # get include
        include = self._get_include(compile_obj.include, extra_compilation_tools)
        inc_flags = self._insert_prefix_to_list(include, "-I")

        # Get dependencies (.o/.a)
        m_code = self._get_dependencies(compile_obj.extra_modules, extra_compilation_tools)

        # Get libraries and library directories
        libs = self._get_libs(compile_obj.libs, extra_compilation_tools)
        libs_flags = [s if s.startswith("-l") else f"-l{s}" for s in libs]
        libdir = self._get_libdir(compile_obj.libdir, extra_compilation_tools)
        libdir_flags = self._insert_prefix_to_list(libdir, "-L")

        exec_cmd = self.get_exec(extra_compilation_tools)

        return exec_cmd, inc_flags, libs_flags, libdir_flags, m_code

    def compile_module(self, compile_obj, output_folder, language, verbose):
        """
        Compile a module.

        Compile a file containing a module to a .o file.

        Parameters
        ----------
        compile_obj : CompileObj
            Object containing all information about the object to be compiled.

        output_folder : str
            The folder where the result should be saved.

        language : str
            Language that we are compiling.

        verbose : int
            Indicates the level of verbosity.
        """
        if not compile_obj.has_target_file:
            return

        if verbose:
            print(">> Compiling :: ", compile_obj.module_target)

        self._language_info = self._compiler_info[language]

        extra_compilation_tools = compile_obj.extra_compilation_tools

        # Get flags
        flags = self._get_flags(compile_obj.flags, extra_compilation_tools)
        flags.append("-c")

        # Get include
        include = self._get_include(compile_obj.include, extra_compilation_tools)
        inc_flags = self._insert_prefix_to_list(include, "-I")

        # Get executable
        exec_cmd = self.get_exec(extra_compilation_tools)

        j_code = (self._language_info["module_output_flag"], output_folder) if language == "fortran" else ()

        cmd = [
            exec_cmd,
            *flags,
            *inc_flags,
            compile_obj.source,
            "-o",
            compile_obj.module_target,
            *j_code,
        ]

        with compile_obj:
            self._run_or_record_command(cmd, verbose)

        self._language_info = None

    def compile_shared_library(self, compile_obj, output_folder, language, verbose, sharedlib_modname=None):
        """
        Compile a module to a shared library.

        Compile a file containing a module with C-API calls to a shared library which can
        be called from Python.

        Parameters
        ----------
        compile_obj : CompileObj
            Object containing all information about the object to be compiled.

        output_folder : str
            The folder where the result should be saved.

        language : str
            Language that we are compiling.

        verbose : int
            Indicates the level of verbosity.

        sharedlib_modname : str, optional
            The name of the library that should be generated. If none is provided then it
            defaults to matching the name of the file.

        Returns
        -------
        str
            Generated library name.
        """
        self._language_info = self._compiler_info[language]

        # Ensure python options are collected
        extra_compilation_tools = set(compile_obj.extra_compilation_tools)

        extra_compilation_tools.remove("python")

        # get flags
        flags = self._get_flags(compile_obj.flags, extra_compilation_tools)

        extra_compilation_tools.add("python")

        # Collect compile information
        exec_cmd, _, libs_flags, libdir_flags, m_code = self._get_compile_components(
            compile_obj, extra_compilation_tools
        )
        linker_libdir_flags = ["-Wl,-rpath" if flag == "-L" else flag for flag in libdir_flags]

        flags.insert(0, "-shared")

        # Get name of file
        ext_suffix = self._language_info["python"]["shared_suffix"]
        sharedlib_modname = sharedlib_modname or compile_obj.python_module
        file_out = os.path.join(output_folder, sharedlib_modname + ext_suffix)

        if verbose:
            print(">> Compiling shared library :: ", file_out)

        cmd = [
            exec_cmd,
            *flags,
            *libdir_flags,
            *linker_libdir_flags,
            compile_obj.module_target,
            *m_code,
            *compile_obj.link_args,
            "-o",
            file_out,
            *libs_flags,
        ]

        with compile_obj:
            self._run_or_record_command(cmd, verbose)

        self._language_info = None

        return file_out

    @staticmethod
    def run_command(cmd, verbose):
        """
        Run the provided command and collect the output.

        Run the provided compilation command, collect the output and raise any
        necessary errors if the file does not compile.

        Parameters
        ----------
        cmd : list of str
            The command to run.
        verbose : int
            Indicates the level of verbosity.

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
            print(shlex.join(cmd))

        start_time = time.perf_counter()
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as p:
            out, err = p.communicate()
        elapsed = time.perf_counter() - start_time

        if verbose and out:
            print(out)
        if verbose:
            print(f">> Command completed in {elapsed:.3f}s")
        if p.returncode != 0:
            err_msg = "Failed to build module"
            err_msg += "\n" + err
            raise RuntimeError(err_msg)
        if err:
            warnings.warn(UserWarning(err), stacklevel=2)

        return cmd
