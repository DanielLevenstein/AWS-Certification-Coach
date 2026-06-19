"""Evaluator providers backed by locally trained answer models."""

from __future__ import annotations

import json
import re
from pathlib import Path

from aws_certification_coach.domain import Question
from aws_certification_coach.model_evaluation.semantic_similarity import semantic_similarity_score
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import letter_to_numeric
from aws_certification_coach.training.answer_classifier import (
    AnswerClassificationModel,
    AnswerRegressionModel,
    answer_calibration_key,
)
from aws_certification_coach.training.dataset import load_feedback_regression_examples
from aws_certification_coach.training.features import AnswerFeatureExtractor


SUCCESS_THRESHOLD = 70
INCORRECT_ANSWER_SCORE_CAP = 49
QUESTION_RESTATEMENT_SCORE_CAP = 25
MISSPELLED_SERVICE_SCORE = 65
EXACT_CORRECT_OPTION_SCORE = 95
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
GENERIC_SERVICE_TOKENS = {"amazon", "aws", "service", "the", "use"}


class TrainedClassifierEvaluatorProvider:
    """Uses the trained classifier to decide whether an answer earns full credit."""

    def __init__(self, model_path: str | Path, feature_extractor: AnswerFeatureExtractor | None = None) -> None:
        self.model = AnswerClassificationModel.load(model_path)
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor()

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        features = self.feature_extractor.extract(question, user_answer)
        probability = self.model.predict_proba(features)
        return _evaluation_response(question, user_answer, probability * 100)


class TrainedRegressionEvaluatorProvider:
    """Uses the partial-credit regression model as the application score source."""

    def __init__(
        self,
        model_path: str | Path | AnswerRegressionModel,
        feature_extractor: AnswerFeatureExtractor | None = None,
    ) -> None:
        self.model = (
            model_path
            if isinstance(model_path, AnswerRegressionModel)
            else AnswerRegressionModel.load(model_path)
        )
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor(answer_form=self.model.answer_form)

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        calibration = self.model.calibrations.get(answer_calibration_key(question, user_answer))
        if calibration is not None:
            return _evaluation_response(question, user_answer, calibration * 100)
        features = self.feature_extractor.extract(question, user_answer)
        return _evaluation_response(question, user_answer, self.model.predict(features) * 100)


class SemanticSimilarityEvaluatorProvider:
    """Uses deterministic semantic_similarity scoring as the application score source."""

    def __init__(
        self,
        feedback_paths: tuple[str, ...] | list[str] | None = None,
        questions_path: str | Path | None = None,
        questions: list[Question] | None = None,
    ) -> None:
        self.calibrations = _feedback_calibrations(feedback_paths or (), questions_path, questions)

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        calibration = self.calibrations.get(answer_calibration_key(question, user_answer))
        score = calibration * 100 if calibration is not None else semantic_similarity_score(question, user_answer)
        return _evaluation_response(question, user_answer, score)


SemanticAwareEvaluatorProvider = SemanticSimilarityEvaluatorProvider


def _evaluation_response(question: Question, user_answer: str, model_score: float) -> str:
    if _is_exact_correct_option(question, user_answer):
        model_score = max(model_score, EXACT_CORRECT_OPTION_SCORE)
    prediction = 1 if model_score >= SUCCESS_THRESHOLD else 0
    if _is_question_restatement(question, user_answer):
        missing = _missing_concepts(question, user_answer)
        payload = {
            "score": min(int(model_score), QUESTION_RESTATEMENT_SCORE_CAP),
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": "This answer restates the question without identifying and explaining the solution.",
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    if _has_bad_service_spelling(question, user_answer):
        missing = _missing_concepts(question, user_answer)
        payload = {
            "score": MISSPELLED_SERVICE_SCORE,
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": "The AWS service name appears to be misspelled.",
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    grading_issue = _incorrect_service_answer_issue(question, user_answer)
    if grading_issue:
        missing = _missing_concepts(question, user_answer)
        payload = {
            "score": min(int(model_score), INCORRECT_ANSWER_SCORE_CAP),
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": grading_issue,
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    missing = [] if prediction == 1 else _missing_concepts(question, user_answer)
    payload = {
        "score": int(model_score),
        "missing_concepts": missing,
        "suggested_improvements": [f"Explain {concept}." for concept in missing],
        "feedback": _feedback(model_score, prediction),
        "detailed_answer": question.reference_answer,
    }
    return json.dumps(payload)


def _feedback_calibrations(
    feedback_paths: tuple[str, ...] | list[str],
    questions_path: str | Path | None,
    questions: list[Question] | None,
) -> dict[str, float]:
    paths = [Path(path) for path in feedback_paths]
    existing_paths = [path for path in paths if path.exists()]
    if not existing_paths:
        return {}
    available_questions = questions
    if available_questions is None:
        if questions_path is None or not Path(questions_path).exists():
            return {}
        available_questions = JsonQuestionRepository(questions_path).all()
    calibration_values: dict[str, set[float]] = {}
    for path in existing_paths:
        for example in load_feedback_regression_examples(path, available_questions):
            key = answer_calibration_key(example.question, example.answer)
            calibration_values.setdefault(key, set()).add(example.rating)
    return {
        key: next(iter(values))
        for key, values in calibration_values.items()
        if len(values) == 1
    }


def _missing_concepts(question: Question, user_answer: str) -> list[str]:
    normalized_answer = user_answer.casefold()
    return [
        concept
        for concept in _required_concepts(question)
        if concept.casefold() not in normalized_answer
    ]


def _incorrect_service_answer_issue(question: Question, user_answer: str) -> str | None:
    if _is_too_generic_service_answer(question, user_answer):
        return "The answer names AWS generally but does not identify the required service."
    if _is_incorrect_service_selection(question, user_answer):
        return "This exact service answer is not in the question's correct answer list."
    return None


def _is_question_restatement(question: Question, user_answer: str) -> bool:
    answer_tokens = set(TOKEN_PATTERN.findall(user_answer.casefold()))
    if len(answer_tokens) < 4 or _is_exact_correct_option(question, user_answer):
        return False

    prompt_texts = [question.question]
    if question.original_multiple_choice:
        prompt_texts.append(question.original_multiple_choice.question)
    for prompt in prompt_texts:
        prompt_tokens = set(TOKEN_PATTERN.findall(prompt.casefold()))
        if _token_containment(answer_tokens, prompt_tokens) < 0.9:
            continue
        identifying_tokens = _expected_service_tokens(question) - prompt_tokens - GENERIC_SERVICE_TOKENS
        if identifying_tokens & answer_tokens:
            continue
        return True
    return False


def _is_exact_correct_option(question: Question, user_answer: str) -> bool:
    original = question.original_multiple_choice
    if original is None:
        return False
    correct_ids = set(original.correct_option_ids)
    normalized_answer = _normalized_service_answer(user_answer)
    return normalized_answer in {
        _normalized_service_answer(option.text)
        for option in original.options
        if option.option_id in correct_ids
    }


def _token_containment(required: set[str], candidate: set[str]) -> float:
    if not required:
        return 0.0
    return len(required & candidate) / len(required)


def _is_too_generic_service_answer(question: Question, user_answer: str) -> bool:
    expected_tokens = _expected_service_tokens(question)
    answer_tokens = set(TOKEN_PATTERN.findall(user_answer.casefold()))
    meaningful_tokens = answer_tokens - GENERIC_SERVICE_TOKENS
    return bool(expected_tokens) and not meaningful_tokens and len(answer_tokens) <= 3


def _has_bad_service_spelling(question: Question, user_answer: str) -> bool:
    expected_tokens = _expected_service_tokens(question) - GENERIC_SERVICE_TOKENS
    answer_tokens = set(TOKEN_PATTERN.findall(user_answer.casefold()))
    for expected in expected_tokens - answer_tokens:
        if any(
            not _is_singular_plural_variant(expected, candidate)
            and _edit_distance(expected, candidate) == 1
            for candidate in answer_tokens
            if len(candidate) >= 3
        ):
            return True
    return False


def _expected_service_tokens(question: Question) -> set[str]:
    concepts = _required_concepts(question)
    if not concepts:
        return set()
    return set(TOKEN_PATTERN.findall(concepts[0].casefold()))


def _required_concepts(question: Question) -> list[str]:
    return question.required_concepts or question.key_concepts


def _is_incorrect_service_selection(question: Question, user_answer: str) -> bool:
    original = question.original_multiple_choice
    if original is None:
        return False
    normalized_answer = _normalized(user_answer)
    if not normalized_answer.startswith("use "):
        return False
    if len(normalized_answer.split()) > 6:
        return False
    correct_ids = set(original.correct_option_ids)
    correct_answers = {
        _normalized(option.text)
        for option in original.options
        if option.option_id in correct_ids
    }
    return normalized_answer not in correct_answers


def _feedback(model_score: float, prediction: int) -> str:
    del model_score
    if prediction == 1:
        return "This answer covers the expected AWS concepts."
    return "This answer needs more AWS-specific detail."


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace(".", "").split())


def _normalized_service_answer(value: str) -> str:
    normalized = _normalized(value)
    return normalized.removeprefix("use ")


def _edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_character in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_character in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_character != right_character),
                )
            )
        previous = current
    return previous[-1]


def _is_singular_plural_variant(left: str, right: str) -> bool:
    return left == f"{right}s" or right == f"{left}s"
