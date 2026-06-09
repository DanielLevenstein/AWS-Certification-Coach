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
class LocalLlamaModelConfig:
    model_path: str = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    model_filename: str = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
    top_p: float = 0.95
    max_tokens: int = 900
    temperature: float = 0.0
    repeat_penalty: float = 1.2
    n_gpu_layers: int = 0
    n_batch: int = 256
    n_ctx: int = 2048
    n_threads: int | None = None


@dataclass(frozen=True)
class EvaluatorConfig:
    provider: str = "heuristic"
    openai: OpenAIModelConfig = field(default_factory=OpenAIModelConfig)
    local_llama: LocalLlamaModelConfig = field(default_factory=LocalLlamaModelConfig)
    trained_classifier_model_path: str = "models/answer_classifier.json"


def load_evaluator_config(path: str | Path | None = None) -> EvaluatorConfig:
    config_path = Path(os.getenv("AWS_COACH_EVALUATOR_CONFIG", path or DEFAULT_CONFIG_PATH))
    raw = _read_json(config_path)
    provider = os.getenv("AWS_COACH_EVALUATOR_PROVIDER", raw.get("provider", "heuristic"))
    return EvaluatorConfig(
        provider=provider,
        openai=_openai_config(raw.get("openai", {})),
        local_llama=_local_llama_config(raw.get("local_llama", {})),
        trained_classifier_model_path=str(
            os.getenv(
                "AWS_COACH_CLASSIFIER_MODEL_PATH",
                raw.get("trained_classifier", {}).get("model_path", "models/answer_classifier.json")
                if isinstance(raw.get("trained_classifier", {}), dict)
                else "models/answer_classifier.json",
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


def _local_llama_config(raw: object) -> LocalLlamaModelConfig:
    values = raw if isinstance(raw, dict) else {}
    return LocalLlamaModelConfig(
        model_path=str(values.get("model_path", LocalLlamaModelConfig.model_path)),
        model_filename=str(values.get("model_filename", LocalLlamaModelConfig.model_filename)),
        top_p=float(values.get("top_p", 0.95)),
        max_tokens=int(values.get("max_tokens", 900)),
        temperature=float(values.get("temperature", 0.0)),
        repeat_penalty=float(values.get("repeat_penalty", 1.2)),
        n_gpu_layers=int(values.get("n_gpu_layers", 0)),
        n_batch=int(values.get("n_batch", 256)),
        n_ctx=int(values.get("n_ctx", 2048)),
        n_threads=values.get("n_threads"),
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
