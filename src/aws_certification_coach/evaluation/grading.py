"""Independent grading agents and deterministic score aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from aws_certification_coach.domain import EvaluationResult, MultipleChoiceOption, Question


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
GENERIC_TOKENS = {"amazon", "aws", "service", "the", "use"}


@dataclass(frozen=True)
class CorrectnessJudgment:
    score: int
    correct_option_coverage: list[str] = field(default_factory=list)
    selected_distractors: list[str] = field(default_factory=list)
    feedback: str = field(default="")
    rubric_level: str = ""


@dataclass(frozen=True)
class ConceptCoverageJudgment:
    score: int
    covered_concepts: list[str] = field(default_factory=list)
    missing_concepts: list[str] = field(default_factory=list)
    feedback: str = ""
    rubric_level: str = ""


@dataclass(frozen=True)
class WordingJudgment:
    score: int
    issues: list[str] = field(default_factory=list)
    feedback: str = ""
    rubric_level: str = ""


class MultipleChoiceCorrectnessAgent:
    """Grades canonical option selection independently of explanation quality."""

    def evaluate(
        self,
        question: Question,
        user_answer: str,
        evidence_score: float | None = None,
    ) -> CorrectnessJudgment:
        answer = _normalized(user_answer)
        if not answer:
            return CorrectnessJudgment(0, feedback="")

        original = question.original_multiple_choice
        if original is None:
            score = _reference_similarity(question.reference_answer, user_answer)
            if evidence_score is not None:
                score = round((score + evidence_score) / 2)
            return CorrectnessJudgment(
                _valid_score(score),
                correct_option_coverage=["reference_answer"] if score == 100 else [],
                feedback="",
            )

        correct_ids = set(original.correct_option_ids)
        correct_options = [option for option in original.options if option.option_id in correct_ids]
        distractors = [option for option in original.options if option.option_id not in correct_ids]
        exact_correct_answer = (
            answer == _normalized(question.reference_answer)
            or any(_same_option_meaning(option.text, user_answer) for option in correct_options)
        )
        covered = [
            option.option_id
            for option in correct_options
            if _option_is_covered(option.text, user_answer)
        ]
        selected_distractors = [
            option.option_id
            for option in distractors
            if _option_is_asserted(option.text, user_answer)
        ]

        short_selection = _looks_like_short_service_selection(user_answer)
        if exact_correct_answer and not selected_distractors:
            score = 100
            covered = [option.option_id for option in correct_options]
        elif _is_question_restatement(question, user_answer):
            score = 10
            covered = []
        elif selected_distractors and not covered:
            score = 0
        elif short_selection:
            score = _misspelled_correct_option_score(correct_options, user_answer)
        elif len(covered) == len(correct_options) and not selected_distractors:
            score = 100
        elif covered:
            score = round(100 * len(covered) / max(1, len(correct_options)))
        else:
            score = round(evidence_score) if evidence_score is not None else _reference_similarity(
                question.reference_answer,
                user_answer,
            )

        return CorrectnessJudgment(
            score=_valid_score(score),
            correct_option_coverage=covered,
            selected_distractors=selected_distractors,
            feedback="",
        )


class ConceptCoverageAgent:
    """Grades required AWS concepts without selecting multiple-choice options."""

    def evaluate(self, question: Question, user_answer: str) -> ConceptCoverageJudgment:
        if not question.key_concepts:
            score = 100 if user_answer.strip() else 0
            return ConceptCoverageJudgment(score, feedback="")

        if _reference_is_covered(question.reference_answer, user_answer):
            covered = list(question.key_concepts)
        else:
            covered = [
                concept
                for concept in question.key_concepts
                if _concept_is_covered(concept, user_answer)
            ]
        missing = [concept for concept in question.key_concepts if concept not in covered]
        score = round(100 * len(covered) / len(question.key_concepts))
        return ConceptCoverageJudgment(score, covered, missing, feedback="")


class AnswerWordingAgent:
    """Grades clarity without duplicating technical correctness judgments."""

    def evaluate(self, question: Question, user_answer: str) -> WordingJudgment:
        del question
        stripped = user_answer.strip()
        if not stripped:
            return WordingJudgment(0, ["The answer is blank."], feedback="")
        tokens = _tokens(stripped)
        if not tokens:
            return WordingJudgment(0, ["The answer is unintelligible."], feedback="")

        issues: list[str] = []
        if len(tokens) == 1 and tokens <= GENERIC_TOKENS:
            issues.append("The answer is too vague to interpret.")
        score = 50 if issues else 100
        return WordingJudgment(
            score,
            issues,
            feedback="",
        )


class EvaluationAggregator:
    """Combines independent agent judgments according to the grading rubric."""

    def aggregate(
        self,
        question: Question,
        correctness: CorrectnessJudgment,
        concepts: ConceptCoverageJudgment,
        wording: WordingJudgment,
    ) -> EvaluationResult:
        original = question.original_multiple_choice
        all_correct_options = (
            original is None
            or set(correctness.correct_option_coverage) == set(original.correct_option_ids)
        )
        full_credit = (
            all_correct_options
            and not correctness.selected_distractors
            and not concepts.missing_concepts
            and wording.score > 0
        )
        score = 100 if full_credit else round(
            correctness.score * 0.70 + concepts.score * 0.20 + wording.score * 0.10
        )
        improvements = [f"Explain {concept}." for concept in concepts.missing_concepts]
        if correctness.selected_distractors:
            improvements.append("Replace the selected distractor with the canonical AWS answer.")
        improvements.extend(wording.issues)
        feedback = _scorecard_feedback(
            correctness,
            concepts,
            wording,
            score,
            full_credit,
        )
        return EvaluationResult(
            score=_valid_score(score),
            missing_concepts=concepts.missing_concepts,
            suggested_improvements=improvements,
            feedback=feedback,
            detailed_answer=question.reference_answer,
        )


def evaluate_with_agents(
    question: Question,
    user_answer: str,
    evidence_score: float | None = None,
) -> EvaluationResult:
    correctness = MultipleChoiceCorrectnessAgent().evaluate(question, user_answer, evidence_score)
    concepts = ConceptCoverageAgent().evaluate(question, user_answer)
    wording = AnswerWordingAgent().evaluate(question, user_answer)
    return EvaluationAggregator().aggregate(question, correctness, concepts, wording)


def _valid_score(value: float | int) -> int:
    return max(0, min(100, round(value)))


def _scorecard_feedback(
    correctness: CorrectnessJudgment,
    concepts: ConceptCoverageJudgment,
    wording: WordingJudgment,
    final_score: int,
    full_credit: bool,
) -> str:
    sections = (
        ("Multiple-choice correctness", 70, correctness),
        ("Heuristic concept coverage", 20, concepts),
        ("Answer wording", 10, wording),
    )
    lines = ["Scoring rubric:"]
    for name, weight, judgment in sections:
        raw_score = _valid_score(judgment.score)
        level = judgment.rubric_level.strip() or _rubric_level(raw_score)
        contribution = raw_score * weight / 100
        lines.append(
            f"- {name} ({weight}%): {raw_score}/100, {level}; "
            f"weighted contribution {contribution:.1f}/{weight}."
        )
    if full_credit:
        lines.append("- Full-credit rule: applied because all canonical answers and required concepts were covered.")
    model_feedback = " ".join(
        feedback.strip()
        for feedback in (correctness.feedback, concepts.feedback, wording.feedback)
        if feedback.strip()
    )
    if model_feedback:
        lines.append(f"Model feedback: {model_feedback}")
    lines.append(f"Final score: {_valid_score(final_score)}/100.")
    return "\n".join(lines)


def _rubric_level(score: int) -> str:
    if score == 100:
        return "full credit"
    if score >= 75:
        return "strong with minor omissions"
    if score >= 40:
        return "partial credit"
    if score >= 1:
        return "minimal credit"
    return "no credit"


def _normalized(value: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(value.casefold()))


def _tokens(value: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(value.casefold()))


def _option_is_covered(option_text: str, user_answer: str) -> bool:
    option_tokens = _tokens(option_text) - GENERIC_TOKENS
    answer_tokens = _tokens(user_answer)
    return bool(option_tokens) and option_tokens <= answer_tokens


def _same_option_meaning(option_text: str, user_answer: str) -> bool:
    return (_tokens(option_text) - GENERIC_TOKENS) == (_tokens(user_answer) - GENERIC_TOKENS)


def _option_is_asserted(option_text: str, user_answer: str) -> bool:
    normalized_option = _normalized(option_text)
    normalized_answer = _normalized(user_answer)
    if normalized_answer == normalized_option:
        return True
    option_tokens = _tokens(option_text) - GENERIC_TOKENS
    answer_tokens = _tokens(user_answer)
    rejection_tokens = {"not", "instead", "rather"}
    return (
        bool(option_tokens)
        and option_tokens <= answer_tokens
        and not (answer_tokens & rejection_tokens)
    )


def _reference_similarity(reference_answer: str, user_answer: str) -> int:
    reference_tokens = _tokens(reference_answer) - GENERIC_TOKENS
    answer_tokens = _tokens(user_answer) - GENERIC_TOKENS
    if not reference_tokens:
        return 100 if answer_tokens else 0
    return round(100 * len(reference_tokens & answer_tokens) / len(reference_tokens))


def _looks_like_short_service_selection(user_answer: str) -> bool:
    normalized = _normalized(user_answer)
    tokens = normalized.split()
    return len(tokens) <= 6 and (normalized.startswith("use ") or len(tokens) <= 3)


def _misspelled_correct_option_score(
    correct_options: list[MultipleChoiceOption],
    user_answer: str,
) -> int:
    answer_tokens = _tokens(user_answer) - GENERIC_TOKENS
    expected_tokens: set[str] = set()
    for option in correct_options:
        expected_tokens.update(_tokens(option.text) - GENERIC_TOKENS)
    if len(answer_tokens) != 1 or len(expected_tokens) != 1:
        return 0
    similarities = [
        max(
            1 - (_edit_distance(expected, actual) / (max(len(expected), len(actual)) + 1))
            for actual in answer_tokens
        )
        for expected in expected_tokens
    ]
    average_similarity = sum(similarities) / len(similarities)
    return round(100 * average_similarity) if average_similarity >= 0.7 else 0


def _reference_is_covered(reference_answer: str, user_answer: str) -> bool:
    reference_tokens = {_stem(token) for token in _tokens(reference_answer) - GENERIC_TOKENS}
    answer_tokens = {_stem(token) for token in _tokens(user_answer) - GENERIC_TOKENS}
    return bool(reference_tokens) and reference_tokens <= answer_tokens


def _concept_is_covered(concept: str, user_answer: str) -> bool:
    concept_tokens = {_stem(token) for token in _tokens(concept) - GENERIC_TOKENS}
    answer_tokens = {_stem(token) for token in _tokens(user_answer) - GENERIC_TOKENS}
    return bool(concept_tokens) and concept_tokens <= answer_tokens


def _stem(token: str) -> str:
    if token.startswith("protect") or token == "protection":
        return "protect"
    for suffix in ("ation", "tion", "ment", "ing", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 3:
            return token[: -len(suffix)]
    return token


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


def _is_question_restatement(question: Question, user_answer: str) -> bool:
    answer_tokens = _tokens(user_answer)
    if len(answer_tokens) < 4:
        return False
    prompts = [question.question]
    if question.original_multiple_choice:
        prompts.append(question.original_multiple_choice.question)
    expected_tokens: set[str] = set()
    if question.original_multiple_choice:
        correct_ids = set(question.original_multiple_choice.correct_option_ids)
        for option in question.original_multiple_choice.options:
            if option.option_id in correct_ids:
                expected_tokens.update(_tokens(option.text) - GENERIC_TOKENS)
    for prompt in prompts:
        prompt_tokens = _tokens(prompt)
        if len(answer_tokens & prompt_tokens) / len(answer_tokens) < 0.9:
            continue
        identifying_tokens = expected_tokens - prompt_tokens
        if identifying_tokens & answer_tokens:
            continue
        return True
    return False
