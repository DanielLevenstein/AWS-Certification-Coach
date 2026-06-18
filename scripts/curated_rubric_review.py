#!/usr/bin/env python3
"""Review curated answer labels against the answer rubric and semantic scorer."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from aws_certification_coach.model_evaluation.semantic_similarity import semantic_similarity_score
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.dataset import load_feedback_regression_examples
from aws_certification_coach.training.features import correct_answer_text


def build_review(curated_path: Path, questions_path: Path) -> str:
    rows = json.loads(curated_path.read_text(encoding="utf-8"))
    questions = JsonQuestionRepository(questions_path).all()
    examples = load_feedback_regression_examples(curated_path, questions)
    suggestions = []
    grade_counts: Counter[str] = Counter()

    for index, (row, example) in enumerate(zip(rows, examples, strict=True)):
        expected = str(row["correct_rating"]).strip().upper()
        score = semantic_similarity_score(example.question, example.answer)
        suggested = score_to_letter(score)
        grade_counts[expected] += 1
        if suggested == expected:
            continue
        suggestions.append(
            {
                "row": index,
                "question": example.question.question,
                "answer": example.answer,
                "correct_answer": correct_answer_text(example.question),
                "current_rating": expected,
                "suggested_rating": suggested,
                "score": score,
                "reason": _suggestion_reason(expected, suggested, example.answer),
            }
        )

    lines = [
        "# Curated Rubric Review",
        "",
        f"- Curated examples reviewed: {len(rows)}",
        "- Rubric grades: `A`, `B`, `C`, `D`, `F`",
        f"- Current grade distribution: `{dict(sorted(grade_counts.items()))}`",
        f"- Suggested label updates: {len(suggestions)}",
        "",
        "## Suggested Answer Updates",
        "",
    ]
    if not suggestions:
        lines.append("- None. Current labels align with the standardized exact-letter rubric and scorer.")
        lines.append("")
    for suggestion in suggestions:
        lines.extend(
            [
                f"### Row {suggestion['row']}: {suggestion['current_rating']} -> {suggestion['suggested_rating']}",
                "",
                f"- Question: {suggestion['question']}",
                f"- Answer: `{suggestion['answer']}`",
                f"- Reference: {suggestion['correct_answer']}",
                f"- Semantic score: `{suggestion['score']}`",
                f"- Rationale: {suggestion['reason']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Release Table Recommendation",
            "",
            "Keep `Release`, `Semantic Accuracy`, `Semantic Precision`, `Semantic Recall`, and `Question Fidelity` in release notes.",
            "Calculate `Semantic Accuracy` as exact A/B/C/D/F letter-grade agreement on curated answer rows.",
            "Do not publish `Training Accuracy` or `Saved Accuracy`; keep those values in generated JSON artifacts only for model-training diagnostics.",
            "",
        ]
    )
    return "\n".join(lines)


def _suggestion_reason(current: str, suggested: str, answer: str) -> str:
    if suggested == "F":
        return "The answer does not identify the required service or enough relevant AWS reasoning for partial credit."
    if current == "F":
        return "The answer names an adjacent AWS concept, so the standardized rubric gives minimal partial credit instead of no credit."
    return "The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated", type=Path, default=Path("data/curated/curated_training_data.json"))
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/curated_rubric_review.md"))
    args = parser.parse_args()

    review = build_review(args.curated, args.questions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(review + "\n", encoding="utf-8")
    print(f"Curated rubric review: {args.output}")


if __name__ == "__main__":
    main()
