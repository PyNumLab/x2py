# -*- coding: utf-8 -*-
"""Public parser entrypoints and source/path input contracts."""

import pytest

from fortran_parser.parser import FortranParser
from x2py import FortranParseError, parse_fortran_file, parse_fortran_project

def test_parser_public_entrypoint_aliases_and_singular_contracts_use_inline_sources():
    parser = FortranParser()
    module_code = """
module alias_mod
contains
  subroutine ping(x)
    integer, intent(in) :: x
  end subroutine ping
end module alias_mod
"""

    assert parser.visit_file(module_code).modules[0].name == "alias_mod"
    assert parser.visit_file(module_code).modules[0].procedures[0].name == "ping"
    assert "alias_mod" in parser.visit_project({"alias.f90": module_code}).modules
    assert "alias_mod.ping" in parser.visit_project({"alias.f90": module_code}).procedures

    assert parser.visit_fortran_module("module single_mod\nend module single_mod\n").name == "single_mod"
    assert parser.visit_fortran_program("program driver\nend program driver\n").name == "driver"
    assert parser.visit_fortran_derived_type("type :: state_t\nend type state_t\n").name == "state_t"
    assert parser.visit_fortran_interface(
        """
interface callback
  subroutine cb()
  end subroutine cb
end interface callback
"""
    ).name == "callback"
    assert parser.visit_fortran_submodule(
        "submodule (parent_mod) child_mod\nend submodule child_mod\n"
    ).name == "child_mod"
    assert parser.visit_fortran_block_data_unit(
        "block data init_data\n  integer seed\nend block data init_data\n"
    ).name == "init_data"

    with pytest.raises(FortranParseError, match="none were found"):
        parser.visit_fortran_module("program not_a_module\nend program not_a_module\n")

    with pytest.raises(FortranParseError, match="found 2"):
        parser.visit_fortran_module(
            """
module first_mod
end module first_mod
module second_mod
end module second_mod
"""
        )

def test_file_path_and_unknown_filename_public_parse_paths(tmp_path):
    source_path = tmp_path / "path_input.f90"
    source_path.write_text(
        """
subroutine from_path(i)
  integer, intent(in) :: i
end subroutine from_path
""",
        encoding="utf-8",
    )

    parsed_from_path = parse_fortran_file(source_path)
    parsed_unknown_suffix = parse_fortran_file(
        """
subroutine from_unknown(i)
  integer, intent(in) :: i
end subroutine from_unknown
""",
        filename="from_unknown.src",
    )
    parsed_literal = parse_fortran_file(12345)

    assert parsed_from_path.filename == str(source_path)
    assert parsed_from_path.format == "modern"
    assert parsed_from_path.procedures[0].name == "from_path"
    assert parsed_unknown_suffix.format == "unknown"
    assert parsed_literal.procedures == []

def test_public_instance_visitor_entrypoints_use_source_strings():
    parser = FortranParser()

    assert parser.visit_file(
        """
subroutine alias_proc()
end subroutine alias_proc
"""
    ).procedures[0].name == "alias_proc"
    assert "alias_mod" in parser.visit_project(
        {
            "alias_mod.f90": """
module alias_mod
end module alias_mod
"""
        }
    ).modules

    with pytest.raises(FortranParseError, match="only standalone procedures were found"):
        parser.visit_fortran_module(
            """
subroutine lone_proc()
end subroutine lone_proc
"""
        )

def test_public_project_parse_from_path_sequence(tmp_path):
    source_path = tmp_path / "listed_project.f90"
    source_path.write_text(
        """
module listed_project_mod
contains
  subroutine work()
  end subroutine work
end module listed_project_mod
""",
        encoding="utf-8",
    )

    project = parse_fortran_project([source_path])

    assert "listed_project_mod" in project.modules
    assert "listed_project_mod.work" in project.procedures
