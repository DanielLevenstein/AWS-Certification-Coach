from pathlib import Path

import json

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.questions.json_repository import JsonQuestionRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "training" / "questions_with_answers_generated.json"
APP_QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "sample_questions.json"


def test_trained_classifier_accepts_shortened_correct_answers():
    service = build_evaluation_service()
    questions = JsonQuestionRepository(QUESTION_ARTIFACT).all()[:10]

    for question in questions:
        shortened_answer = _drop_every_nth_word(question.reference_answer, 4)
        result = service.evaluate(question, shortened_answer)

        assert result.score > 50, (
            f"{question.question_id} should accept shortened correct answer: "
            f"{shortened_answer!r}. Feedback: {result.feedback}"
        )
        assert result.score < 100
        assert "classifier" not in result.feedback.lower()
        assert "confidence" not in result.feedback.lower()


def test_trained_classifier_rejects_incorrect_service_answers():
    service = build_evaluation_service()
    questions = JsonQuestionRepository(APP_QUESTION_ARTIFACT).all()
    service_answers = sorted(
        {
            option.text
            for question in questions
            for option in question.original_multiple_choice.options
        }
    )

    failures = []
    for question in questions:
        correct_answers = _correct_option_texts(question)
        for answer in service_answers:
            if _normalized(answer) in correct_answers:
                continue
            result = service.evaluate(question, answer)
            if result.score > 50:
                failures.append((question.question_id, result.score, answer, result.feedback))

    assert not failures


def test_trained_classifier_rejects_low_partial_credit_answers():
    service = build_evaluation_service()
    questions = {question.question_id: question for question in JsonQuestionRepository(QUESTION_ARTIFACT).all()}
    raw_questions = json.loads(QUESTION_ARTIFACT.read_text(encoding="utf-8"))

    failures = []
    for row in raw_questions:
        question = questions[row["question_id"]]
        for answer in row.get("partial_answers", []):
            if answer.get("rating_bucket") != 0.25:
                continue
            result = service.evaluate(question, answer["answer"])
            if result.score > 50:
                failures.append((question.question_id, result.score, answer["answer"], result.feedback))

    assert not failures


def _drop_every_nth_word(value: str, n: int) -> str:
    words = value.split()
    kept = [word for index, word in enumerate(words, start=1) if index % n != 0]
    return " ".join(kept) if kept else value


def _correct_option_texts(question) -> set[str]:
    original = question.original_multiple_choice
    correct_ids = set(original.correct_option_ids)
    return {
        _normalized(option.text)
        for option in original.options
        if option.option_id in correct_ids
    }


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace(".", "").split())
