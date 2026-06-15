import json
from pathlib import Path

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.dataset import load_feedback_regression_examples


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CURATED_TRAINING_DATA = PROJECT_ROOT / "data" / "curated" / "curated_training_data.json"
APP_QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "sample_questions.json"


def test_app_grades_match_all_curated_training_data():
    rows = json.loads(CURATED_TRAINING_DATA.read_text(encoding="utf-8"))
    questions = JsonQuestionRepository(APP_QUESTION_ARTIFACT).all()
    questions_by_id = {question.question_id: question for question in questions}
    examples = load_feedback_regression_examples(CURATED_TRAINING_DATA, questions_by_id)
    service = build_evaluation_service()

    assert len(examples) == len(rows)

    mismatches = []
    for index, (row, example) in enumerate(zip(rows, examples, strict=True)):
        result = service.evaluate(questions_by_id[example.question_id], example.answer)
        expected_grade = str(row["correct_rating"]).strip().upper()
        actual_grade = score_to_letter(result.score)
        if actual_grade != expected_grade:
            mismatches.append(
                f"row {index}: {example.question_id}, answer={example.answer!r}, "
                f"expected={expected_grade}, actual={actual_grade} ({result.score}/100)"
            )

    assert not mismatches, "Curated grading mismatches:\n" + "\n".join(mismatches)
