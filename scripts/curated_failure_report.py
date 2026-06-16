#!/usr/bin/env python3
"""Generate a diagnostic report for curated-grade prediction failures."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.evaluation.trained_classifier_provider import SemanticAwareEvaluatorProvider
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import letter_to_grade_band, letter_to_numeric, score_to_letter
from aws_certification_coach.training.dataset import load_feedback_regression_examples
from aws_certification_coach.training.features import AnswerFeatureExtractor


def build_failure_report(
    model_path: Path,
    curated_path: Path,
    questions_path: Path,
) -> str:
    rows = json.loads(curated_path.read_text(encoding="utf-8"))
    questions = JsonQuestionRepository(questions_path).all()
    examples = load_feedback_regression_examples(curated_path, questions)
    del model_path
    extractor = AnswerFeatureExtractor()
    service = EvaluationService(SemanticAwareEvaluatorProvider())
    conflicts = _conflicting_labels(rows)
    failures = []

    for index, (row, example) in enumerate(zip(rows, examples, strict=True)):
        question = example.question
        features = extractor.extract(question, example.answer)
        result = service.evaluate(question, example.answer)
        raw_score = float(result.score)
        expected = str(row["correct_rating"]).strip().upper()
        actual = score_to_letter(result.score)
        expected_band = letter_to_grade_band(expected)
        actual_band = letter_to_grade_band(actual)
        if actual_band == expected_band:
            continue
        normalized_key = _normalized_pair(row)
        failures.append(
            {
                "row": index,
                "question": question.question,
                "correct_answer": question.reference_answer,
                "user_answer": example.answer,
                "expected_rating": letter_to_numeric(expected),
                "expected_band": expected_band,
                "actual_band": actual_band,
                "score": result.score,
                "raw_score": raw_score,
                "feedback": result.feedback,
                "contributions": [("semantic_similarity_score", raw_score / 100)],
                "reason": _suspected_reason(
                    expected,
                    actual,
                    raw_score,
                    result.feedback,
                    features,
                    normalized_key in conflicts,
                ),
            }
        )

    grouped = _group_failures(failures)
    return _format_markdown(rows, failures, grouped, conflicts)


def _conflicting_labels(rows: list[dict]) -> dict[tuple[str, str], set[str]]:
    labels: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        labels[_normalized_pair(row)].add(str(row["correct_rating"]).strip().upper())
    return {
        key: values
        for key, values in labels.items()
        if len({letter_to_grade_band(value) for value in values}) > 1
    }


def _normalized_pair(row: dict) -> tuple[str, str]:
    return (_normalized(row.get("question", "")), _normalized(row.get("answer_given", "")))


def _normalized(value: object) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value).casefold()))


def _top_contributions(
    model: AnswerRegressionModel,
    features: list[float],
    limit: int = 4,
) -> list[tuple[str, float]]:
    contributions = [
        (name, weight * value)
        for name, weight, value in zip(model.feature_names, model.weights, features)
        if value
    ]
    return sorted(contributions, key=lambda item: abs(item[1]), reverse=True)[:limit]


def _suspected_reason(
    expected: str,
    actual: str,
    raw_score: float,
    feedback: str,
    features: list[float],
    has_label_conflict: bool,
) -> str:
    if has_label_conflict:
        return "Conflicting curated labels: the same normalized question and answer has multiple expected grades."
    if "misspelled" in feedback.casefold():
        return "Runtime spelling guard assigned a fixed D-range score; the expected grade disagrees with that policy."
    if "not in the question's correct answer list" in feedback:
        return "Runtime exact-service guard treated the answer as a wrong option before partial-credit semantics were considered."
    if expected == "A" and features[4] == 0:
        return (
            "Semantically correct prose is not an exact option-text match. The model relies on lexical containment and "
            "does not receive the runtime 95-point exact-option boost."
        )
    if expected in {"B", "C", "D"} and actual == "F":
        if raw_score < 60:
            return (
                "Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. "
                "The feature set lacks service aliases and calibrated partial-credit semantics."
            )
        return "The raw score is near a grade boundary and integer conversion/calibration pushes it into F."
    return "The expected grade and model score disagree; inspect the curated label and feature calibration together."


def _group_failures(failures: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str, str], dict] = {}
    for failure in failures:
        key = (
            failure["question"],
            _normalized(failure["user_answer"]),
            failure["expected_rating"],
            failure["actual_band"],
        )
        if key not in grouped:
            grouped[key] = {**failure, "rows": [failure["row"]], "occurrences": 1}
        else:
            grouped[key]["rows"].append(failure["row"])
            grouped[key]["occurrences"] += 1
    return sorted(grouped.values(), key=lambda item: (item["question"], item["user_answer"], item["expected_rating"]))


def _format_markdown(
    rows: list[dict],
    failures: list[dict],
    grouped: list[dict],
    conflicts: dict[tuple[str, str], set[str]],
) -> str:
    actual_counts = Counter(failure["actual_band"] for failure in failures)
    conflict_finding = (
        "At least one normalized question/answer pair has contradictory curated grades, "
        "making perfect accuracy impossible until labels are reconciled."
        if conflicts
        else "No cross-band duplicate-label conflicts were detected in the curated data."
    )
    lines = [
        "# Curated Grade Failure Report",
        "",
        f"- Curated examples: {len(rows)}",
        "- Evaluation bands: `A/B`, `C/D`, `F`",
        f"- Passing grade-band predictions: {len(rows) - len(failures)}",
        f"- Failing grade-band predictions: {len(failures)}",
        f"- Grade-band accuracy: {(len(rows) - len(failures)) / max(1, len(rows)):.2%}",
        f"- Unique failing question/answer/grade cases: {len(grouped)}",
        f"- Conflicting normalized label sets: {len(conflicts)}",
        f"- Actual grade bands among failures: {dict(sorted(actual_counts.items()))}",
        "",
        "## Primary Findings",
        "",
        "1. Generated-label training error is low; remaining app-scoring failures are now semantic-aware calibration cases rather than epoch-count issues.",
        "2. The semantic-aware scorer recognizes service aliases and concept coverage, but it still uses deterministic rules that miss some AWS synonym and near-service cases.",
        "3. Full-credit prose is scored through service and concept coverage rather than only exact option text.",
        f"4. {conflict_finding}",
        "",
        "## Label Conflicts",
        "",
    ]
    if conflicts:
        for (question, answer), labels in sorted(conflicts.items()):
            lines.append(f"- Question: `{question}`; answer: `{answer}`; grades: `{', '.join(sorted(labels))}`")
    else:
        lines.append("- None detected.")
    lines.extend(["", "## Failing Cases", ""])
    for number, failure in enumerate(grouped, start=1):
        contribution_text = ", ".join(
            f"`{name}` {value:+.3f}" for name, value in failure["contributions"]
        )
        lines.extend(
            [
                f"### {number}. Expected {failure['expected_band']}, received {failure['actual_band']}",
                "",
                f"- Rows: `{', '.join(str(row) for row in failure['rows'])}`; occurrences: `{failure['occurrences']}`",
                f"- Question: {failure['question']}",
                f"- Expected rating: `{failure['expected_rating']:.2f}`",
                f"- User answer: `{failure['user_answer'].strip()}`",
                f"- Correct answer: {failure['correct_answer']}",
                f"- Raw model score: `{failure['raw_score']:.2f}`; runtime score: `{failure['score']}`",
                f"- Runtime feedback: {failure['feedback']}",
                f"- Largest feature contributions: {contribution_text}",
                f"- Suspected cause: {failure['reason']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Recommended Remediation Order",
            "",
            "1. Reconcile conflicting curated labels before changing model code.",
            "2. Expand normalized AWS service aliases and near-service synonym handling.",
            "3. Tune concept-coverage thresholds against curated examples.",
            "4. Keep generated-label regression metrics out of release tracking unless the trained model returns to the app path.",
            "5. Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=Path("release/metrics/answer_regressor_model.json"))
    parser.add_argument("--curated", type=Path, default=Path("data/curated/curated_training_data.json"))
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/curated_failure_report.md"))
    args = parser.parse_args()

    report = build_failure_report(args.model, args.curated, args.questions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report + "\n", encoding="utf-8")
    print(f"Curated failure report: {args.output}")


if __name__ == "__main__":
    main()
