"""In-memory quiz session state."""

from __future__ import annotations

import random

from aws_certification_coach.domain import AnsweredQuestion, EvaluationResult, Question


class QuizSession:
    """Tracks progress through a single filtered question set."""

    def __init__(self, questions: list[Question], *, shuffle: bool = True, seed: int | None = None) -> None:
        self.questions = list(questions)
        if shuffle:
            random.Random(seed).shuffle(self.questions)
        self.current_index = 0
        self.completed: list[AnsweredQuestion] = []

    def current_question(self) -> Question | None:
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def record_answer(
        self,
        question: Question,
        user_answer: str,
        evaluation: EvaluationResult,
    ) -> None:
        if any(answered.question == question for answered in self.completed):
            return
        self.completed.append(AnsweredQuestion(question, user_answer, evaluation))

    def advance(self) -> None:
        self.current_index += 1

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.questions)

    @property
    def score_history(self) -> list[int]:
        return [answered.evaluation.score for answered in self.completed]

    @property
    def average_score(self) -> float:
        scores = self.score_history
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
