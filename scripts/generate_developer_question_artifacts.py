#!/usr/bin/env python3
"""Generate self-authored Developer Associate freeform questions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.config import current_schema_version
from aws_certification_coach.question_fidelity.model import QuestionFidelityModel
from aws_certification_coach.question_templates import load_question_templates
from aws_certification_coach.questions.rubric_metadata import service_selection_rubric_metadata
try:
    from generate_app_question_artifacts import documentation_url_for_option, distractor_feedback, service_metadata_for_option
except ModuleNotFoundError:  # Imported as scripts.generate_developer_question_artifacts in tests.
    from scripts.generate_app_question_artifacts import (
        distractor_feedback,
        documentation_url_for_option,
        service_metadata_for_option,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path("data/original_questions/developer_associate_sources.json"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/developer_question_expansion.json"))
    parser.add_argument("--app-output", type=Path, default=None)
    args = parser.parse_args()

    sources = json.loads(args.sources.read_text(encoding="utf-8"))
    questions = build_questions(sources)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(questions, indent=2) + "\n", encoding="utf-8")
    if args.app_output is not None:
        existing = json.loads(args.app_output.read_text(encoding="utf-8")) if args.app_output.exists() else []
        args.app_output.parent.mkdir(parents=True, exist_ok=True)
        args.app_output.write_text(json.dumps([*existing, *questions], indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(questions)} Developer Associate questions into {args.output}.")


def build_questions(sources: list[dict[str, object]]) -> list[dict[str, object]]:
    model = QuestionFidelityModel()
    schema_version = current_schema_version("QUESTION_SCHEMA_VERSION")
    template_scenarios = _developer_question_scenarios()
    questions: list[dict[str, object]] = []
    for source in sources:
        source_id = str(source["source_id"])
        template_scenario = template_scenarios.get(source_id)
        service = str(source["services"][0])
        concepts = [str(concept) for concept in source["concepts"]]
        question_text = _generated_question(source, template_scenario)
        reference_answer = _reference_answer(source, template_scenario, service)
        options = [_option("A", _correct_option(source, template_scenario), str(source["source_url"]))]
        options.extend(
            _option(option_id, text, documentation_url_for_option(text))
            for option_id, text in zip(["B", "C", "D"], _distractors(source, template_scenario), strict=True)
        )
        row = {
            "schema_version": schema_version,
            "certification": source["certification"],
            "exam_code": source.get("exam_code", ""),
            "domain": source["domain"],
            "difficulty": source["difficulty"],
            "question_type": str(source.get("question_type", "scenario_multiple_choice")),
            "question_category": _question_category(source),
            "question": question_text,
            "reference_answer": reference_answer,
            "key_concepts": concepts,
            **_rubric_metadata(source, template_scenario, service, concepts, reference_answer),
            "original_multiple_choice": {
                "question": question_text,
                "options": options,
                "correct_option_ids": ["A"],
                "explanation": reference_answer,
                "source_name": source["source_name"],
                "source_url": source["source_url"],
                "source_license_notes": source["source_license_notes"],
            },
            "source_examples": [source_id],
            "exam_calibration": {
                "source_type": source["source_type"],
                "exam_style_notes": source["exam_style_notes"],
                "reasoning_pattern": source["reasoning_pattern"],
            },
        }
        row.update(_artifact_metadata(source))
        row["question_fidelity"] = model.score(source, row).__dict__
        questions.append(row)
    return questions


def _option(option_id: str, text: str, source_url: str = "") -> dict[str, str]:
    payload = {"option_id": option_id, "text": text}
    if source_url:
        payload["source_url"] = source_url
        metadata = service_metadata_for_option(text, source_url)
        if metadata:
            payload["metadata"] = metadata
    return payload


def _rubric_metadata(
    source: dict[str, object],
    template_scenario: dict[str, object] | None,
    service: str,
    concepts: list[str],
    reference_answer: str,
) -> dict[str, list[str]]:
    distractors = _distractors(source, template_scenario)
    correct_option = _correct_option(source, template_scenario)
    return service_selection_rubric_metadata(
        service,
        concepts,
        distractors,
        correct_option,
        reference_answer,
        _scenario_purpose(source, reference_answer),
        misconception_subject="scenario",
        acceptable_answer_aliases=_acceptable_answer_aliases(source, template_scenario),
        feedback_builder=distractor_feedback,
    )


def _generated_question(source: dict[str, object], template_scenario: dict[str, object] | None) -> str:
    if template_scenario is not None:
        return str(template_scenario["generated_question"])
    if source.get("generated_question"):
        return str(source["generated_question"])
    raise KeyError(f"No question-template generated_question for source {source['source_id']!r}")


def _correct_option(source: dict[str, object], template_scenario: dict[str, object] | None) -> str:
    if template_scenario is not None:
        return str(template_scenario["correct_option"])
    if source.get("correct_option"):
        return str(source["correct_option"])
    raise KeyError(f"No question-template correct_option for source {source['source_id']!r}")


def _distractors(source: dict[str, object], template_scenario: dict[str, object] | None) -> list[str]:
    if template_scenario is not None:
        return [str(distractor) for distractor in template_scenario["distractors"]]
    if source.get("distractors"):
        return [str(distractor) for distractor in source["distractors"]]
    raise KeyError(f"No question-template distractors for source {source['source_id']!r}")


def _reference_answer(source: dict[str, object], template_scenario: dict[str, object] | None, service: str) -> str:
    if template_scenario is not None:
        return str(template_scenario["reference_answer"])
    if source.get("reference_answer"):
        return str(source["reference_answer"])
    return f"Use {service} for this developer workflow."


def _developer_question_scenarios() -> dict[str, dict[str, object]]:
    return {
        scenario.id: {
            "generated_question": scenario.generated_question,
            "correct_option": scenario.correct_option,
            "reference_answer": scenario.reference_answer,
            "distractors": list(scenario.distractors),
            "acceptable_answer_aliases": list(scenario.acceptable_answer_aliases),
        }
        for scenario in load_question_templates().developer_question_scenarios
    }


def _acceptable_answer_aliases(
    source: dict[str, object],
    template_scenario: dict[str, object] | None,
) -> list[str]:
    if template_scenario is not None:
        return [str(alias) for alias in template_scenario.get("acceptable_answer_aliases", [])]
    return [str(alias) for alias in source.get("acceptable_answer_aliases", [])]


def _scenario_purpose(source: dict[str, object], reference_answer: str) -> str:
    if source.get("expected_issue"):
        return str(source["expected_issue"]).strip().rstrip(".")
    if source.get("reasoning_pattern"):
        return str(source["reasoning_pattern"]).strip().rstrip(".")
    return reference_answer.strip().rstrip(".") or "satisfy the developer workflow"


def _question_category(source: dict[str, object]) -> str:
    text = " ".join(
        str(source.get(field, ""))
        for field in (
            "domain",
            "task_statement",
            "exam_style_notes",
            "distractor_pattern",
            "reasoning_pattern",
            "expected_issue",
        )
    ).casefold()
    text = f"{text} {' '.join(str(concept) for concept in source.get('concepts', []))}".casefold()

    if _has_any(text, ["secret", "credential", "authorizer", "permission", "policy", "least privilege", "kms"]):
        return "security_identity"
    if _has_any(text, ["queue", "sqs", "sns", "event", "stream", "async", "step functions", "lambda"]):
        return "integration_workflows"
    if _has_any(text, ["latency", "trace", "x-ray", "logs insights", "troubleshoot", "diagnose"]):
        return "latency_tradeoff"
    if _has_any(text, ["ttl", "lifecycle", "expiration", "retention", "archive"]):
        return "cost_tradeoff"
    if _has_any(text, ["dead-letter", "dlq", "fail", "retry", "rollback", "transaction"]):
        return "durability_availability_tradeoff"
    if _has_any(text, ["managed", "deployment", "build", "configuration", "throttling", "quota", "pagination"]):
        return "operational_complexity_tradeoff"
    return "integration_workflows"


def _has_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def _artifact_metadata(source: dict[str, object]) -> dict[str, object]:
    if source.get("question_type") != "artifact_review":
        return {}
    return {
        "artifact_type": str(source.get("artifact_type", "")),
        "artifact_language": str(source.get("artifact_language", "")),
        "artifact_body": str(source.get("artifact_body", "")),
        "artifact_context": str(source.get("artifact_context", "")),
        "artifact_corrected": str(source.get("artifact_corrected", "")),
        "expected_issue": str(source.get("expected_issue", "")),
    }


if __name__ == "__main__":
    main()
