#!/usr/bin/env python3
"""Print failed pytest node IDs from a JUnit XML report."""

from __future__ import annotations

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


def failed_pytest_nodes(report: Path) -> list[str]:
    """Return failed or errored pytest node IDs in report order."""
    root = ET.parse(report).getroot()
    nodes = []
    seen = set()
    for case in root.iter("testcase"):
        if case.find("failure") is None and case.find("error") is None:
            continue
        node = _testcase_node_id(case)
        if node not in seen:
            seen.add(node)
            nodes.append(node)
    return nodes


def _testcase_node_id(case: ET.Element) -> str:
    """Return the most precise pytest-style node ID available for one case."""
    name = case.get("name") or "<unnamed test>"
    filename = case.get("file")
    if filename:
        return f"{filename}::{name}"
    classname = case.get("classname")
    if classname:
        return f"{classname}::{name}"
    return name


def failure_summary(report: Path) -> str:
    """Format a failure-name summary without obscuring a prior pytest failure."""
    heading = "Failed pytest nodes"
    if not report.is_file():
        return f"{heading}\n- report unavailable: {report}"
    try:
        nodes = failed_pytest_nodes(report)
    except (ET.ParseError, OSError) as error:
        return f"{heading}\n- report unreadable: {error}"
    if not nodes:
        return f"{heading}\n- no failed nodes recorded"
    return "\n".join((heading, *(f"- {node}" for node in nodes)))


def main(argv: list[str] | None = None) -> int:
    """Print the failed-node summary for one pytest JUnit report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="pytest JUnit XML report")
    arguments = parser.parse_args(argv)
    print(failure_summary(arguments.report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
