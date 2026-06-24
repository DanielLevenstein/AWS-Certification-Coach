"""Structured AWS knowledge used by local answer evaluators."""

from aws_certification_coach.knowledge_base.repository import (
    DEFAULT_KNOWLEDGE_BASE_PATH,
    Concept,
    KnowledgeBase,
    KnowledgeSelection,
    ServiceFamily,
    load_knowledge_base,
)

__all__ = [
    "DEFAULT_KNOWLEDGE_BASE_PATH",
    "Concept",
    "KnowledgeBase",
    "KnowledgeSelection",
    "ServiceFamily",
    "load_knowledge_base",
]
