import json
from pathlib import Path

import pytest

from aws_certification_coach.knowledge_base import (
    DEFAULT_KNOWLEDGE_BASE_PATH,
    load_knowledge_base,
)
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.features import AnswerFeatureExtractor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STRUCTURED_TRAINING_DATA = PROJECT_ROOT / "config" / "data" / "structured_answer_training_data.json"


def test_default_knowledge_base_has_expected_first_version_sections():
    knowledge = load_knowledge_base()

    assert knowledge.schema_version == 2
    assert len(knowledge.syntax_aliases) == 18
    assert len(knowledge.services) == 42
    assert len(knowledge.concepts) == 161
    assert len(knowledge.common_misconceptions) >= 1
    assert len(knowledge.must_not_claim) >= 1
    assert not hasattr(knowledge, "rubric_profiles")


def test_knowledge_base_covers_every_structured_training_key_concept():
    rows = json.loads(STRUCTURED_TRAINING_DATA.read_text(encoding="utf-8"))
    expected = {str(concept) for row in rows for concept in row["key_concepts"]}
    knowledge = load_knowledge_base()

    assert expected <= {concept.name for concept in knowledge.concepts}
    assert all(concept.service_ids for concept in knowledge.concepts)
    assert all(concept.description for concept in knowledge.concepts)


def test_knowledge_base_exposes_feedback_flag_sections_with_sources():
    knowledge = load_knowledge_base()
    row = knowledge.common_misconceptions[0]

    assert row.key_concepts
    assert row.common_misconceptions
    assert row.acceptable_answers
    assert row.must_not_claim
    assert row.do_not_claim_explanation
    assert row.source_url.startswith("https://docs.aws.amazon.com/")
    assert row in knowledge.flag_sets_for_source_url(row.source_url)


def test_knowledge_base_normalizes_syntax_and_exposes_service_aliases():
    knowledge = load_knowledge_base()

    assert knowledge.canonicalize("AWS Code Build") == "aws codebuild"
    assert knowledge.canonicalize("Cloud Trail API activity") == "cloudtrail api activity"
    assert "aws cost center" in knowledge.aliases_for_service_token("budgets")
    assert knowledge.service_for_name("AWS Lambda").id == "lambda"
    assert knowledge.service_for_name("AWS Lambda").source_url.startswith("https://docs.aws.amazon.com/")


def test_knowledge_base_renders_only_relevant_bounded_context():
    knowledge = load_knowledge_base()
    selection = knowledge.select(
        ["SQS visibility timeout"],
        "Increase the message processing window.",
    )

    rendered = selection.render(max_characters=700)

    assert "CONCEPT: SQS visibility timeout" in rendered
    assert "CONCEPT: processing window" in rendered
    assert "SERVICES: Amazon SQS" in rendered
    assert "AWS KMS" not in rendered
    assert len(rendered) <= 700


def test_knowledge_base_loader_is_cached():
    assert load_knowledge_base() is load_knowledge_base(DEFAULT_KNOWLEDGE_BASE_PATH)


def test_knowledge_base_rejects_answer_labels(tmp_path: Path):
    payload = json.loads(DEFAULT_KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8"))
    payload["concepts"][0]["rating"] = 0.95
    invalid = tmp_path / "invalid_knowledge.json"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="answer-label fields"):
        load_knowledge_base(invalid)


def test_classifier_features_use_knowledge_base_syntax_aliases():
    questions = JsonQuestionRepository(STRUCTURED_TRAINING_DATA).all()
    question = next(question for question in questions if "managed build project" in question.question)
    extractor = AnswerFeatureExtractor(answer_form="both")

    joined_name_features = extractor.extract(question, "Use AWS CodeBuild.")
    spaced_name_features = extractor.extract(question, "Use AWS Code Build.")

    assert spaced_name_features == joined_name_features
