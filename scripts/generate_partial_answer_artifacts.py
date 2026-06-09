"""Generate partial-credit answer examples without changing binary training data."""

from __future__ import annotations

import json
from pathlib import Path

from aws_certification_coach.questions.json_repository import JsonQuestionRepository


TRAINING_QUESTION_ARTIFACT = Path("data/questions/transformed_freeform_generated.json")
TRAINING_OUTPUT_PATH = Path("data/training/partial_answer_ratings_generated.json")
HOLDOUT_QUESTION_ARTIFACT = Path("data/verification/questions/transformed_freeform_holdout.json")
HOLDOUT_OUTPUT_PATH = Path("data/verification/answers/partial_answer_ratings_holdout.json")


def main() -> None:
    training_rows = _build_rows(JsonQuestionRepository(TRAINING_QUESTION_ARTIFACT).all())
    holdout_rows = _build_rows(JsonQuestionRepository(HOLDOUT_QUESTION_ARTIFACT).all())

    _write_rows(TRAINING_OUTPUT_PATH, training_rows)
    _write_rows(HOLDOUT_OUTPUT_PATH, holdout_rows)
    print(f"Generated {len(training_rows)} training partial-answer examples at {TRAINING_OUTPUT_PATH}.")
    print(f"Generated {len(holdout_rows)} holdout partial-answer examples at {HOLDOUT_OUTPUT_PATH}.")


def _build_rows(questions) -> list[dict]:
    rows = []
    for question in questions:
        original = question.original_multiple_choice
        correct_option = _correct_option_text(question)
        service_name = _service_name(correct_option)
        concepts = question.key_concepts
        rows.extend(
            _rated_examples(
                question_id=question.question_id,
                service_name=service_name,
                concepts=concepts,
                question_text=original.question if original else question.question,
            )
        )

    return rows


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def _correct_option_text(question) -> str:
    original = question.original_multiple_choice
    if original is None:
        return question.reference_answer
    correct_ids = set(original.correct_option_ids)
    for option in original.options:
        if option.option_id in correct_ids:
            return option.text
    return question.reference_answer


def _service_name(correct_option: str) -> str:
    value = correct_option.strip().rstrip(".")
    for prefix in ("Use ", "Attach ", "Deploy "):
        if value.startswith(prefix):
            value = value[len(prefix) :]
    if " with " in value:
        value = value.split(" with ", 1)[0]
    if " to " in value:
        value = value.split(" to ", 1)[0]
    return value.strip()


def _rated_examples(question_id: str, service_name: str, concepts: list[str], question_text: str) -> list[dict]:
    examples = [
        _example(
            question_id,
            _rating_75_answer(service_name, concepts, index=0),
            0.75,
            "generated_partial_075",
            "Names the correct service or feature and one important permission or design detail, but omits fuller exam wording.",
            service_name,
            concepts,
        ),
        _example(
            question_id,
            _rating_75_answer(service_name, concepts, index=1),
            0.75,
            "generated_partial_075_paraphrase",
            "Uses an abbreviated paraphrase that should still receive substantial credit.",
            service_name,
            concepts,
        ),
        _example(
            question_id,
            _rating_50_answer(service_name, concepts, index=0),
            0.50,
            "generated_partial_050",
            "Names the correct service or feature, but gives little explanation of why it satisfies the requirement.",
            service_name,
            concepts,
        ),
        _example(
            question_id,
            _rating_50_answer(service_name, concepts, index=1),
            0.50,
            "generated_partial_050_paraphrase",
            "Shows partial conceptual understanding without exact service-name wording.",
            service_name,
            concepts,
        ),
        _example(
            question_id,
            _rating_25_answer(question_text),
            0.25,
            "generated_partial_025",
            "Recognizes the general area of the question but does not identify the correct service or mechanism.",
            service_name,
            concepts,
        ),
    ]
    return examples


def _example(
    question_id: str,
    answer: str,
    rating_bucket: float,
    source: str,
    rationale: str,
    service_name: str,
    concepts: list[str],
) -> dict:
    return {
        "question_id": question_id,
        "answer": answer,
        "rating": _continuous_rating(answer, rating_bucket, service_name, concepts),
        "rating_bucket": rating_bucket,
        "source": source,
        "rationale": rationale,
    }


def _continuous_rating(answer: str, rating_bucket: float, service_name: str, concepts: list[str]) -> float:
    normalized_answer = answer.casefold()
    normalized_service = service_name.casefold()
    concept_hits = sum(1 for concept in concepts if concept.casefold() in normalized_answer)
    concept_ratio = concept_hits / max(1, len(concepts))
    service_bonus = 0.08 if normalized_service and normalized_service in normalized_answer else 0.0
    specificity_bonus = min(0.07, len(answer.split()) / 120)
    if rating_bucket >= 0.75:
        value = 0.68 + service_bonus + (0.16 * concept_ratio) + specificity_bonus
    elif rating_bucket >= 0.50:
        value = 0.38 + service_bonus + (0.14 * concept_ratio) + specificity_bonus
    else:
        value = 0.14 + (0.10 * concept_ratio) + specificity_bonus
    return round(max(0.0, min(1.0, value)), 2)


def _rating_75_answer(service_name: str, concepts: list[str], index: int) -> str:
    if "IAM" in service_name or any("temporary credentials" == concept for concept in concepts):
        return [
            "Assume a role with S3 bucket permission.",
            "Use a role for S3 access instead of putting keys on the instance.",
        ][index % 2]
    supporting_concepts = [concept for concept in concepts if concept.casefold() not in service_name.casefold()]
    if index % 2 == 1 and supporting_concepts:
        return f"{service_name} handles this; mention {supporting_concepts[0]}."
    if supporting_concepts:
        return f"Use {service_name} and mention {supporting_concepts[0]}."
    return f"Use {service_name} for the requirement."


def _rating_50_answer(service_name: str, concepts: list[str], index: int) -> str:
    if index % 2 == 1 and concepts:
        return f"This is about {concepts[0]}."
    return f"Use {service_name}."


def _rating_25_answer(question_text: str) -> str:
    lowered = question_text.casefold()
    if "cost" in lowered or "spend" in lowered or "budget" in lowered:
        return "Set up a cost alert."
    if "available" in lowered or "fail" in lowered or "zone" in lowered:
        return "Make the application more redundant."
    if "access" in lowered or "permission" in lowered or "security" in lowered:
        return "Use permissions for the resource."
    return "Use an AWS managed service for this requirement."


if __name__ == "__main__":
    main()
