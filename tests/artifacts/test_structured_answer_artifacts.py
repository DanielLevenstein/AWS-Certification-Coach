from pathlib import Path

import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STRUCTURED_ANSWER_DATA = PROJECT_ROOT / "config" / "data" / "structured_answer_training_data.json"


def test_structured_answer_data_preserves_knowledge_base_seed_schema():
    questions = json.loads(STRUCTURED_ANSWER_DATA.read_text(encoding="utf-8"))

    assert questions
    assert all(question["key_concepts"] for question in questions)
    assert all(question["partial_answers"] for question in questions)
    assert {
        str(answer["source"])
        for question in questions
        for answer in question["partial_answers"]
    } == {"structured_answer_test_case"}
