"""Configuration loading for model providers and hyperparameters."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "evaluator_default.json"


@dataclass(frozen=True)
class OpenAIModelConfig:
    model: str = "gpt-5.4-mini"
    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 900
    reasoning_effort: str | None = "low"


@dataclass(frozen=True)
class EvaluatorConfig:
    provider: str = "heuristic"
    openai: OpenAIModelConfig = field(default_factory=OpenAIModelConfig)
    semantic_feedback_paths: tuple[str, ...] = (
        "data/curated/curated_training_data.json",
    )
    semantic_questions_path: str = "data/questions/sample_questions.json"


def load_evaluator_config(path: str | Path | None = None) -> EvaluatorConfig:
    config_path = Path(os.getenv("AWS_COACH_EVALUATOR_CONFIG", path or DEFAULT_CONFIG_PATH))
    raw = _read_json(config_path)
    provider = os.getenv("AWS_COACH_EVALUATOR_PROVIDER", raw.get("provider", "heuristic"))
    return EvaluatorConfig(
        provider=provider,
        openai=_openai_config(raw.get("openai", {})),
        semantic_feedback_paths=_semantic_feedback_paths(raw),
        semantic_questions_path=str(
            os.getenv(
                "AWS_COACH_SEMANTIC_QUESTIONS_PATH",
                raw.get("semantic_similarity", {}).get("questions_path", "data/questions/sample_questions.json")
                if isinstance(raw.get("semantic_similarity", {}), dict)
                else "data/questions/sample_questions.json",
            )
        ),
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except FileNotFoundError:
        return {}
    if not isinstance(payload, dict):
        raise ValueError(f"Evaluator config must be a JSON object: {path}")
    return payload


def _openai_config(raw: object) -> OpenAIModelConfig:
    values = raw if isinstance(raw, dict) else {}
    return OpenAIModelConfig(
        model=str(os.getenv("AWS_COACH_OPENAI_MODEL", values.get("model", OpenAIModelConfig.model))),
        temperature=_float_env("AWS_COACH_OPENAI_TEMPERATURE", values.get("temperature", 0.0)),
        top_p=_float_env("AWS_COACH_OPENAI_TOP_P", values.get("top_p", 1.0)),
        max_output_tokens=_int_env("AWS_COACH_OPENAI_MAX_OUTPUT_TOKENS", values.get("max_output_tokens", 900)),
        reasoning_effort=_optional_str_env("AWS_COACH_OPENAI_REASONING_EFFORT", values.get("reasoning_effort", "low")),
    )

def _float_env(name: str, default: object) -> float:
    return float(os.getenv(name, default))


def _int_env(name: str, default: object) -> int:
    return int(os.getenv(name, default))


def _optional_str_env(name: str, default: object) -> str | None:
    value = os.getenv(name, default)
    if value in (None, "", "none", "None"):
        return None
    return str(value)


def _semantic_feedback_paths(raw: dict[str, Any]) -> tuple[str, ...]:
    env_value = os.getenv("AWS_COACH_SEMANTIC_FEEDBACK_PATHS")
    if env_value is not None:
        return tuple(path.strip() for path in env_value.split(":") if path.strip())
    semantic = raw.get("semantic_similarity", {})
    if isinstance(semantic, dict) and isinstance(semantic.get("feedback_paths"), list):
        return tuple(str(path) for path in semantic["feedback_paths"])
    return EvaluatorConfig.semantic_feedback_paths
