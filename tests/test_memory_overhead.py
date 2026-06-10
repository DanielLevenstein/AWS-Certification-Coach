from pathlib import Path
import tracemalloc

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.evaluation.trained_classifier_provider import SUCCESS_THRESHOLD
from aws_certification_coach.questions.json_repository import JsonQuestionRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "sample_questions.json"
MAX_EVALUATION_OVERHEAD_BYTES = 20 * 1024 * 1024


def test_question_loading_and_evaluation_memory_overhead_stays_small():
    tracemalloc.start()
    try:
        repository = JsonQuestionRepository(QUESTION_ARTIFACT)
        questions = repository.all()
        service = build_evaluation_service()
        result = service.evaluate(questions[0], questions[0].reference_answer)
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    print(f"memory_overhead_peak_bytes={peak}")

    assert result.score >= SUCCESS_THRESHOLD
    assert peak <= MAX_EVALUATION_OVERHEAD_BYTES
