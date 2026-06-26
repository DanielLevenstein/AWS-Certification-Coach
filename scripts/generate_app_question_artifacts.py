"""Generate app-facing AWS certification questions separate from training data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.config import current_schema_version
from aws_certification_coach.knowledge_base import load_knowledge_base
from aws_certification_coach.question_templates import load_question_templates


SERVICE_SELECTION_TEMPLATE_ID = "service-selection-freeform"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/questions/sample_questions.json")
    parser.add_argument("--count", type=int, default=160)
    args = parser.parse_args()

    questions = _build_app_questions(args.count)
    _write_json(args.output, questions)
    print(f"Generated {len(questions)} app questions into {args.output}.")


def _build_app_questions(count: int) -> list[dict]:
    knowledge = load_knowledge_base()
    template_catalog = load_question_templates()
    template = template_catalog.get(SERVICE_SELECTION_TEMPLATE_ID)
    prompt_variants = template.prompt_variants
    scenarios = template_catalog.service_scenarios
    max_count = len(scenarios) * len(prompt_variants)
    if count > max_count:
        raise ValueError(f"Cannot generate {count} unique app questions from {max_count} source scenarios.")

    questions = []
    schema_version = current_schema_version("QUESTION_SCHEMA_VERSION")
    for index in range(count):
        scenario = scenarios[index % len(scenarios)]
        variant = prompt_variants[index // len(scenarios)]
        service = knowledge.service_by_id(scenario.service_id)
        concepts = list(scenario.key_concepts)
        distractors = list(scenario.distractors)
        correct_option = template.option_pattern.format(service_name=service.name)
        explanation = template.reference_answer_pattern.format(service_name=service.name, purpose=scenario.purpose)
        mcq_question = variant.format(purpose=scenario.purpose)
        questions.append(
            {
                "schema_version": schema_version,
                "certification": scenario.certification,
                "exam_code": scenario.exam_code,
                "domain": scenario.domain,
                "difficulty": scenario.difficulty,
                "question_type": template.question_type,
                "question": template.question_pattern.format(purpose=scenario.purpose),
                "reference_answer": explanation,
                "key_concepts": concepts,
                "source_url": service.source_url,
                "question_template_id": template.id,
                **_rubric_metadata(service.name, concepts, distractors, correct_option, explanation, scenario.purpose),
                "original_multiple_choice": {
                    "question": mcq_question,
                    "options": [
                        _option("A", correct_option),
                        _option("B", template.option_pattern.format(service_name=distractors[0])),
                        _option("C", template.option_pattern.format(service_name=distractors[1])),
                        _option("D", template.option_pattern.format(service_name=distractors[2])),
                    ],
                    "correct_option_ids": list(template.selection_rule["correct_option_ids"]),
                    "explanation": explanation,
                    "source_name": f"AWS Documentation: {service.name}",
                    "source_url": service.source_url,
                    "source_license_notes": "AWS documentation was used for topic grounding; this question text is self-authored.",
                },
            }
        )
    return questions


def _rubric_metadata(
    service_name: str,
    concepts: list[str],
    distractors: list[str],
    correct_option: str,
    explanation: str,
    purpose: str,
) -> dict[str, list[str]]:
    return {
        "required_concepts": concepts,
        "bonus_concepts": [],
        "common_misconceptions": [f"{distractor} is the best fit for this requirement." for distractor in distractors],
        "acceptable_answers": [correct_option, explanation, service_name],
        "must_not_claim": [f"{distractor} satisfies the scenario better than {service_name}." for distractor in distractors],
        "do_not_claim_explanation": [
            f"{service_name} is a better option because it is designed to {purpose}, while {distractor} does not satisfy that requirement."
            for distractor in distractors
        ],
    }


def _option(option_id: str, text: str) -> dict[str, str]:
    payload = {"option_id": option_id, "text": text}
    source_url = documentation_url_for_option(text)
    if source_url:
        payload["source_url"] = source_url
        payload["metadata"] = service_metadata_for_option(text, source_url)
    return payload


def documentation_url_for_option(text: str) -> str:
    service = _knowledge_service_for_option(text)
    return service.source_url if service else ""


def service_name_for_option(text: str) -> str:
    service = _knowledge_service_for_option(text)
    return service.name if service else ""


def service_metadata_for_option(text: str, source_url: str = "") -> dict[str, str]:
    service_name = service_name_for_option(text)
    service = _knowledge_service_for_option(text)
    resolved_url = source_url or (service.source_url if service else "")
    if not service_name and resolved_url:
        service_name = service_name_for_source_url(resolved_url)
    if not service_name or not resolved_url:
        return {}
    knowledge_metadata = _knowledge_service_metadata(service_name, resolved_url)
    if knowledge_metadata:
        return knowledge_metadata
    return {
        "service_id": _metadata_service_id(service_name),
        "service_name": service_name,
        "source_url": resolved_url,
    }


def service_name_for_source_url(source_url: str) -> str:
    for service in load_knowledge_base().services:
        if source_url == service.source_url:
            return service.name
    return ""


def _knowledge_service_metadata(service_name: str, source_url: str = "") -> dict[str, str]:
    service = load_knowledge_base().service_for_name(service_name)
    if service:
        return {
            "service_id": service.id,
            "service_name": service.name,
            "source_url": source_url or service.source_url,
        }
    return {}


def _knowledge_service_for_option(text: str):
    knowledge = load_knowledge_base()
    normalized = _normalized_option_text(text)
    for service in knowledge.services:
        terms = (service.name, *service.aliases, *service.tokens)
        for term in terms:
            normalized_term = _normalized_option_text(term)
            if normalized == normalized_term or normalized_term in normalized or normalized in normalized_term:
                return service
    return None


def _normalized_option_text(text: str) -> str:
    value = " ".join(text.casefold().replace(".", "").split())
    return value.removeprefix("use ")


def _metadata_service_id(service_name: str) -> str:
    tokens = _normalized_option_text(service_name).split()
    if tokens and tokens[0] in {"amazon", "aws"}:
        tokens = tokens[1:]
    return "-".join(tokens)


def _write_json(path: str, payload: list[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
