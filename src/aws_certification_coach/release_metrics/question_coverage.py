"""Question-bank coverage metrics for release reporting."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable


CHART_FONT_SIZES = {
    "title": 20,
    "suptitle": 24,
    "axis": 15,
    "tick": 18,
    "pie": 13,
    "footer": 12,
}


def measure_question_coverage(rows: Iterable[dict[str, object]]) -> dict[str, object]:
    questions = list(rows)
    domains = Counter(_text(row.get("domain"), "Unknown") for row in questions)
    certifications = Counter(_text(row.get("certification"), "Unknown") for row in questions)
    difficulties = Counter(_text(row.get("difficulty"), "Unknown") for row in questions)
    question_intents = Counter(_question_intent(row) for row in questions)
    concepts = Counter(
        concept
        for row in questions
        for concept in _concepts(row.get("key_concepts"))
    )
    service_names = Counter(
        _service_name(source_name)
        for source_name in (
            row.get("original_multiple_choice", {}).get("source_name")
            for row in questions
            if isinstance(row.get("original_multiple_choice"), dict)
        )
    )
    source_names = Counter(
        _text(source_name, "Unknown")
        for source_name in (
            row.get("original_multiple_choice", {}).get("source_name")
            for row in questions
            if isinstance(row.get("original_multiple_choice"), dict)
        )
    )

    return {
        "question_count": len(questions),
        "domain_count": len(domains),
        "certification_count": len(certifications),
        "concept_count": len(concepts),
        "question_intent_count": len(question_intents),
        "domains": _counter_rows(domains),
        "certifications": _counter_rows(certifications),
        "difficulties": _counter_rows(difficulties),
        "question_intents": _counter_rows(question_intents),
        "covered_services": _counter_rows(service_names),
        "top_concepts": _counter_rows(concepts, limit=20),
        "top_sources": _counter_rows(source_names, limit=10),
    }


def plot_question_coverage(metrics: dict[str, object], output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    domains = _series(metrics.get("domains", []), limit=12)
    certifications = _series(metrics.get("certifications", []), limit=8)
    question_intents = _series(metrics.get("question_intents", []), limit=8)

    figure = plt.figure(figsize=(16, 18), constrained_layout=True)
    grid = figure.add_gridspec(3, 1, height_ratios=[1.1, 1.1, 1])

    domain_axis = figure.add_subplot(grid[0, 0])
    _plot_horizontal_bars(domain_axis, domains, "Domain Coverage", "Question count", "#2f6f73")

    intent_axis = figure.add_subplot(grid[1, 0])
    _plot_question_intents(intent_axis, question_intents)

    cert_axis = figure.add_subplot(grid[2, 0])
    _plot_certifications(cert_axis, certifications)

    figure.suptitle(
        "AWS Certification Coach Question Coverage",
        fontsize=CHART_FONT_SIZES["suptitle"],
        fontweight="bold",
    )
    figure.text(
        0.01,
        0.01,
        (
            f"Questions: {int(metrics.get('question_count', 0))} | "
            f"Domains: {int(metrics.get('domain_count', 0))} | "
            f"Concepts: {int(metrics.get('concept_count', 0))}"
        ),
        fontsize=CHART_FONT_SIZES["footer"],
        color="#57606a",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(figure)


def plot_question_coverage_artifacts(metrics: dict[str, object], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "domain": output_dir / "question_domain_coverage.png",
        "intent": output_dir / "question_intent_coverage.png",
        "certification": output_dir / "question_certification_coverage.png",
    }
    plot_domain_coverage(metrics, outputs["domain"])
    plot_question_intent_coverage(metrics, outputs["intent"])
    plot_certification_coverage(metrics, outputs["certification"])
    return outputs


def plot_domain_coverage(metrics: dict[str, object], output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    domains = _series(metrics.get("domains", []), limit=12)
    figure, axis = plt.subplots(figsize=(14, 7), constrained_layout=True)
    _plot_horizontal_bars(axis, domains, "Domain Coverage", "Question count", "#2f6f73")
    _add_footer(figure, metrics)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(figure)


def plot_question_intent_coverage(metrics: dict[str, object], output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    question_intents = _series(metrics.get("question_intents", []), limit=8)
    figure, axis = plt.subplots(figsize=(14, 7), constrained_layout=True)
    _plot_question_intents(axis, question_intents)
    _add_footer(figure, metrics)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(figure)


def plot_certification_coverage(metrics: dict[str, object], output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    certifications = _series(metrics.get("certifications", []), limit=8)
    figure, axis = plt.subplots(figsize=(10, 7), constrained_layout=True)
    _plot_certifications(axis, certifications)
    _add_footer(figure, metrics)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(figure)


def _text(value: object, fallback: str) -> str:
    text = str(value or "").strip()
    return text or fallback


def _concepts(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(concept, "") for concept in value if _text(concept, "")]


def _service_name(source_name: object) -> str:
    text = _text(source_name, "Unknown")
    prefix = "AWS Documentation:"
    if text.startswith(prefix):
        return text[len(prefix):].strip() or "Unknown"
    return text


def _question_intent(row: dict[str, object]) -> str:
    question_type = _text(row.get("question_type"), "")
    question = _text(row.get("question"), "")
    reference_answer = _text(row.get("reference_answer"), "")
    concepts = " ".join(_concepts(row.get("key_concepts")))
    haystack = f"{question_type} {question} {reference_answer} {concepts}".lower()

    if question_type == "service_comparison" or _has_any(
        haystack,
        [" compare ", " versus ", " vs ", " tradeoff", " trade-off", " near-miss", " next best"],
    ):
        return "Comparison tradeoff"
    if _has_any(
        haystack,
        ["troubleshoot", "diagnose", "latency", "error", "fail", "failed", "bottleneck", "optimize"],
    ):
        return "Troubleshooting or optimization"
    if _has_any(
        haystack,
        [
            "configure",
            "configuration",
            "setting",
            "policy",
            "rule",
            "timeout",
            "lifecycle",
            "authorizer",
            "rotation",
        ],
    ):
        return "Configuration decision"
    if _has_any(haystack, ["which aws service", "which service", "which feature", "should be used", "best fit"]):
        return "Service or feature selection"
    return "Concept explanation"


def _has_any(haystack: str, needles: list[str]) -> bool:
    return any(needle in haystack for needle in needles)


def _counter_rows(counter: Counter[str], limit: int | None = None) -> list[dict[str, object]]:
    items = counter.most_common(limit)
    return [{"name": name, "count": count} for name, count in items]


def _series(value: object, limit: int) -> list[tuple[str, int]]:
    if not isinstance(value, list):
        return []
    series = []
    for row in value[:limit]:
        if isinstance(row, dict):
            series.append((_text(row.get("name"), "Unknown"), int(row.get("count", 0))))
    return series


def _plot_horizontal_bars(
    axis: object,
    series: list[tuple[str, int]],
    title: str,
    xlabel: str,
    color: str,
) -> None:
    labels = [label for label, _ in series][::-1]
    values = [value for _, value in series][::-1]
    axis.barh(labels, values, color=color)
    axis.set_title(title, fontsize=CHART_FONT_SIZES["title"], pad=12)
    axis.set_xlabel(xlabel, fontsize=CHART_FONT_SIZES["axis"])
    axis.tick_params(axis="both", labelsize=CHART_FONT_SIZES["tick"])
    axis.grid(axis="x", color="#e5e7eb", linewidth=0.8)


def _plot_certifications(axis: object, series: list[tuple[str, int]]) -> None:
    labels = [label for label, _ in series]
    values = [value for _, value in series]
    colors = ["#4267ac", "#6f8f3d", "#b35f5f", "#756bb1", "#c98f2f", "#4f8f9f", "#7b6d5d", "#8a7bb8"]
    axis.pie(
        values,
        labels=labels,
        autopct=lambda pct: f"{pct:.0f}%" if pct >= 4 else "",
        startangle=90,
        colors=colors[: len(values)],
        textprops={"fontsize": CHART_FONT_SIZES["pie"]},
    )
    axis.set_title("Certification Split", fontsize=CHART_FONT_SIZES["title"], pad=12)


def _plot_question_intents(axis: object, series: list[tuple[str, int]]) -> None:
    labels = [label.replace("_", " ").title() for label, _ in series][::-1]
    values = [value for _, value in series][::-1]
    axis.barh(labels, values, color="#5e6c84")
    axis.set_title("Question Intent Mix", fontsize=CHART_FONT_SIZES["title"], pad=12)
    axis.set_xlabel("Question count", fontsize=CHART_FONT_SIZES["axis"])
    axis.tick_params(axis="both", labelsize=CHART_FONT_SIZES["tick"])
    axis.grid(axis="x", color="#e5e7eb", linewidth=0.8)


def _add_footer(figure: object, metrics: dict[str, object]) -> None:
    figure.text(
        0.01,
        0.01,
        (
            f"Questions: {int(metrics.get('question_count', 0))} | "
            f"Domains: {int(metrics.get('domain_count', 0))} | "
            f"Concepts: {int(metrics.get('concept_count', 0))}"
        ),
        fontsize=CHART_FONT_SIZES["footer"],
        color="#57606a",
    )
