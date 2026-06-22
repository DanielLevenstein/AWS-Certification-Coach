import json

from aws_certification_coach.config import LocalSemanticModelConfig, load_evaluator_config
from aws_certification_coach.domain import Question
from aws_certification_coach.evaluation.sentence_transformer_provider import (
    SentenceTransformerEvaluatorProvider,
    resolve_device,
)


class FakeEncoder:
    def encode(self, sentences, *, normalize_embeddings):
        assert normalize_embeddings is True
        return [self._vector(text) for text in sentences]

    @staticmethod
    def _vector(text):
        normalized = text.casefold()
        if "visibility" in normalized:
            return [1.0, 0.0]
        if "fifo" in normalized:
            return [0.0, 1.0]
        return [0.70710678, 0.70710678]


class FakeClassifier:
    def predict(self, features):
        return ["A" if row[-2] > 0.5 else "F" for row in features]


def _question():
    return Question(
        certification="AWS Certified Developer",
        domain="Application Integration",
        difficulty="Medium",
        question="Which SQS setting hides a message during processing?",
        reference_answer="Adjust the SQS visibility timeout.",
        key_concepts=["SQS visibility timeout"],
        required_concepts=["SQS visibility timeout"],
        acceptable_answers=["SQS visibility timeout"],
        common_misconceptions=["SQS FIFO queue"],
    )


def test_device_defaults_to_accelerator_auto_selection():
    assert resolve_device(LocalSemanticModelConfig(device="auto")) is None
    assert resolve_device(LocalSemanticModelConfig(device="cuda")) == "cuda"


def test_cpu_only_override_wins_over_configured_accelerator():
    config = LocalSemanticModelConfig(device="cuda", cpu_only=True)

    assert resolve_device(config) == "cpu"


def test_local_provider_uses_semantic_and_structured_anchors(tmp_path):
    structured_path = tmp_path / "structured.json"
    question = _question()
    structured_path.write_text(
        json.dumps(
            [
                {
                    "question": question.question,
                    "partial_answers": [
                        {"answer": "SQS visibility timeout", "rating": 0.95},
                        {"answer": "SQS FIFO queue", "rating": 0.25},
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    provider = SentenceTransformerEvaluatorProvider(
        LocalSemanticModelConfig(structured_answer_data_path=str(structured_path)),
        encoder=FakeEncoder(),
        classifier=FakeClassifier(),
    )

    correct = json.loads(provider.evaluate("ignored", question, "SQS visibility timeout"))
    incorrect = json.loads(provider.evaluate("ignored", question, "SQS FIFO queue"))

    assert correct["score"] >= 90
    assert incorrect["score"] < 60


def test_cpu_only_environment_flag_is_loaded(tmp_path, monkeypatch):
    config_path = tmp_path / "evaluator.json"
    config_path.write_text(
        json.dumps({"provider": "sentence_transformer", "local_semantic": {"device": "auto"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("AWS_COACH_CPU_ONLY", "1")

    config = load_evaluator_config(config_path)

    assert config.local_semantic.cpu_only is True
