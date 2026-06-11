import json

from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.evaluation.grading import evaluate_with_agents
from aws_certification_coach.evaluation.prompting import EvaluationPromptBuilder, EvaluationResponseParser


def _question() -> Question:
    return Question(
        question_id="test",
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Which service manages encryption keys?",
        reference_answer="Use AWS KMS to create and manage encryption keys for data protection.",
        key_concepts=["AWS KMS", "encryption keys", "data protection"],
        original_multiple_choice=MultipleChoiceQuestion(
            question="Which service manages encryption keys?",
            options=[
                MultipleChoiceOption("A", "Use AWS KMS."),
                MultipleChoiceOption("B", "Use AWS WAF."),
            ],
            correct_option_ids=["A"],
        ),
    )


def test_complete_answer_receives_100_without_a_model_score_cap():
    result = evaluate_with_agents(
        _question(),
        "AWS KMS creates and manages encryption keys that protect data.",
        evidence_score=73,
    )

    assert result.score == 100
    assert result.missing_concepts == []
    assert "Full-credit rule: applied" in result.feedback


def test_multiple_choice_correctness_is_separate_from_concept_coverage():
    result = evaluate_with_agents(
        _question(),
        "AWS WAF protects data and uses encryption keys.",
        evidence_score=95,
    )

    assert result.score < 70
    assert "AWS KMS" in result.missing_concepts


def test_model_prompt_and_parser_use_three_independent_agent_results():
    question = _question()
    prompt = EvaluationPromptBuilder().build(question, "AWS KMS manages encryption keys.")
    assert '"correctness"' in prompt
    assert '"concept_coverage"' in prompt
    assert '"wording"' in prompt
    assert '"rubric_level"' in prompt
    assert "Do not adjust an agent score" in prompt

    response = json.dumps(
        {
            "correctness": {
                "score": 100,
                "rubric_level": "full credit",
                "correct_option_coverage": ["A"],
                "selected_distractors": [],
                "feedback": "Correct option selected.",
            },
            "concept_coverage": {
                "score": 100,
                "rubric_level": "full credit",
                "covered_concepts": question.key_concepts,
                "missing_concepts": [],
                "feedback": "All concepts covered.",
            },
            "wording": {
                "score": 100,
                "rubric_level": "full credit",
                "issues": [],
                "feedback": "Clear.",
            },
        }
    )

    result = EvaluationResponseParser().parse(response, question)
    assert result.score == 100
    assert "Multiple-choice correctness (70%): 100/100, full credit" in result.feedback
    assert "Heuristic concept coverage (20%): 100/100, full credit" in result.feedback
    assert "Answer wording (10%): 100/100, full credit" in result.feedback
    assert "Model feedback: Correct option selected." in result.feedback
    assert "Final score: 100/100." in result.feedback
