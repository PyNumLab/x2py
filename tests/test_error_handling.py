# -*- coding: utf-8 -*-
import os
import pytest

from fortran_parser import (
    FortranParseError,
    parse_fortran_interfaces,
    parse_fortran_modules,
    parse_fortran_signatures,
    parse_fortran_types,
)


def _make_error():
    code = "subroutine foo(x)\n  integer :: x\n  weirdtype :: y\nend subroutine foo\n"
    with pytest.raises(FortranParseError) as exc_info:
        parse_fortran_signatures(code, filename="foo.f90")
    return exc_info.value


# ---------------------------------------------------------------------------
# Diagnostic formatting
# ---------------------------------------------------------------------------

def test_error_message_contains_diagnostic_code():
    err = _make_error()
    msg = str(err)
    assert "error[PARSE001]" in msg


def test_error_message_contains_location_arrow():
    err = _make_error()
    msg = str(err)
    assert "--> foo.f90:3" in msg


def test_error_message_contains_source_context():
    err = _make_error()
    msg = str(err)
    assert "weirdtype :: y" in msg


def test_error_debug_mode_shows_internal_location():
    err = _make_error()
    msg = err.format(debug=True)
    assert "[internal]" in msg
    assert "in " in msg


def test_error_env_debug_mode(monkeypatch):
    monkeypatch.setenv("X2PY_DEBUG_ERRORS", "1")
    err = _make_error()
    msg = err.format()
    assert "[internal]" in msg


def test_error_color_mode_does_not_crash():
    err = _make_error()
    msg = err.format(color=True)
    assert isinstance(msg, str)


# ---------------------------------------------------------------------------
# Existing behavior
# ---------------------------------------------------------------------------

def test_parse_error_carries_filename():
    err = _make_error()
    assert err.filename == "foo.f90"
    assert err.line_number == 3
    assert err.source_line is not None


def test_parse_error_is_subclass_of_value_error():
    with pytest.raises(ValueError):
        _make_error()
