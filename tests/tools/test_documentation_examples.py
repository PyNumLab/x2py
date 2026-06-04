"""Execute explicitly marked examples embedded in Markdown documentation."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

import pytest


ROOT = Path(__file__).parents[2]
DOC_PATHS = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
TEST_MARKER = re.compile(r"^\s*<!--\s*x2py-doc-test:\s*(run|exact)\s*-->\s*$")
OUTPUT_MARKER = re.compile(r"^\s*<!--\s*x2py-doc-test-output\s*-->\s*$")
FENCE_MARKER = re.compile(r"^\s*(`{3,}|~{3,})")
SHELL_OPERATORS = {"&&", "||", ";", "|", ">", ">>", "<", "2>", "2>>"}
DISALLOWED_OPTIONS = {
    "--compile-commands",
    "--compiler",
    "--compiler-arg",
    "--out",
    "--preprocess-template",
}


@dataclass(frozen=True)
class DocumentationExample:
    path: Path
    line: int
    mode: str
    language: str
    command: str
    expected_output: str | None = None

    @property
    def test_id(self) -> str:
        return f"{self.path.relative_to(ROOT)}:{self.line}"


def _next_nonempty_line(lines: list[str], start: int) -> int:
    index = start
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def _fenced_block(lines: list[str], start: int, *, language: str | None = None) -> tuple[str, int, str]:
    start = _next_nonempty_line(lines, start)
    if start >= len(lines) or not lines[start].startswith("```"):
        raise AssertionError(f"expected a fenced block at line {start + 1}")
    actual_language = lines[start][3:].strip()
    if language is not None and actual_language != language:
        raise AssertionError(f"expected a {language!r} fenced block at line {start + 1}, got {actual_language!r}")

    end = start + 1
    while end < len(lines) and lines[end].strip() != "```":
        end += 1
    if end >= len(lines):
        raise AssertionError(f"unclosed fenced block at line {start + 1}")
    return "\n".join(lines[start + 1 : end]), end + 1, actual_language


def _logical_command(command_block: str, *, location: str) -> str:
    command = re.sub(r"\\\n\s*", " ", command_block).strip()
    if "\n" in command:
        raise AssertionError(f"{location}: documentation tests must contain exactly one shell command")
    return command


def _examples_from_path(path: Path) -> list[DocumentationExample]:
    lines = path.read_text(encoding="utf-8").splitlines()
    examples: list[DocumentationExample] = []
    index = 0

    while index < len(lines):
        marker = TEST_MARKER.match(lines[index])
        if marker is None:
            if OUTPUT_MARKER.match(lines[index]):
                raise AssertionError(f"{path.relative_to(ROOT)}:{index + 1}: output marker has no exact test")
            fence = FENCE_MARKER.match(lines[index])
            if fence is not None:
                token = fence.group(1)
                index += 1
                while index < len(lines) and lines[index].strip() != token:
                    index += 1
            index += 1
            continue

        mode = marker.group(1)
        marker_line = index + 1
        command_block, after_command, language = _fenced_block(lines, index + 1)
        if language not in {"bash", "python"}:
            raise AssertionError(
                f"{path.relative_to(ROOT)}:{marker_line}: documentation tests require a bash or python fenced block"
            )
        command = (
            _logical_command(command_block, location=f"{path.relative_to(ROOT)}:{marker_line}")
            if language == "bash"
            else command_block
        )
        expected_output = None
        index = after_command

        if mode == "exact":
            while index < len(lines) and not OUTPUT_MARKER.match(lines[index]):
                if TEST_MARKER.match(lines[index]):
                    raise AssertionError(
                        f"{path.relative_to(ROOT)}:{marker_line}: exact test is missing an output marker"
                    )
                index += 1
            if index >= len(lines):
                raise AssertionError(f"{path.relative_to(ROOT)}:{marker_line}: exact test is missing an output marker")
            expected_output, index, _output_language = _fenced_block(lines, index + 1)

        examples.append(
            DocumentationExample(
                path=path,
                line=marker_line,
                mode=mode,
                language=language,
                command=command,
                expected_output=expected_output,
            )
        )

    return examples


DOCUMENTATION_EXAMPLES = [example for path in DOC_PATHS for example in _examples_from_path(path)]


def _command_argv(example: DocumentationExample) -> list[str]:
    if example.language == "python":
        return [sys.executable, "-c", example.command]

    argv = shlex.split(example.command)
    if not argv or argv[0] not in {"python", "python3"} or argv[1:3] != ["-m", "x2py"]:
        raise AssertionError(f"{example.test_id}: only 'python[3] -m x2py' commands are supported")
    if any(argument in SHELL_OPERATORS for argument in argv):
        raise AssertionError(f"{example.test_id}: shell operators are not supported")
    if any(
        argument == option or argument.startswith(f"{option}=") for argument in argv for option in DISALLOWED_OPTIONS
    ):
        raise AssertionError(f"{example.test_id}: output-writing and custom-executable options are not supported")
    argv[0] = sys.executable
    return argv


def test_documentation_has_automatically_verified_examples():
    assert DOCUMENTATION_EXAMPLES, "mark at least one Markdown example with x2py-doc-test"
    assert any(example.mode == "exact" for example in DOCUMENTATION_EXAMPLES)


@pytest.mark.parametrize("path", DOC_PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_documented_expected_output_labels_are_automatically_verified(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() not in {"Expected output:", "Output:"}:
            continue
        marker_index = _next_nonempty_line(lines, index + 1)
        assert marker_index < len(lines) and OUTPUT_MARKER.match(lines[marker_index]), (
            f"{path.relative_to(ROOT)}:{index + 1}: documented output must use x2py-doc-test-output"
        )


@pytest.mark.parametrize("example", DOCUMENTATION_EXAMPLES, ids=lambda example: example.test_id)
def test_documentation_example(example: DocumentationExample):
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT), env.get("PYTHONPATH")]))
    result = subprocess.run(
        _command_argv(example),
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, (
        f"{example.test_id}: command failed with status {result.returncode}\n"
        f"command: {example.command}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert result.stderr == "", f"{example.test_id}: command wrote to stderr:\n{result.stderr}"
    if example.mode == "exact":
        assert result.stdout.rstrip("\n") == (example.expected_output or "").rstrip("\n")
