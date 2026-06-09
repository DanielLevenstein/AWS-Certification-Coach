"""Reusable local LLM runtime helpers.

This is adapted from the previous RAG prototype, with FAISS, embeddings,
chunk loading, and RAG prompts removed.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import atexit
import gc
from threading import RLock
from typing import Any

from aws_certification_coach.domain import Question


@dataclass(frozen=True)
class LLMRuntimeConfig:
    model_path: str = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    model_filename: str = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
    top_p: float = 0.95
    max_tokens: int = 500
    temperature: float = 0.0
    repeat_penalty: float = 1.2
    n_gpu_layers: int = 0
    n_batch: int = 256
    n_ctx: int = 2048
    n_threads: int | None = None

    def with_overrides(self, **overrides: Any) -> "LLMRuntimeConfig":
        values = {key: value for key, value in overrides.items() if value is not None}
        return replace(self, **values)


class LocalLlamaRuntime:
    """Lazy, cached llama-cpp runtime for deterministic chat completions."""

    def __init__(self, config: LLMRuntimeConfig | None = None) -> None:
        self.config = config or LLMRuntimeConfig()
        self._client = None
        self._lock = RLock()
        atexit.register(self.close)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            repeat_penalty=self.config.repeat_penalty,
        )
        return trim_model_response(response["choices"][0]["message"]["content"])

    @property
    def client(self):
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._client = self._create_client()
        return self._client

    def close(self) -> None:
        with self._lock:
            client = self._client
            self._client = None

        close = getattr(client, "close", None)
        if callable(close):
            close()
        gc.collect()

    def _create_client(self):
        import multiprocessing

        from huggingface_hub import hf_hub_download
        from llama_cpp import Llama

        model_path = hf_hub_download(
            repo_id=self.config.model_path,
            filename=self.config.model_filename,
        )
        cpu_count = multiprocessing.cpu_count()
        n_threads = self.config.n_threads or max(4, cpu_count - 1)
        return Llama(
            model_path=model_path,
            n_threads=n_threads,
            n_batch=self.config.n_batch,
            n_gpu_layers=self.config.n_gpu_layers,
            n_ctx=self.config.n_ctx,
            verbose=False,
        )


def trim_model_response(response_text: str) -> str:
    marker = "</think>"
    if marker in response_text:
        return response_text.split(marker, 1)[1].lstrip()
    return response_text.strip()


class LocalLlamaEvaluatorProvider:
    """Adapter that lets LocalLlamaRuntime satisfy the evaluator provider API."""

    SYSTEM_PROMPT = "You are a strict AWS certification answer evaluator. Return JSON only."

    def __init__(self, runtime: LocalLlamaRuntime | None = None) -> None:
        self.runtime = runtime or LocalLlamaRuntime()

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del question, user_answer
        return self.runtime.complete(self.SYSTEM_PROMPT, prompt)
