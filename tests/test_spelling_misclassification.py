from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import LETTER_RATINGS, score_to_letter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "sample_questions.json"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
IGNORED_OPTION_TOKENS = {"amazon", "aws", "service", "the", "use"}


class TestSpellingMisclassification(unittest.TestCase):
    """Characterize grading changes caused only by service-name misspellings."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.service = build_evaluation_service()
        cls.questions = JsonQuestionRepository(QUESTION_ARTIFACT).all()
        cls.observations = []

        for question in cls.questions:
            original = question.original_multiple_choice
            if original is None:
                continue
            correct_ids = set(original.correct_option_ids)
            for option in original.options:
                if option.option_id not in correct_ids:
                    continue
                misspelling = _misspell_option(option.text)
                if misspelling == option.text:
                    continue
                correct_result = cls.service.evaluate(question, option.text)
                misspelled_result = cls.service.evaluate(question, misspelling)
                cls.observations.append(
                    {
                        "question_id": question.question_id,
                        "correct_answer": option.text,
                        "misspelled_answer": misspelling,
                        "correct_score": correct_result.score,
                        "misspelled_score": misspelled_result.score,
                        "correct_bucket": score_to_letter(correct_result.score),
                        "misspelled_bucket": score_to_letter(misspelled_result.score),
                    }
                )

    def test_every_generated_spelling_case_is_graded(self) -> None:
        self.assertGreater(len(self.observations), 0)
        for observation in self.observations:
            with self.subTest(question_id=observation["question_id"]):
                self.assertIn(observation["correct_bucket"], LETTER_RATINGS)
                self.assertIn(observation["misspelled_bucket"], LETTER_RATINGS)

    def test_report_spelling_bucket_distribution(self) -> None:
        correct_distribution = Counter(
            observation["correct_bucket"] for observation in self.observations
        )
        misspelled_distribution = Counter(
            observation["misspelled_bucket"] for observation in self.observations
        )
        score_movements = Counter(
            "lower"
            if observation["misspelled_score"] < observation["correct_score"]
            else "higher"
            if observation["misspelled_score"] > observation["correct_score"]
            else "unchanged"
            for observation in self.observations
        )

        print(
            "spelling_characterization "
            f"cases={len(self.observations)} "
            f"correct={_ordered_counts(correct_distribution)} "
            f"misspelled={_ordered_counts(misspelled_distribution)} "
            f"score_movements={dict(score_movements)}"
        )

        self.assertEqual(sum(correct_distribution.values()), len(self.observations))
        self.assertEqual(sum(misspelled_distribution.values()), len(self.observations))
        self.assertEqual(sum(score_movements.values()), len(self.observations))


def _misspell_option(option_text: str) -> str:
    tokens = TOKEN_PATTERN.findall(option_text)
    candidates = [
        token
        for token in tokens
        if token.casefold() not in IGNORED_OPTION_TOKENS and len(token) >= 3
    ]
    if not candidates:
        return option_text
    target = candidates[-1]
    replacement = target[:-1] + _replacement_character(target[-1])
    return option_text.replace(target, replacement, 1)


def _replacement_character(character: str) -> str:
    replacement = "z" if character.casefold() != "z" else "x"
    return replacement.upper() if character.isupper() else replacement


def _ordered_counts(counts: Counter[str]) -> dict[str, int]:
    return {grade: counts.get(grade, 0) for grade in LETTER_RATINGS}


if __name__ == "__main__":
    unittest.main()
