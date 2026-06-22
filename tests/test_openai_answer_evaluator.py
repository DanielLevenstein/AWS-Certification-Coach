import json
from types import SimpleNamespace

from aws_certification_coach.config import OpenAIModelConfig, load_evaluator_config
from aws_certification_coach.domain import Question
from aws_certification_coach.evaluation.structured_answer_context import StructuredAnswerContext
from aws_certification_coach.llm.openai_provider import OpenAIEvaluatorProvider


def _question(text: str = "Which setting prevents duplicate SQS processing?") -> Question:
    return Question(
        certification="AWS Certified Developer",
        domain="Application Integration",
        difficulty="Medium",
        question=text,
        reference_answer="Adjust the SQS visibility timeout.",
        key_concepts=["SQS visibility timeout"],
        required_concepts=["SQS visibility timeout"],
    )


def _structured_data(path, question_text: str) -> None:
    path.write_text(
        json.dumps(
            [
                {
                    "question": question_text,
                    "reference_answer": "Adjust the SQS visibility timeout.",
                    "required_concepts": ["SQS visibility timeout"],
                    "acceptable_answers": ["SQS visibility timeout"],
                    "common_misconceptions": ["SQS FIFO queue"],
                    "must_not_claim": ["FIFO controls message visibility"],
                    "partial_answers": [
                        {"answer": "SQS visibility timeout", "rating": 0.95},
                        {"answer": "SQS FIFO queue", "rating": 0.25},
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )


def test_structured_context_returns_only_question_matched_examples(tmp_path):
    data_path = tmp_path / "structured.json"
    question = _question()
    _structured_data(data_path, question.question)
    context = StructuredAnswerContext(data_path)

    matched = context.for_question(question)
    unmatched = context.for_question(_question("Which service stores objects?"))

    assert '"expected_letter": "A"' in matched
    assert '"expected_letter": "F"' in matched
    assert "not as an exact-text requirement" in matched
    assert unmatched == ""


def test_openai_provider_uses_gpt54_and_includes_structured_context(tmp_path, monkeypatch):
    data_path = tmp_path / "structured.json"
    question = _question()
    _structured_data(data_path, question.question)
    captured = {}

    class FakeResponses:
        def create(self, **request):
            captured.update(request)
            return SimpleNamespace(
                output_text=(
                    '{"score": 95, "missing_concepts": [], "suggested_improvements": [], '
                    '"feedback": "Correct", "detailed_answer": "Use the visibility timeout."}'
                )
            )

    class FakeOpenAI:
        def __init__(self):
            self.responses = FakeResponses()

    monkeypatch.setitem(__import__("sys").modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    provider = OpenAIEvaluatorProvider(
        OpenAIModelConfig(model="gpt-5.4"),
        structured_answer_data_path=str(data_path),
    )

    provider.evaluate("Base grading prompt", question, "SQS visibility timeout")

    assert captured["model"] == "gpt-5.4"
    prompt = captured["input"][1]["content"]
    assert "Base grading prompt" in prompt
    assert "Structured grading evidence for this exact question" in prompt
    assert "SQS FIFO queue" in prompt


def test_evaluator_config_selects_openai_gpt54_and_structured_data(tmp_path):
    config_path = tmp_path / "evaluator.json"
    config_path.write_text(
        json.dumps(
            {
                "provider": "openai",
                "openai": {
                    "model": "gpt-5.4",
                    "structured_answer_data_path": "config/data/structured_answer_training_data.json",
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_evaluator_config(config_path)

    assert config.provider == "openai"
    assert config.openai.model == "gpt-5.4"
    assert config.structured_answer_data_path == "config/data/structured_answer_training_data.json"
