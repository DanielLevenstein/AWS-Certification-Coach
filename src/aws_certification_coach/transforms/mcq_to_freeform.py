"""Transform multiple-choice questions into freeform study prompts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Protocol


@dataclass(frozen=True)
class TransformationModelConfig:
    model: str = "gpt-5.4"
    temperature: float = 0.1
    top_p: float = 1.0
    max_output_tokens: int = 1200
    reasoning_effort: str | None = "medium"


class TransformationProvider(Protocol):
    def transform(self, prompt: str) -> str:
        """Return JSON text for one transformed question."""


class TransformationPromptBuilder:
    """Builds a conversion prompt for preserving exam intent without answer cues."""

    def build(self, source_item: dict) -> str:
        return f"""Convert this AWS certification multiple-choice item into a freeform paragraph-answer study question.

Rules:
- Preserve the exam objective, service names, constraints, and scenario.
- Remove answer-choice cues from the learner-facing freeform question.
- Produce an answer paragraph that explains the correct concept, not just the selected option.
- Include key concepts that should be present in a strong answer.
- For each must_not_claim item, include a matching do_not_claim_explanation item explaining why the correct service or pattern is better than that distractor.
- Keep the original multiple-choice item unchanged in original_multiple_choice.
- Return JSON only using the schema shown below.

Output schema:
{{
  "certification": string,
  "domain": string,
  "difficulty": string,
  "question_type": "multiple_choice" | "scenario_multiple_choice" | "multi_select_source" | "service_selection" | "service_comparison" | "architecture_tradeoff",
  "question": string,
  "reference_answer": string,
  "key_concepts": [string],
  "required_concepts": [string],
  "bonus_concepts": [string],
  "common_misconceptions": [string],
  "acceptable_answers": [string],
  "must_not_claim": [string],
  "do_not_claim_explanation": [string],
  "original_multiple_choice": object
}}

Source item:
{json.dumps(source_item, indent=2)}
"""


class MultipleChoiceToFreeformTransformer:
    """Converts source MCQ records into app-ready freeform records."""

    def __init__(
        self,
        provider: TransformationProvider,
        prompt_builder: TransformationPromptBuilder | None = None,
    ) -> None:
        self.provider = provider
        self.prompt_builder = prompt_builder or TransformationPromptBuilder()

    def transform_many(self, source_items: list[dict]) -> list[dict]:
        return [self.transform_one(item) for item in source_items]

    def transform_one(self, source_item: dict) -> dict:
        prompt = self.prompt_builder.build(source_item)
        response_text = self.provider.transform(prompt)
        transformed = json.loads(response_text)
        if not isinstance(transformed, dict):
            raise ValueError("Transformation provider must return a JSON object.")
        return transformed


class OpenAITransformationProvider:
    """High-quality transformer backed by the OpenAI Responses API."""

    SYSTEM_PROMPT = "You transform AWS exam-style questions into freeform study questions. Return JSON only."

    def __init__(self, config: TransformationModelConfig | None = None) -> None:
        self.config = config or TransformationModelConfig()

    def transform(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI()
        request = {
            "model": self.config.model,
            "input": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_output_tokens": self.config.max_output_tokens,
        }
        if self.config.reasoning_effort:
            request["reasoning"] = {"effort": self.config.reasoning_effort}
        response = client.responses.create(**request)
        return response.output_text


class HeuristicTransformationProvider:
    """Offline transformer for tests and development."""

    def transform(self, prompt: str) -> str:
        marker = "Source item:\n"
        source_item = json.loads(prompt.split(marker, 1)[1])
        original = source_item["original_multiple_choice"]
        correct_ids = set(original.get("correct_option_ids", []))
        correct_options = [
            option["text"]
            for option in original.get("options", [])
            if option.get("option_id") in correct_ids
        ]
        reference_answer = original.get("explanation") or " ".join(correct_options)
        key_concepts = source_item.get("key_concepts", correct_options)
        incorrect_options = [
            option["text"]
            for option in original.get("options", [])
            if option.get("option_id") not in correct_ids
        ]
        transformed = {
            "certification": source_item["certification"],
            "domain": source_item["domain"],
            "difficulty": source_item["difficulty"],
            "question_type": "service_selection",
            "question_category": source_item.get("question_category", "operational_complexity_tradeoff"),
            "question": _freeform_question(original["question"]),
            "reference_answer": reference_answer,
            "key_concepts": key_concepts,
            "required_concepts": key_concepts,
            "bonus_concepts": [],
            "common_misconceptions": [f"{option} is the best answer." for option in incorrect_options],
            "acceptable_answers": [*correct_options, reference_answer],
            "must_not_claim": [f"{option} is the best answer." for option in incorrect_options],
            "do_not_claim_explanation": [
                f"The reference answer is stronger because it satisfies the scenario, while {option} is a distractor."
                for option in incorrect_options
            ],
            "original_multiple_choice": original,
        }
        return json.dumps(transformed)


def _freeform_question(question: str) -> str:
    return f"Explain the AWS concept or service decision tested by this scenario: {question}"
