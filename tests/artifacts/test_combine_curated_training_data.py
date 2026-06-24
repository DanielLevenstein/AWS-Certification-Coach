import json

from scripts.combine_curated_training_data import combine_curated_training_data


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
