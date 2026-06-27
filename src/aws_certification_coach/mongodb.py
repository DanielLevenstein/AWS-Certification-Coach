"""MongoDB configuration helpers."""

from __future__ import annotations

import os
from typing import Any


DEFAULT_MONGODB_DATABASE = "aws_certification_coach"


def mongodb_uri() -> str:
    return os.environ.get("MONGODB_URI", "").strip()


def mongodb_database_name() -> str:
    return os.environ.get("AWS_COACH_MONGODB_DATABASE", DEFAULT_MONGODB_DATABASE).strip() or DEFAULT_MONGODB_DATABASE


def mongodb_content_enabled() -> bool:
    backend = os.environ.get("AWS_COACH_CONTENT_BACKEND", "").strip().lower()
    if backend in {"json", "file", "files"}:
        return False
    if backend in {"mongo", "mongodb"}:
        return True
    return bool(mongodb_uri())


def get_mongodb_database(uri: str | None = None, database_name: str | None = None) -> Any:
    try:
        from pymongo import MongoClient
    except ImportError as exc:
        raise RuntimeError("pymongo is required for MongoDB-backed content loading.") from exc

    resolved_uri = uri or mongodb_uri()
    if not resolved_uri:
        raise RuntimeError("MONGODB_URI is required for MongoDB-backed content loading.")
    return MongoClient(resolved_uri)[database_name or mongodb_database_name()]
