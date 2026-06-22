#!/usr/bin/env python3
"""Download the pinned local answer-embedding model from Hugging Face."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_REPOSITORY = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_OUTPUT = Path("models/huggingface/all-MiniLM-L6-v2")
PYTORCH_MODEL_FILES = [
    "config.json",
    "config_sentence_transformers.json",
    "model.safetensors",
    "modules.json",
    "sentence_bert_config.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
    "1_Pooling/config.json",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    from huggingface_hub import snapshot_download

    args.output.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=args.repository,
        local_dir=args.output,
        allow_patterns=PYTORCH_MODEL_FILES,
    )
    print(f"Downloaded {args.repository} to {args.output}")


if __name__ == "__main__":
    main()
