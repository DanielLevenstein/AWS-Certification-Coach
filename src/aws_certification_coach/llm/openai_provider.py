"""OpenAI evaluator provider."""

from __future__ import annotations

from aws_certification_coach.config import OpenAIModelConfig
from aws_certification_coach.domain import Question
from aws_certification_coach.evaluation.structured_answer_context import StructuredAnswerContext


class OpenAIEvaluatorProvider:
    """EvaluatorProvider implementation backed by the OpenAI Responses API."""

    SYSTEM_PROMPT = "You are a careful AWS certification coach. Return JSON only."

    def __init__(
        self,
        config: OpenAIModelConfig | None = None,
        structured_answer_data_path: str | None = None,
    ) -> None:
        self.config = config or OpenAIModelConfig()
        self.structured_context = (
            StructuredAnswerContext(structured_answer_data_path)
            if structured_answer_data_path
            else None
        )

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del user_answer
        from openai import OpenAI

        client = OpenAI()
        structured_context = self.structured_context.for_question(question) if self.structured_context else ""
        grading_prompt = prompt
        if structured_context:
            grading_prompt = f"{prompt}\n\n{structured_context}"
        request = {
            "model": self.config.model,
            "input": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": grading_prompt},
            ],
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_output_tokens": self.config.max_output_tokens,
        }
        if self.config.reasoning_effort:
            request["reasoning"] = {"effort": self.config.reasoning_effort}
        response = client.responses.create(**request)
        return response.output_text
