"""Cyclomatic complexity measurement using the Python AST."""

from __future__ import annotations

import ast
from pathlib import Path


BRANCH_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.IfExp,
    ast.Match,
    ast.comprehension,
)


def measure_complexity(source_root: Path) -> dict[str, object]:
    functions = []
    for path in sorted(source_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = 1 + sum(_branch_cost(child) for child in ast.walk(node) if child is not node)
                functions.append(
                    {
                        "file": str(path),
                        "function": node.name,
                        "line": node.lineno,
                        "complexity": complexity,
                    }
                )
    complexities = [item["complexity"] for item in functions]
    return {
        "function_count": len(functions),
        "average_complexity": sum(complexities) / max(1, len(complexities)),
        "maximum_complexity": max(complexities, default=0),
        "functions": sorted(functions, key=lambda item: (-item["complexity"], item["file"], item["line"])),
    }


def _branch_cost(node: ast.AST) -> int:
    if isinstance(node, ast.BoolOp):
        return max(0, len(node.values) - 1)
    if isinstance(node, BRANCH_NODES):
        return 1
    return 0
