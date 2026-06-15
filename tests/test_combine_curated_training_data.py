import json

import pytest

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


def test_rejects_question_ids_in_curated_training_data(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "curated_training_invalid.json").write_text(
        '[{"question_id": "Q1", "question": "Readable question"}]',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="question text, not question_id"):
        combine_curated_training_data(config_dir, tmp_path / "combined.json")
