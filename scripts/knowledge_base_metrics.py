#!/usr/bin/env python3
"""Write stable release metrics for the committed AWS knowledge base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.knowledge_base import DEFAULT_KNOWLEDGE_BASE_PATH, load_knowledge_base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-base", type=Path, default=DEFAULT_KNOWLEDGE_BASE_PATH)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    knowledge = load_knowledge_base(args.knowledge_base)
    metrics = {
        "schema_version": knowledge.schema_version,
        "file_size_bytes": args.knowledge_base.stat().st_size,
        "syntax_alias_count": len(knowledge.syntax_aliases),
        "service_family_count": len(knowledge.service_families),
        "concept_count": len(knowledge.concepts),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
