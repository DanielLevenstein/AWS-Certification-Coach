"""OpenAI evaluator provider."""

from __future__ import annotations

from aws_certification_coach.config import OpenAIModelConfig
from aws_certification_coach.domain import Question


class OpenAIEvaluatorProvider:
    """EvaluatorProvider implementation backed by the OpenAI Responses API."""

    SYSTEM_PROMPT = "You are a careful AWS certification coach. Return JSON only."

    def __init__(self, config: OpenAIModelConfig | None = None) -> None:
        self.config = config or OpenAIModelConfig()

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del question, user_answer
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
