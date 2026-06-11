from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics
import unittest

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import LETTER_RATINGS, score_to_letter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATED_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_generated.json"


class TestGeneratedAnswerDistribution(unittest.TestCase):
    """Observe grade distributions without assuming that they follow a bell curve."""

    @classmethod
    def setUpClass(cls) -> None:
        rows = json.loads(GENERATED_ARTIFACT.read_text(encoding="utf-8"))
        questions = {
            question.question_id: question
            for question in JsonQuestionRepository(GENERATED_ARTIFACT).all()
        }
        service = build_evaluation_service()

        cls.observations = []
        for row in rows:
            question = questions[row["question_id"]]
            for example in row.get("generated_answers", []):
                result = service.evaluate(question, example["answer"])
                cls.observations.append(
                    {
                        "question_id": question.question_id,
                        "source": example.get("source", ""),
                        "expected_bucket": example["rating"],
                        "predicted_bucket": score_to_letter(result.score),
                        "score": result.score,
                    }
                )

    def test_full_generated_corpus_is_evaluated(self) -> None:
        self.assertGreater(len(self.observations), 0)
        expected_question_ids = {
            row["question_id"]
            for row in json.loads(GENERATED_ARTIFACT.read_text(encoding="utf-8"))
        }
        observed_question_ids = {
            observation["question_id"] for observation in self.observations
        }
        self.assertEqual(observed_question_ids, expected_question_ids)
        for observation in self.observations:
            with self.subTest(
                question_id=observation["question_id"],
                source=observation["source"],
            ):
                self.assertIn(observation["expected_bucket"], LETTER_RATINGS)
                self.assertIn(observation["predicted_bucket"], LETTER_RATINGS)

    def test_report_observed_grade_distribution(self) -> None:
        predicted = Counter(
            observation["predicted_bucket"] for observation in self.observations
        )
        expected = Counter(
            observation["expected_bucket"] for observation in self.observations
        )
        confusion_matrix: dict[str, Counter[str]] = defaultdict(Counter)
        for observation in self.observations:
            confusion_matrix[observation["expected_bucket"]][
                observation["predicted_bucket"]
            ] += 1

        scores = [observation["score"] for observation in self.observations]
        report = {
            "examples": len(self.observations),
            "mean_score": round(statistics.fmean(scores), 2),
            "median_score": statistics.median(scores),
            "predicted_buckets": _ordered_counts(predicted),
            "source_label_buckets": _ordered_counts(expected),
            "confusion_matrix": {
                expected_grade: _ordered_counts(confusion_matrix[expected_grade])
                for expected_grade in LETTER_RATINGS
            },
        }
        print("generated_answer_distribution " + json.dumps(report, sort_keys=True))

        self.assertEqual(sum(predicted.values()), len(self.observations))
        self.assertEqual(sum(expected.values()), len(self.observations))
        self.assertEqual(
            sum(sum(row.values()) for row in confusion_matrix.values()),
            len(self.observations),
        )


def _ordered_counts(counts: Counter[str]) -> dict[str, int]:
    return {grade: counts.get(grade, 0) for grade in LETTER_RATINGS}


if __name__ == "__main__":
    unittest.main()
