from pathlib import Path

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.questions.json_repository import JsonQuestionRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "transformed_freeform_generated.json"


def test_trained_classifier_accepts_shortened_correct_answers():
    service = build_evaluation_service()
    questions = JsonQuestionRepository(QUESTION_ARTIFACT).all()[:10]

    for question in questions:
        shortened_answer = _drop_every_nth_word(question.reference_answer, 4)
        result = service.evaluate(question, shortened_answer)

        assert result.score == 100, (
            f"{question.question_id} should accept shortened correct answer: "
            f"{shortened_answer!r}. Feedback: {result.feedback}"
        )
        assert "classifier" not in result.feedback.lower()
        assert "confidence" not in result.feedback.lower()


def test_trained_classifier_returns_low_score_for_unrelated_answers():
    service = build_evaluation_service()
    question = JsonQuestionRepository(QUESTION_ARTIFACT).all()[0]

    result = service.evaluate(question, "This should use a totally unrelated service.")

    assert result.score <= 50


def _drop_every_nth_word(value: str, n: int) -> str:
    words = value.split()
    kept = [word for index, word in enumerate(words, start=1) if index % n != 0]
    return " ".join(kept) if kept else value
