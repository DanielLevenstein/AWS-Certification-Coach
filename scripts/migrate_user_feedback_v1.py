"""Migrate legacy reviewed feedback records to the self-contained v1 schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.feedback.repository import build_feedback_record
from aws_certification_coach.questions.json_repository import JsonQuestionRepository


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/curated/user_feedback.json")
    parser.add_argument("--output", default="data/curated/user_feedback.v1.json")
    parser.add_argument("--questions", default="data/questions/sample_questions.json")
    args = parser.parse_args()

    questions = {
        question.question_id: question
        for question in JsonQuestionRepository(args.questions).all()
    }
    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    migrated = []
    for row in rows:
        question_id = str(row.get("question_id", ""))
        if question_id not in questions:
            raise ValueError(f"Feedback references unknown question ID: {question_id}")
        migrated.append(
            build_feedback_record(
                question=questions[question_id],
                answer_given=str(row["answer_given"]),
                rating_given=str(row["rating_given"]),
                correct_rating=str(row["correct_rating"]),
            )
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(migrated, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
