"""Local classifier and deterministic semantic evaluator providers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass
from difflib import SequenceMatcher

from aws_certification_coach.domain import Question
from aws_certification_coach.knowledge_base import Service, load_knowledge_base
from aws_certification_coach.model_evaluation.semantic_similarity import semantic_similarity_score
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.answer_classifier import (
    AnswerClassificationModel,
    answer_calibration_key,
)
from aws_certification_coach.training.dataset import load_feedback_graded_examples
from aws_certification_coach.training.features import AnswerFeatureExtractor


SUCCESS_THRESHOLD = 70
INCORRECT_ANSWER_SCORE_CAP = 49
QUESTION_RESTATEMENT_SCORE_CAP = 25
MISSPELLED_SERVICE_SCORE = 65
EXACT_CORRECT_OPTION_SCORE = 95
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
GENERIC_SERVICE_TOKENS = {"amazon", "aws", "service", "the", "use"}
CURATED_FEEDBACK_SOURCE = "curated_answer_feedback"
MISCONCEPTION_SCORE_CAP = 65
MUST_NOT_CLAIM_SCORE_CAP = 49
CLAIM_FILLER_TOKENS = {
    "a",
    "an",
    "and",
    "answer",
    "better",
    "best",
    "claim",
    "fit",
    "for",
    "is",
    "meets",
    "not",
    "requirement",
    "satisfies",
    "scenario",
    "should",
    "than",
    "the",
    "this",
    "to",
    "use",
}
NEGATION_TOKENS = {"avoid", "cannot", "don't", "doesnt", "doesn't", "incorrect", "not", "wrong"}
QUESTION_RESTATEMENT_FRAME_TOKENS = {
    "answer",
    "asks",
    "asking",
    "identify",
    "learner",
    "question",
    "should",
    "this",
    "to",
}


@dataclass(frozen=True)
class AnswerCalibration:
    rating: float
    feedback: str = ""


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
        score = calibration.rating * 100 if calibration is not None else semantic_similarity_score(question, user_answer)
        curated_feedback = calibration.feedback if calibration is not None else ""
        return _evaluation_response(question, user_answer, score, curated_feedback=curated_feedback)


SemanticAwareEvaluatorProvider = SemanticSimilarityEvaluatorProvider


def _evaluation_response(
    question: Question,
    user_answer: str,
    model_score: float,
    curated_feedback: str = "",
) -> str:
    relevant_service = _get_relevant_services(question, user_answer)
    if _is_exact_correct_option(question, user_answer):
        model_score = max(model_score, _exact_correct_option_score(question, user_answer))
    if _is_exact_corrected_artifact_answer(question, user_answer):
        payload = {
            "score": EXACT_CORRECT_OPTION_SCORE,
            "missing_concepts": [],
            "suggested_improvements": [],
            "relevant_service": relevant_service,
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    prediction = 1 if model_score >= SUCCESS_THRESHOLD else 0
    if _is_question_restatement(question, user_answer):
        missing = _missing_concepts(question, user_answer)
        feedback = "This answer restates the question without identifying and explaining the solution."
        payload = {
            "score": min(int(model_score), QUESTION_RESTATEMENT_SCORE_CAP),
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": feedback,
            "relevant_service": relevant_service,
            "feedback_source": CURATED_FEEDBACK_SOURCE if curated_feedback else "",
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
            "relevant_service": relevant_service,
            "feedback_source": CURATED_FEEDBACK_SOURCE if curated_feedback else "",
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    claim_issue = _rubric_claim_issue(question, user_answer)
    if claim_issue:
        missing = _missing_concepts(question, user_answer)
        score_cap = MUST_NOT_CLAIM_SCORE_CAP if claim_issue["section"] == "must_not_claim" else MISCONCEPTION_SCORE_CAP
        payload = {
            "score": min(int(model_score), score_cap),
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": str(claim_issue["feedback"]),
            "relevant_service": relevant_service,
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    reasoning_issue = _correct_service_wrong_reasoning_issue(question, user_answer)
    if reasoning_issue:
        missing = _missing_concepts(question, user_answer)
        score = min(89, max(80, int(model_score)))
        payload = {
            "score": score,
            "missing_concepts": missing,
            **_structured_feedback_fields(question, user_answer, missing, score),
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": reasoning_issue,
            "relevant_service": relevant_service,
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
            "relevant_service": relevant_service,
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    missing_service_issue = _missing_required_service_name_issue(question, user_answer, model_score)
    if missing_service_issue:
        missing = _missing_concepts(question, user_answer)
        payload = {
            "score": min(int(model_score), 79),
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": missing_service_issue,
            "relevant_service": relevant_service,
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)
    missing = [] if prediction == 1 else _missing_concepts(question, user_answer)
    payload = {
        "score": int(model_score),
        "missing_concepts": missing,
        "suggested_improvements": [f"Explain {concept}." for concept in missing],
        "relevant_service": relevant_service,
        "detailed_answer": question.reference_answer,
    }
    return json.dumps(payload)


def _structured_feedback_fields(
    question: Question,
    user_answer: str,
    missing_concepts: list[str],
    score: int | float,
) -> dict[str, object]:
    service_correct = _answer_names_expected_service_or_feature(question, user_answer) or (
        score >= 90 and not missing_concepts
    )
    core_concept_correct = not missing_concepts
    return {
        "service_correct": service_correct,
        "core_concept_correct": core_concept_correct,
    }


def _feedback_calibrations(
    feedback_paths: tuple[str, ...] | list[str],
    questions_path: str | Path | None,
    questions: list[Question] | None,
) -> dict[str, AnswerCalibration]:
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
    feedback_values: dict[str, set[str]] = {}
    for path in existing_paths:
        rows = json.loads(path.read_text(encoding="utf-8"))
        examples = load_feedback_graded_examples(path, available_questions)
        for row, example in zip(rows, examples, strict=True):
            key = answer_calibration_key(example.question, example.answer)
            calibration_values.setdefault(key, set()).add(example.rating)
            feedback_text = str(row.get("feedback_text", "")).strip() if isinstance(row, dict) else ""
            if feedback_text:
                feedback_values.setdefault(key, set()).add(feedback_text)
    return {
        key: AnswerCalibration(
            rating=next(iter(values)),
            feedback=_unique_feedback(feedback_values.get(key, set())),
        )
        for key, values in calibration_values.items()
        if len(values) == 1
    }


def _unique_feedback(values: set[str]) -> str:
    return next(iter(values)) if len(values) == 1 else ""

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


def _correct_service_wrong_reasoning_issue(question: Question, user_answer: str) -> str | None:
    if not _answer_names_expected_service_or_feature(question, user_answer):
        return None
    if _answer_uses_wrong_service_reasoning(question, user_answer):
        return "The answer names the correct service but includes reasoning for a different AWS concept."
    return None


def _missing_required_service_name_issue(question: Question, user_answer: str, model_score: float) -> str | None:
    if _answer_names_expected_service_or_feature(question, user_answer):
        return None
    if model_score < 70 and not _answer_covers_required_nonservice_concepts(question, user_answer):
        return None
    return "Name the specific AWS service or feature required by the question."


def _get_relevant_services(question: Question, user_answer: str) -> list[str]:
    names = []
    distractor_service = _selected_distractor_service(question, user_answer)
    if distractor_service is not None:
        names.append(distractor_service.name)
    # Removing service descriptions from answer for now
    #names.extend(service.name for service in _mentioned_answer_services(user_answer))
    expected_service = _expected_service_or_feature(question)
    if expected_service is not None:
        names.append(expected_service.name)
    return list(dict.fromkeys(names))


def _mentioned_answer_services(user_answer: str) -> list[Service]:
    knowledge = load_knowledge_base()
    normalized_answer = knowledge.canonicalize(_normalized_service_answer(user_answer))
    matches = []
    for service in knowledge.services:
        terms = (service.name, *service.aliases, *service.tokens)
        term_positions = [
            match.start()
            for term in terms
            for match in [re.search(rf"\b{re.escape(knowledge.canonicalize(term))}\b", normalized_answer)]
            if match is not None
        ]
        if term_positions:
            matches.append((min(term_positions), service))
    return [service for _position, service in sorted(matches, key=lambda item: item[0])]


def _selected_distractor_service(question: Question, user_answer: str) -> Service | None:
    original = question.original_multiple_choice
    if original is None:
        return None
    correct_ids = set(original.correct_option_ids)
    normalized_answer = _normalized_service_answer(user_answer)
    for option in original.options:
        if option.option_id in correct_ids:
            continue
        if normalized_answer != _normalized_service_answer(option.text):
            continue
        service = _service_for_option(option)
        if service is not None:
            return service
    return None


def _service_for_option(option: object) -> Service | None:
    knowledge = load_knowledge_base()
    metadata = getattr(option, "metadata", {})
    if isinstance(metadata, dict):
        service_name = str(metadata.get("service_name", "")).strip()
        if service_name:
            service = knowledge.service_for_name(service_name)
            if service is not None:
                return service
    option_text = _normalized_service_answer(str(getattr(option, "text", "")))
    service = knowledge.service_for_name(option_text)
    if service is not None:
        return service
    return knowledge.service_for_name(option_text.removesuffix(".").strip())


def _expected_service_or_feature(question: Question) -> Service | None:
    knowledge = load_knowledge_base()
    for term in _expected_service_or_feature_terms(question):
        service = knowledge.service_for_name(term)
        if service is not None:
            return service
    for concept_name in _required_concepts(question):
        normalized_name = knowledge.canonicalize(concept_name)
        for concept in knowledge.concepts:
            terms = (concept.name, *concept.aliases)
            if normalized_name not in {knowledge.canonicalize(term) for term in terms}:
                continue
            for service_id in concept.service_ids:
                try:
                    return knowledge.service_by_id(service_id)
                except KeyError:
                    continue
    return None


def _rubric_claim_issue(question: Question, user_answer: str) -> dict[str, str] | None:
    for index, claim in enumerate(question.must_not_claim):
        if _answer_affirms_claim(user_answer, claim):
            return {
                "section": "must_not_claim",
                "feedback": _do_not_claim_feedback(question, index, claim),
            }
    for claim in question.common_misconceptions:
        if _answer_affirms_claim(user_answer, claim):
            return {
                "section": "common_misconceptions",
                "feedback": f"This answer appears to rely on a common misconception: {claim}",
            }
    return None


def _do_not_claim_feedback(question: Question, index: int, claim: str) -> str:
    if index < len(question.do_not_claim_explanation):
        explanation = question.do_not_claim_explanation[index].strip()
        if explanation:
            return explanation
    return f"Do not claim this for this question: {claim}"


def _answer_names_expected_service_or_feature(question: Question, user_answer: str) -> bool:
    normalized_answer = _normalized_service_answer(user_answer)
    for term in _expected_service_or_feature_terms(question):
        normalized_term = _normalized_service_answer(term)
        term_tokens = _service_term_tokens(normalized_term)
        if not term_tokens:
            continue
        if normalized_term and re.search(rf"\b{re.escape(normalized_term)}\b", normalized_answer):
            return True
        answer_tokens = set(TOKEN_PATTERN.findall(normalized_answer))
        if term_tokens <= answer_tokens:
            return True
    return False


def _expected_service_or_feature_terms(question: Question) -> tuple[str, ...]:
    terms = []
    if _required_concepts(question):
        terms.append(_required_concepts(question)[0])
    terms.extend(question.acceptable_answers)
    if question.original_multiple_choice:
        correct_ids = set(question.original_multiple_choice.correct_option_ids)
        terms.extend(
            option.text
            for option in question.original_multiple_choice.options
            if option.option_id in correct_ids
        )
    return tuple(dict.fromkeys(term for term in terms if term.strip()))


def _service_term_tokens(term: str) -> set[str]:
    tokens = set(TOKEN_PATTERN.findall(term.casefold())) - GENERIC_SERVICE_TOKENS
    return tokens


def _answer_covers_required_nonservice_concepts(question: Question, user_answer: str) -> bool:
    answer_tokens = set(TOKEN_PATTERN.findall(user_answer.casefold()))
    matched_tokens = set()
    for concept in _required_concepts(question)[1:]:
        concept_tokens = set(TOKEN_PATTERN.findall(concept.casefold())) - GENERIC_SERVICE_TOKENS
        matched_tokens.update(answer_tokens & concept_tokens)
    return len(matched_tokens) >= 2


def _answer_uses_wrong_service_reasoning(question: Question, user_answer: str) -> bool:
    answer_tokens = set(TOKEN_PATTERN.findall(user_answer.casefold())) - GENERIC_SERVICE_TOKENS
    if not answer_tokens:
        return False
    for claim in (*question.common_misconceptions, *question.must_not_claim):
        service = load_knowledge_base().service_for_name(_claim_subject(claim))
        if service is None:
            continue
        service_name_tokens = set(TOKEN_PATTERN.findall(service.name.casefold()))
        wrong_reasoning_tokens = (
            set(TOKEN_PATTERN.findall(service.description.casefold()))
            - GENERIC_SERVICE_TOKENS
            - service_name_tokens
        )
        if len(answer_tokens & wrong_reasoning_tokens) >= 2:
            return True
    return False


def _claim_subject(claim: str) -> str:
    normalized = claim.strip()
    lowered = normalized.casefold()
    for separator in (
        " satisfies ",
        " is the best ",
        " is best ",
        " is the better ",
        " is better ",
    ):
        if separator in lowered:
            return normalized[: lowered.index(separator)].strip()
    return normalized


def _answer_affirms_claim(user_answer: str, claim: str) -> bool:
    answer_tokens = set(TOKEN_PATTERN.findall(user_answer.casefold()))
    claim_tokens = _claim_subject_tokens(claim)
    if not answer_tokens or not claim_tokens:
        return False
    if not claim_tokens <= answer_tokens:
        return False
    if _answer_negates_claim(user_answer, claim_tokens):
        return False
    return True


def _claim_subject_tokens(claim: str) -> set[str]:
    normalized = claim.casefold()
    for separator in (
        " satisfies ",
        " is the best ",
        " is best ",
        " is the better ",
        " is better ",
    ):
        if separator in normalized:
            normalized = normalized.split(separator, 1)[0]
            break
    tokens = set(TOKEN_PATTERN.findall(normalized))
    subject_tokens = tokens - CLAIM_FILLER_TOKENS - GENERIC_SERVICE_TOKENS
    return subject_tokens or tokens


def _answer_negates_claim(user_answer: str, claim_tokens: set[str]) -> bool:
    tokens = TOKEN_PATTERN.findall(user_answer.casefold().replace("n't", " not"))
    if not tokens:
        return False
    claim_positions = [index for index, token in enumerate(tokens) if token in claim_tokens]
    for position in claim_positions:
        window = tokens[max(0, position - 3): position + 4]
        if set(window) & NEGATION_TOKENS:
            return True
    return False


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
    if _is_framed_question_restatement(question, answer_tokens):
        return True
    return False


def _is_framed_question_restatement(question: Question, answer_tokens: set[str]) -> bool:
    if "question" not in answer_tokens and not {"asks", "asking"} & answer_tokens:
        return False
    answer_content_tokens = answer_tokens - QUESTION_RESTATEMENT_FRAME_TOKENS - GENERIC_SERVICE_TOKENS
    if len(answer_content_tokens) < 3:
        return False
    prompt_tokens = set(TOKEN_PATTERN.findall(question.question.casefold())) - GENERIC_SERVICE_TOKENS
    overlap = _token_containment(answer_content_tokens, prompt_tokens)
    if overlap < 0.55:
        return False
    identifying_tokens = _expected_service_tokens(question) - prompt_tokens - GENERIC_SERVICE_TOKENS
    return not bool(identifying_tokens & answer_tokens)


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


def _is_exact_corrected_artifact_answer(question: Question, user_answer: str) -> bool:
    if question.question_type != "artifact_review" or not question.artifact_corrected:
        return False
    normalized_answer = _normalized_code_answer(user_answer)
    if not normalized_answer:
        return False
    expected_answers = {
        _normalized_code_answer(question.artifact_corrected),
        _normalized_code_answer("\n".join(_changed_corrected_artifact_lines(question))),
    }
    return normalized_answer in {answer for answer in expected_answers if answer}


def _changed_corrected_artifact_lines(question: Question) -> list[str]:
    original_lines = question.artifact_body.splitlines()
    corrected_lines = question.artifact_corrected.splitlines()
    changed_lines: list[str] = []
    matcher = SequenceMatcher(a=original_lines, b=corrected_lines)
    for tag, _original_start, _original_end, corrected_start, corrected_end in matcher.get_opcodes():
        if tag != "equal":
            changed_lines.extend(corrected_lines[corrected_start:corrected_end])
    return changed_lines


def _normalized_code_answer(value: str) -> str:
    normalized_lines = []
    for line in value.splitlines():
        stripped = line.strip()
        if stripped.startswith("+") and not stripped.startswith("++"):
            stripped = stripped[1:].strip()
        if stripped:
            normalized_lines.append(stripped)
    return "\n".join(normalized_lines)


def _exact_correct_option_score(question: Question, user_answer: str) -> int:
    return EXACT_CORRECT_OPTION_SCORE if _has_explanatory_detail(question, user_answer) else 85


def _has_explanatory_detail(question: Question, user_answer: str) -> bool:
    answer_tokens = set(TOKEN_PATTERN.findall(user_answer.casefold())) - GENERIC_SERVICE_TOKENS
    if len(answer_tokens) >= 5:
        return True
    required_without_service = set()
    for concept in _required_concepts(question)[1:]:
        required_without_service.update(TOKEN_PATTERN.findall(concept.casefold()))
    required_without_service -= GENERIC_SERVICE_TOKENS
    return len(answer_tokens & required_without_service) >= 2


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
    if _contains_known_service_name(user_answer):
        return False
    for expected in expected_tokens - answer_tokens:
        if any(
            not _is_singular_plural_variant(expected, candidate)
            and _edit_distance(expected, candidate) == 1
            for candidate in answer_tokens
            if len(candidate) >= 3
        ):
            return True
    return False


def _contains_known_service_name(user_answer: str) -> bool:
    knowledge = load_knowledge_base()
    normalized_answer = knowledge.canonicalize(_normalized_service_answer(user_answer))
    for service in knowledge.services:
        terms = (service.name, *service.aliases, *service.tokens)
        for term in terms:
            normalized_term = knowledge.canonicalize(term)
            if normalized_term and re.search(rf"\b{re.escape(normalized_term)}\b", normalized_answer):
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
