"""Core domain models for AWS Certification Coach."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvaluationResult:
    """Structured feedback returned by an evaluator."""

    score: int
    missing_concepts: list[str] = field(default_factory=list)
    suggested_improvements: list[str] = field(default_factory=list)
    feedback: str = ""
    detailed_answer: str = ""


@dataclass(frozen=True)
class Question:
    certification: str
    domain: str
    difficulty: str
    question: str
    reference_answer: str
    key_concepts: list[str]
    exam_code: str = ""
    original_multiple_choice: "MultipleChoiceQuestion | None" = None


@dataclass(frozen=True)
class MultipleChoiceOption:
    option_id: str
    text: str


@dataclass(frozen=True)
class MultipleChoiceQuestion:
    question: str
    options: list[MultipleChoiceOption]
    correct_option_ids: list[str]
    explanation: str = ""
    source_name: str = ""
    source_url: str = ""
    source_license_notes: str = ""


@dataclass(frozen=True)
class QuestionFilter:
    certification: str | None = None
    domain: str | None = None
    difficulty: str | None = None


@dataclass(frozen=True)
class AnsweredQuestion:
    question: Question
    user_answer: str
    evaluation: EvaluationResult
