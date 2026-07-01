#!/usr/bin/env python3
"""Check that deploy release metrics were recorded in release notes."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_RELEASE_NOTES_PATH = Path("RELEASE_NOTES.md")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-notes", type=Path, default=DEFAULT_RELEASE_NOTES_PATH)
    parser.add_argument("--guardrails", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--release-label", required=True)
    args = parser.parse_args()

    del args.guardrails
    check_release_guardrails(args.release_notes, args.release_label)


def check_release_guardrails(release_notes: Path, release_label: str) -> None:
    markdown = release_notes.read_text(encoding="utf-8")
    failures = _release_record_failures(markdown, release_label)
    if failures:
        formatted = "\n".join(f"- {failure}" for failure in failures)
        raise SystemExit(f"Release guardrails failed for {release_label}:\n{formatted}")
    print(f"Release guardrails passed for {release_label}.")


def _release_record_failures(markdown: str, release_label: str) -> list[str]:
    failures = []
    generated_metrics = _markdown_table_after_heading(markdown, "## Generated Release Metrics")
    if not _table_has_release(generated_metrics, release_label):
        failures.append(f"{release_label} is missing from the Generated Release Metrics table.")
    for heading in ("### Grade Band Precision", "## Grade Precision"):
        table = _markdown_table_after_heading(markdown, heading)
        if _last_table_release(table) != release_label:
            failures.append(f"{heading.lstrip('#').strip()} last row is not {release_label}.")
    return failures


def _markdown_table_after_heading(markdown: str, heading: str) -> list[str]:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            table = []
            for table_line in lines[index + 1:]:
                if table_line.startswith("#"):
                    break
                if table_line.strip().startswith("|"):
                    table.append(table_line)
            if len(table) >= 3:
                return table
    raise SystemExit(f"Release guardrails failed: {heading.lstrip('#').strip()} table was not found.")


def _table_has_release(table: list[str], release_label: str) -> bool:
    for row in table[2:]:
        cells = _table_cells(row)
        if cells and cells[0] == release_label:
            return True
    return False


def _last_table_release(table: list[str]) -> str:
    for row in reversed(table[2:]):
        cells = _table_cells(row)
        if cells:
            return cells[0]
    return ""


def _table_cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


if __name__ == "__main__":
    main()
