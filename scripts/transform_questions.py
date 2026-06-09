"""Convert multiple-choice source artifacts into freeform app artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from aws_certification_coach.transforms.mcq_to_freeform import (
    HeuristicTransformationProvider,
    MultipleChoiceToFreeformTransformer,
    OpenAITransformationProvider,
    TransformationModelConfig,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to source multiple-choice JSON list.")
    parser.add_argument("--output", required=True, help="Path for transformed freeform JSON list.")
    parser.add_argument("--provider", choices=["openai", "heuristic"], default="openai")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-output-tokens", type=int, default=1200)
    parser.add_argument("--reasoning-effort", default="medium")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    source_items = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(source_items, list):
        raise ValueError("Input artifact must be a JSON list.")

    provider = _provider(args)
    transformer = MultipleChoiceToFreeformTransformer(provider)
    transformed = transformer.transform_many(source_items)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(transformed, indent=2) + "\n", encoding="utf-8")


def _provider(args):
    if args.provider == "heuristic":
        return HeuristicTransformationProvider()
    return OpenAITransformationProvider(
        TransformationModelConfig(
            model=args.model,
            temperature=args.temperature,
            top_p=args.top_p,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Question transformation failed: {exc}", file=sys.stderr)
        raise
