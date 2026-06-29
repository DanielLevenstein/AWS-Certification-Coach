"""Runtime visibility rules for question types."""

from __future__ import annotations

import os
from typing import Iterable

from aws_certification_coach.domain import Question


QUESTION_TYPE_ENV_FLAGS = {
    "artifact_review": "SHOW_ARTIFACT_REVIEW",
}


def visible_questions(questions: Iterable[Question]) -> list[Question]:
    return [question for question in questions if is_question_type_enabled(question.question_type)]


def visible_question_rows(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if is_question_type_enabled(str(row.get("question_type", "service_selection")))]


def is_question_type_enabled(question_type: str) -> bool:
    env_var = QUESTION_TYPE_ENV_FLAGS.get(question_type)
    return env_var is None or _env_enabled(env_var)


def _env_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}
