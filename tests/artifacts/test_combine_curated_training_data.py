import json
from collections import Counter
from pathlib import Path

from scripts.combine_curated_training_data import combine_curated_training_data, curated_training_input_paths


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIN_CURATED_EXAMPLES_PER_GRADE = 10


def test_combines_curated_training_fragments_in_filename_order(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "curated_training_b.json").write_text(
        '[{"question": "JSON question", "answer_given": "answer"}]',
        encoding="utf-8",
    )
    (config_dir / "curated_training_a.data").write_text(
        '[{"question": "Data question", "answer_given": "answer"}]',
        encoding="utf-8",
    )
    (config_dir / "unrelated.json").write_text('[{"id": "ignored"}]', encoding="utf-8")
    output = tmp_path / "data" / "curated" / "curated_training_data.json"

    file_count, row_count = combine_curated_training_data(config_dir, output)

    assert file_count == 2
    assert row_count == 2
    assert json.loads(output.read_text(encoding="utf-8")) == [
        {"question": "Data question", "answer_given": "answer"},
        {"question": "JSON question", "answer_given": "answer"},
    ]


def test_combiner_keeps_only_supported_curated_fields(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "curated_training_extra.json").write_text(
        '[{"question": "Readable question", "answer_given": "answer", "extra": "ignored"}]',
        encoding="utf-8",
    )

    output = tmp_path / "combined.json"
    combine_curated_training_data(config_dir, output)

    assert json.loads(output.read_text(encoding="utf-8")) == [
        {"question": "Readable question", "answer_given": "answer"}
    ]


def test_combiner_preserves_feedback_text_and_correct_answer_text(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "curated_training_extra.json").write_text(
        json.dumps(
            [
                {
                    "schema_version": 2,
                    "question": "Readable question",
                    "exam_code": "DVA-C02",
                    "reference_answer": "Use the exact service.",
                    "answer_given": "Near miss",
                    "correct_rating": "C",
                    "rating_given": "F",
                    "correct_answer_text": "Use the exact service.",
                    "feedback_text": "Treat this as a partial-credit near miss.",
                    "extra": "ignored",
                }
            ]
        ),
        encoding="utf-8",
    )

    output = tmp_path / "combined.json"
    combine_curated_training_data(config_dir, output)

    assert json.loads(output.read_text(encoding="utf-8")) == [
        {
            "schema_version": 2,
            "question": "Readable question",
            "exam_code": "DVA-C02",
            "reference_answer": "Use the exact service.",
            "answer_given": "Near miss",
            "correct_rating": "C",
            "rating_given": "F",
            "correct_answer_text": "Use the exact service.",
            "feedback_text": "Treat this as a partial-credit near miss.",
        }
    ]


def test_combiner_includes_generated_curated_fragments(tmp_path):
    config_dir = tmp_path / "config"
    generated_dir = tmp_path / "generated"
    config_dir.mkdir()
    generated_dir.mkdir()
    (config_dir / "curated_training_data.json").write_text(
        json.dumps(
            [
                {
                    "question": "Readable question",
                    "reference_answer": "Use the exact service.",
                    "answer_given": "Correct service",
                    "correct_rating": "A",
                    "rating_given": "A",
                }
            ]
        ),
        encoding="utf-8",
    )
    (generated_dir / "curated_training_question_rewordings.json").write_text(
        json.dumps(
            [
                {
                    "schema_version": 2,
                    "question": "Readable question",
                    "reference_answer": "Use the exact service.",
                    "answer_given": "This question asks which service is exact.",
                    "correct_rating": "D",
                    "rating_given": "A",
                    "feedback_text": "Generated question-restatement negative example.",
                }
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "combined.json"

    file_count, row_count = combine_curated_training_data(config_dir, output, generated_dir)

    rows = json.loads(output.read_text(encoding="utf-8"))
    assert file_count == 2
    assert row_count == 2
    assert [row["answer_given"] for row in rows] == [
        "Correct service",
        "This question asks which service is exact.",
    ]


def test_combiner_deduplicates_matching_curated_rows(tmp_path):
    config_dir = tmp_path / "config"
    generated_dir = tmp_path / "generated"
    config_dir.mkdir()
    generated_dir.mkdir()
    duplicate = {
        "schema_version": 2,
        "question": "Readable question",
        "reference_answer": "Use the exact service.",
        "answer_given": "This question asks which service is exact.",
        "correct_rating": "D",
        "rating_given": "A",
        "feedback_text": "Question-restatement negative example.",
    }
    (config_dir / "curated_training_data.json").write_text(
        json.dumps([duplicate]),
        encoding="utf-8",
    )
    generated_duplicate = dict(duplicate)
    generated_duplicate["question"] = "  readable   QUESTION  "
    generated_duplicate["answer_given"] = "This question asks which service is exact.  "
    (generated_dir / "curated_training_question_rewordings.json").write_text(
        json.dumps([generated_duplicate]),
        encoding="utf-8",
    )
    output = tmp_path / "combined.json"

    file_count, row_count = combine_curated_training_data(config_dir, output, generated_dir)

    assert file_count == 2
    assert row_count == 1
    assert json.loads(output.read_text(encoding="utf-8")) == [duplicate]


def test_config_curated_training_sources_cover_each_grade_letter():
    rows = []
    for path in curated_training_input_paths(PROJECT_ROOT / "config" / "data"):
        rows.extend(json.loads(path.read_text(encoding="utf-8")))

    distribution = Counter(
        str(row.get("correct_rating", "")).strip().upper()
        for row in rows
        if row.get("correct_rating")
    )

    assert all(distribution[grade] >= MIN_CURATED_EXAMPLES_PER_GRADE for grade in
               "ABCDF"), f"Grades failing: {[grade for grade in 'ABCDF' if distribution[grade] < MIN_CURATED_EXAMPLES_PER_GRADE]}"
