#!/usr/bin/env python3
"""Generate a diagnostic report for curated-grade prediction failures."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.evaluation.trained_classifier_provider import TrainedRegressionEvaluatorProvider
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import letter_to_grade_band, score_to_letter
from aws_certification_coach.training.answer_classifier import AnswerRegressionModel
from aws_certification_coach.training.dataset import load_feedback_regression_examples
from aws_certification_coach.training.features import AnswerFeatureExtractor


def build_failure_report(
    model_path: Path,
    curated_path: Path,
    questions_path: Path,
) -> str:
    rows = json.loads(curated_path.read_text(encoding="utf-8"))
    questions = JsonQuestionRepository(questions_path).all()
    questions_by_id = {question.question_id: question for question in questions}
    examples = load_feedback_regression_examples(curated_path, questions_by_id)
    model = AnswerRegressionModel.load(model_path)
    extractor = AnswerFeatureExtractor()
    service = EvaluationService(TrainedRegressionEvaluatorProvider(model, extractor))
    conflicts = _conflicting_labels(rows)
    failures = []

    for index, (row, example) in enumerate(zip(rows, examples, strict=True)):
        question = questions_by_id[example.question_id]
        features = extractor.extract(question, example.answer)
        raw_score = model.predict(features) * 100
        result = service.evaluate(question, example.answer)
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
                "reference_answer": question.reference_answer,
                "answer": example.answer,
                "expected": expected,
                "actual": actual,
                "expected_band": expected_band,
                "actual_band": actual_band,
                "score": result.score,
                "raw_score": raw_score,
                "feedback": result.feedback,
                "contributions": _top_contributions(model, features),
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
            _normalized(failure["answer"]),
            failure["expected"],
            failure["actual"],
        )
        if key not in grouped:
            grouped[key] = {**failure, "rows": [failure["row"]], "occurrences": 1}
        else:
            grouped[key]["rows"].append(failure["row"])
            grouped[key]["occurrences"] += 1
    return sorted(grouped.values(), key=lambda item: (item["question"], item["answer"], item["expected"]))


def _format_markdown(
    rows: list[dict],
    failures: list[dict],
    grouped: list[dict],
    conflicts: dict[tuple[str, str], set[str]],
) -> str:
    actual_counts = Counter(failure["actual"] for failure in failures)
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
        f"- Actual grades among failures: {dict(sorted(actual_counts.items()))}",
        "",
        "## Primary Findings",
        "",
        "1. Training error is low; remaining failures cross the broader A/B, C/D, and F boundaries, indicating a calibration/generalization problem rather than insufficient epochs.",
        "2. The feature extractor is lexical. It does not encode AWS aliases, semantic equivalence, or calibrated partial-credit concepts.",
        "3. Full-credit prose does not receive the exact-option boost unless it exactly matches a multiple-choice option.",
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
                f"- Letter grades: expected `{failure['expected']}`, received `{failure['actual']}`",
                f"- Curated answer: `{failure['answer'].strip()}`",
                f"- Reference answer: {failure['reference_answer']}",
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
            "2. Add normalized AWS service aliases and semantic service-match features.",
            "3. Add concept-coverage features that are independent of full reference-answer overlap.",
            "4. Calibrate grade boundaries against curated examples rather than relying only on regression MSE.",
            "5. Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=Path("release/metrics/partial_answer_regressor.json"))
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
