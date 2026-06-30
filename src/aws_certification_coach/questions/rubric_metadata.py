"""Helpers for generated learner-answer rubric metadata."""

from __future__ import annotations

from collections.abc import Callable, Sequence


FeedbackBuilder = Callable[[str, str, str], str]


def service_selection_rubric_metadata(
    service_name: str,
    concepts: Sequence[str],
    distractors: Sequence[str],
    correct_option: str,
    reference_answer: str,
    purpose: str,
    *,
    misconception_subject: str = "requirement",
    acceptable_answer_aliases: Sequence[str] = (),
    feedback_builder: FeedbackBuilder | None = None,
) -> dict[str, list[str]]:
    """Build generated answer-rubric fields from question-generation inputs."""

    feedback = feedback_builder or default_distractor_feedback
    acceptable_answers = [
        correct_option,
        reference_answer,
        service_name,
        *acceptable_answer_aliases,
    ]
    return {
        "required_concepts": list(concepts),
        "bonus_concepts": [],
        "common_misconceptions": common_misconceptions_from_distractors(
            distractors,
            subject=misconception_subject,
        ),
        "acceptable_answers": list(dict.fromkeys(acceptable_answers)),
        "must_not_claim": must_not_claim_from_distractors(distractors, service_name),
        "do_not_claim_explanation": [
            feedback(service_name, distractor, purpose)
            for distractor in distractors
        ],
    }


def common_misconceptions_from_distractors(
    distractors: Sequence[str],
    *,
    subject: str = "requirement",
) -> list[str]:
    return [f"{distractor} is the best fit for this {subject}." for distractor in distractors]


def must_not_claim_from_distractors(distractors: Sequence[str], service_name: str) -> list[str]:
    return [f"{distractor} satisfies the scenario better than {service_name}." for distractor in distractors]


def default_distractor_feedback(service_name: str, distractor: str, purpose: str) -> str:
    if is_s3_lifecycle_bucket_policy_boundary(service_name, distractor):
        return (
            f"{service_name} is a better option because it is designed to {purpose}. "
            "S3 Lifecycle rules manage object transitions and expiration over time; "
            "S3 bucket policies are resource-based access policies that allow or deny requests to the bucket and objects."
        )
    return (
        f"{service_name} is a better option because it is designed to {purpose}, "
        f"while {distractor} does not satisfy that requirement."
    )


def is_s3_lifecycle_bucket_policy_boundary(service_name: str, distractor: str) -> bool:
    return "s3 lifecycle" in service_name.casefold() and "bucket polic" in distractor.casefold()
