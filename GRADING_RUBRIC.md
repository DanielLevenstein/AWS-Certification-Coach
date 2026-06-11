# Grading Rubric

## Purpose

AWS Certification Coach grades free-response answers with three independent agents. Each agent evaluates one dimension of the answer and returns a score from 0 to 100. A deterministic aggregator combines those scores into the final percentage.

The agents must not apply model-specific maximum scores or score caps. A concise answer may earn full credit when it identifies the correct AWS answer and covers every required concept. When all required concepts are covered and the answer does not select a distractor, the final score is 100%.

## Scoring Agent Rules
Focus on qualitative assessment for each dimension.
Don't update scoring for subagents with the intent of achieving a specific in the combined evaluator.
Include a full rubric-based scoring system in the user feedback with model feedback for each section indicating why the score was given.

## Final Score

| Agent                       | Weight | Responsibility                                                                                         |
|-----------------------------|-------:|--------------------------------------------------------------------------------------------------------|
| Multiple-choice correctness |    70% | Determine whether the learner selected or described the canonical AWS answer rather than a distractor. |
| Heuristic concept coverage  |    20% | Measure coverage of the required AWS concepts and explanation details.                                 |
| Answer wording              |    10% | Measure clarity, specificity, and readability without requiring unnecessary length.                    |

The normal calculation is:

```text
final_score = round(
    correctness_score * 0.70
    + concept_score * 0.20
    + wording_score * 0.10
)
```

The final score is bounded only to the valid percentage range of 0 through 100. Bounding invalid output is validation, not a grading cap.

### Full-Credit Rule

Return 100% when all the following are true:

- The learner identifies or accurately describes every canonical correct option.
- The learner does not assert a distractor or contradictory AWS service as the answer.
- Every required key concept is covered, including clear synonyms and valid paraphrases.
- The answer is understandable enough to demonstrate the learner's intent.

Grammar, spelling, answer length, and preferred phrasing must not prevent 100% when these conditions are met. Minor service-name misspellings may reduce wording or correctness confidence in proportion to ambiguity, but they do not trigger a fixed score or ceiling.

## Agent 1: Multiple-Choice Correctness

This agent is logically separate from heuristic grading. It uses the original multiple-choice provenance when available: the canonical correct option IDs and text, distractor option text, and source explanation. It may also use the reference answer when no original multiple-choice item exists.

### Evaluation Criteria

- **100:** The answer selects or unambiguously describes all canonical correct options and rejects or avoids all distractors.
- **75–99:** The primary answer is correct, but part of a multi-answer requirement is missing or a minor ambiguity remains.
- **40–74:** The answer shows relevant AWS knowledge but does not clearly select the canonical answer.
- **1–39:** The answer mostly supports a distractor, names the wrong service, or merely restates the question.
- **0:** The answer is blank, unrelated, or explicitly selects only an incorrect option.

For multiple-answer questions, mentioning several AWS services is not sufficient. The learner must make the canonical selections clear. A distractor presented only as a contrast or rejection is not treated as a selected answer.

### Output

The agent returns:

- `score`: integer from 0 to 100.
- `correct_option_coverage`: canonical option IDs or meanings covered by the answer.
- `selected_distractors`: distractors incorrectly asserted by the learner.
- `feedback`: a short explanation of the correctness judgment.

## Agent 2: Heuristic Concept Coverage

This agent does not decide which multiple-choice option is correct. It independently evaluates how much of the expected AWS reasoning is present by comparing the learner answer with the key concepts and reference explanation.

Concept matching is semantic. Exact string matches are useful evidence but are not required; accepted aliases, acronyms, singular/plural forms, and accurate paraphrases receive credit.

### Evaluation Criteria

- **100:** Every required concept is accurately covered with no material contradiction.
- **75–99:** Most concepts are covered; omissions are minor and do not change the primary conclusion.
- **40–74:** Some concepts are correct, but important mechanisms, constraints, or outcomes are missing.
- **1–39:** Only a small fragment of the expected reasoning is present.
- **0:** No required concept is demonstrated.

Each required concept contributes equally unless the question artifact later defines explicit concept weights. The agent reports covered and missing concepts rather than applying fixed penalties or score ceilings.

### Output

The agent returns:

- `score`: integer from 0 to 100.
- `covered_concepts`: required concepts demonstrated by the answer.
- `missing_concepts`: required concepts not demonstrated by the answer.
- `feedback`: a short explanation of the concept judgment.

## Agent 3: Answer Wording

This agent evaluates whether the response communicates its AWS knowledge clearly. It must not duplicate correctness or concept-coverage grading.

### Evaluation Criteria

- **100:** Clear, specific, readable, and internally consistent.
- **75–99:** Understandable with minor spelling, grammar, or organization issues.
- **40–74:** Meaning can be recovered, but vague wording or fragments make the answer materially harder to interpret.
- **1–39:** Severely unclear or contradictory wording obscures the intended answer.
- **0:** Blank or unintelligible.

Full sentences are encouraged but not mandatory. A short answer can earn 100 when it communicates the complete answer clearly. Verbosity does not earn credit by itself.

### Output

The agent returns:

- `score`: integer from 0 to 100.
- `issues`: clarity, spelling, specificity, or contradiction issues.
- `feedback`: a short wording recommendation.

## Aggregation And Feedback

The aggregator is deterministic and is not a fourth grading agent. It validates each agent's output, applies the documented weights, enforces the full-credit rule, and returns the existing learner-facing `EvaluationResult`.

- `missing_concepts` comes from the heuristic concept-coverage agent.
- `suggested_improvements` is assembled from missing concepts, selected distractors, and wording issues.
- `feedback` summarizes the three judgments without exposing model confidence or internal implementation details.
- `detailed_answer` uses the reviewed reference answer and must cover every missing concept.

## Examples

| Learner answer                                        | Correctness | Concepts | Wording | Final |
|-------------------------------------------------------|------------:|---------:|--------:|------:|
| Correct service, all concepts, concise wording        |         100 |      100 |     100 |   100 |
| Correct service and most concepts, one minor omission |         100 |       80 |      90 |    95 |
| Correct service name with little explanation          |         100 |       40 |      80 |    86 |
| Relevant explanation but wrong canonical service      |          20 |       70 |      90 |    37 |
| Question restatement without an answer                |          10 |       10 |      60 |    15 |

These examples illustrate weighting rather than fixed outcomes. Agents score the evidence in the specific question and answer; they do not clamp results to letter-grade ceilings.
