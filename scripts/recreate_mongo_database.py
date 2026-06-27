#!/usr/bin/env python3
"""Recreate the MongoDB database from raw JSON source files."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
KNOWLEDGE_BASE_PATH = CONFIG_DIR / "knowledge_base" / "knowledge_base.json"
QUESTION_TEMPLATE_PATH = CONFIG_DIR / "question_templates" / "question_template.json"
SCHEMA_VERSION_PATH = CONFIG_DIR / "schema_version.json"
USER_FEEDBACK_PATH = CONFIG_DIR / "data" / "user_feedback.v3.json"
STRUCTURED_ANSWER_TRAINING_PATH = CONFIG_DIR / "data" / "structured_answer_training_data.json"

MIGRATED_SCHEMA_VERSION = 4.1
DEFAULT_MONGODB_URI = "mongodb://localhost:27017"
DEFAULT_DATABASE_NAME = "aws_certification_coach"


@dataclass(frozen=True)
class SourceFiles:
    knowledge_base: Path = KNOWLEDGE_BASE_PATH
    question_template: Path = QUESTION_TEMPLATE_PATH
    schema_version: Path = SCHEMA_VERSION_PATH
    user_feedback: Path = USER_FEEDBACK_PATH
    structured_answer_training: Path = STRUCTURED_ANSWER_TRAINING_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uri", default=os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI))
    parser.add_argument("--database", default=os.getenv("AWS_COACH_MONGODB_DATABASE", DEFAULT_DATABASE_NAME))
    parser.add_argument("--drop-existing", action="store_true", help="Drop the target database before importing.")
    parser.add_argument("--yes", action="store_true", help="Confirm destructive database recreation.")
    parser.add_argument("--dry-run", action="store_true", help="Build and validate documents without writing to MongoDB.")
    args = parser.parse_args()

    if args.drop_existing and not args.yes:
        raise SystemExit("Refusing to drop a database without --yes.")
    if not str(args.database).strip():
        raise SystemExit("Database name must not be empty.")

    collections = build_collection_documents(SourceFiles())
    if args.dry_run:
        _print_summary(args.database, collections, dry_run=True)
        return

    recreate_database(args.uri, args.database, collections, drop_existing=args.drop_existing)
    _print_summary(args.database, collections, dry_run=False)


def build_collection_documents(sources: SourceFiles) -> dict[str, list[dict[str, Any]]]:
    knowledge_base = _read_json_object(sources.knowledge_base)
    question_template = _read_json_object(sources.question_template)
    schema_versions = _read_json_object(sources.schema_version)
    user_feedback = _read_json_array(sources.user_feedback)
    structured_answer_training = _read_json_array(sources.structured_answer_training)

    _validate_identical_misconception_sources(knowledge_base)

    return {
        "content_manifests": _content_manifests(sources, knowledge_base, question_template, schema_versions),
        "syntax_aliases": _documents_with_ids(knowledge_base["syntax_aliases"], "alias"),
        "services": _documents_with_ids(knowledge_base["services"], "id"),
        "concepts": _documents_with_ids(knowledge_base["concepts"], "id"),
        "misconceptions": _documents_with_ids(knowledge_base["common_misconceptions"], "id"),
        "question_templates": _documents_with_ids(question_template["templates"], "id"),
        "service_scenarios": _documents_with_ids(question_template["service_scenarios"], "id"),
        "developer_question_scenarios": _documents_with_ids(question_template["developer_question_scenarios"], "id"),
        "user_feedback": _documents_with_stable_hash_ids(user_feedback),
        "structured_answer_training_examples": _documents_with_stable_hash_ids(structured_answer_training),
    }


def recreate_database(
    uri: str,
    database_name: str,
    collections: dict[str, list[dict[str, Any]]],
    *,
    drop_existing: bool,
) -> None:
    try:
        from pymongo import ASCENDING, TEXT, MongoClient
    except ImportError as exc:
        raise SystemExit("pymongo is required. Run .venv/bin/python -m pip install -r requirements.txt first.") from exc

    client = MongoClient(uri)
    if drop_existing:
        client.drop_database(database_name)

    database = client[database_name]
    for collection_name, documents in collections.items():
        collection = database[collection_name]
        if documents:
            collection.insert_many(documents, ordered=True)

    _create_indexes(database, ascending=ASCENDING, text=TEXT)


def _create_indexes(database: Any, *, ascending: int, text: str) -> None:
    database["content_manifests"].create_index([("source", ascending)], unique=True)
    database["content_manifests"].create_index([("schema_version", ascending)])
    database["syntax_aliases"].create_index([("alias", ascending)], unique=True)
    database["syntax_aliases"].create_index([("canonical", ascending)])
    database["services"].create_index([("id", ascending)], unique=True)
    database["services"].create_index([("name", text), ("tokens", text), ("aliases", text)])
    database["concepts"].create_index([("id", ascending)], unique=True)
    database["concepts"].create_index([("service_ids", ascending)])
    database["misconceptions"].create_index([("id", ascending)], unique=True)
    database["misconceptions"].create_index([("key_concepts", ascending)])
    database["question_templates"].create_index([("id", ascending)], unique=True)
    database["question_templates"].create_index([("question_type", ascending)])
    database["question_templates"].create_index([("certifications", ascending)])
    database["service_scenarios"].create_index([("id", ascending)], unique=True)
    database["service_scenarios"].create_index([("service_id", ascending)])
    database["service_scenarios"].create_index([("certification", ascending), ("exam_code", ascending), ("difficulty", ascending)])
    database["developer_question_scenarios"].create_index([("id", ascending)], unique=True)
    database["user_feedback"].create_index([("schema_version", ascending)])
    database["user_feedback"].create_index([("exam_code", ascending)])
    database["user_feedback"].create_index([("correct_rating", ascending), ("rating_given", ascending)])
    database["structured_answer_training_examples"].create_index(
        [("certification", ascending), ("exam_code", ascending), ("domain", ascending), ("difficulty", ascending)]
    )
    database["structured_answer_training_examples"].create_index([("key_concepts", ascending)])
    database["structured_answer_training_examples"].create_index([("required_concepts", ascending)])


def _content_manifests(
    sources: SourceFiles,
    knowledge_base: dict[str, Any],
    question_template: dict[str, Any],
    schema_versions: dict[str, Any],
) -> list[dict[str, Any]]:
    imported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return [
        _manifest(
            "knowledge_base",
            sources.knowledge_base,
            knowledge_base.get("schema_version", schema_versions.get("KNOWLEDGE_BASE_VERSION")),
            knowledge_base.get("description", ""),
            imported_at,
        ),
        _manifest(
            "question_template",
            sources.question_template,
            question_template.get("schema_version", schema_versions.get("QUESTION_SCHEMA_VERSION")),
            question_template.get("description", ""),
            imported_at,
        ),
        _manifest(
            "user_feedback",
            sources.user_feedback,
            schema_versions.get("USER_FEEDBACK_VERSION"),
            "Versioned learner feedback examples.",
            imported_at,
        ),
        _manifest(
            "structured_answer_training_data",
            sources.structured_answer_training,
            schema_versions.get("QUESTION_SCHEMA_VERSION"),
            "Curated structured-answer training and evaluation examples.",
            imported_at,
        ),
    ]


def _manifest(source: str, path: Path, source_schema_version: Any, description: str, imported_at: str) -> dict[str, Any]:
    return {
        "_id": source,
        "source": source,
        "source_path": _display_path(path),
        "schema_version": MIGRATED_SCHEMA_VERSION,
        "source_schema_version": source_schema_version,
        "description": description,
        "imported_at": imported_at,
    }


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _documents_with_ids(rows: list[Any], key: str) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Row {index} for {key} documents must be a JSON object.")
        document_id = str(row.get(key, "")).strip()
        if not document_id:
            raise ValueError(f"Row {index} is missing required key {key!r}.")
        if document_id in seen:
            raise ValueError(f"Duplicate {key} value: {document_id}")
        seen.add(document_id)
        documents.append({"_id": document_id, **row})
    return documents


def _documents_with_stable_hash_ids(rows: list[Any]) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Row {index} must be a JSON object.")
        document_id = _stable_document_id(row)
        if document_id in seen:
            raise ValueError(f"Duplicate generated document id: {document_id}")
        seen.add(document_id)
        documents.append({"_id": document_id, **row})
    return documents


def _stable_document_id(row: dict[str, Any]) -> str:
    canonical = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_identical_misconception_sources(knowledge_base: dict[str, Any]) -> None:
    if knowledge_base.get("common_misconceptions") != knowledge_base.get("must_not_claim"):
        raise ValueError("knowledge_base.common_misconceptions and knowledge_base.must_not_claim must match before import.")


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _read_json_array(path: Path) -> list[Any]:
    payload = _read_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Expected JSON array: {path}")
    return payload


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _print_summary(database_name: str, collections: dict[str, list[dict[str, Any]]], *, dry_run: bool) -> None:
    mode = "Validated" if dry_run else "Recreated"
    print(f"{mode} MongoDB database {database_name!r} from raw JSON files.")
    for collection_name, documents in collections.items():
        print(f"- {collection_name}: {len(documents)} documents")


if __name__ == "__main__":
    main()
