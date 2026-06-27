from __future__ import annotations

import aws_certification_coach.questions.json_repository as question_repository
from aws_certification_coach.questions.json_repository import DEFAULT_GENERATED_QUESTIONS_PATH, JsonQuestionRepository
from scripts.recreate_mongo_database import SourceFiles, build_collection_documents


def test_question_repository_reads_generated_questions_from_mongodb(monkeypatch) -> None:
    collections = build_collection_documents(SourceFiles())
    database = _FakeDatabase(collections)
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("AWS_COACH_MONGODB_DATABASE", "aws_certification_coach_test")
    monkeypatch.setattr(question_repository, "get_mongodb_database", lambda _uri, _database_name: database)

    questions = JsonQuestionRepository(DEFAULT_GENERATED_QUESTIONS_PATH).all()

    assert len(questions) >= 198
    assert len([question for question in questions if question.exam_code == "DVA-C02"]) == 38
    assert any(question.question_type == "artifact_review" for question in questions)


class _FakeDatabase:
    def __init__(self, collections: dict[str, list[dict]]) -> None:
        self.collections = collections

    def __getitem__(self, name: str):
        return _FakeCollection(self.collections[name])


class _FakeCollection:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows

    def find(self, _filter: dict, projection: dict | None = None):
        for row in self.rows:
            yield _without_id(row) if projection and projection.get("_id") is False else dict(row)


def _without_id(row: dict) -> dict:
    return {key: value for key, value in row.items() if key != "_id"}
