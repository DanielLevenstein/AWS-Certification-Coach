"""Question-template configuration access."""

from aws_certification_coach.question_templates.repository import (
    DEFAULT_QUESTION_TEMPLATE_PATH,
    DeveloperQuestionScenario,
    QuestionTemplate,
    QuestionTemplateCatalog,
    ServiceScenario,
    load_question_templates,
)

__all__ = [
    "DEFAULT_QUESTION_TEMPLATE_PATH",
    "DeveloperQuestionScenario",
    "QuestionTemplate",
    "QuestionTemplateCatalog",
    "ServiceScenario",
    "load_question_templates",
]
