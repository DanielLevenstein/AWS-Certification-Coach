"""Line coverage collection built on the standard-library trace module."""

from __future__ import annotations

from pathlib import Path
import sys
import trace

import pytest


def measure_coverage(
    source_root: Path,
    test_path: Path,
    ignore_paths: tuple[Path, ...] = (),
) -> dict[str, object]:
    project_root = Path.cwd().resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    tracer = trace.Trace(count=True, trace=False, ignoredirs=[str(Path.cwd() / ".venv")])
    pytest_args = [str(test_path), "-q"]
    pytest_args.extend(f"--ignore={path}" for path in ignore_paths)
    exit_code = tracer.runfunc(pytest.main, pytest_args)
    if exit_code != 0:
        raise RuntimeError(f"Unit tests failed while collecting coverage: pytest exit code {exit_code}")

    counts = tracer.results().counts
    covered_by_file: dict[Path, set[int]] = {}
    for (filename, line), count in counts.items():
        if count > 0:
            covered_by_file.setdefault(Path(filename).resolve(), set()).add(line)
    files = []
    total_executable = 0
    total_covered = 0
    for path in sorted(source_root.rglob("*.py")):
        executable = _executable_lines(path)
        covered = covered_by_file.get(path.resolve(), set())
        covered_count = len(executable & covered)
        total_executable += len(executable)
        total_covered += covered_count
        files.append(
            {
                "file": str(path),
                "executable_lines": len(executable),
                "covered_lines": covered_count,
                "coverage": covered_count / max(1, len(executable)),
            }
        )
    return {
        "executable_lines": total_executable,
        "covered_lines": total_covered,
        "coverage": total_covered / max(1, total_executable),
        "files": files,
    }


def _executable_lines(path: Path) -> set[int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return {
        line
        for line, source_line in enumerate(lines, start=1)
        if source_line.strip() and not source_line.lstrip().startswith("#")
    }
