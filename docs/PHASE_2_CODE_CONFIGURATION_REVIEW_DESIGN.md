# Phase 2 Code And Configuration Review Design

## Release Target

Target release: `v2.4.1`

Phase 2 extends AWS Certification Coach from concept-only freeform questions into artifact-based review questions. Learners should inspect short IAM policies, Lambda handlers, SDK usage snippets, and CloudFormation/SAM fragments, then explain the problem, best fix, or expected behavior.

This phase remains a design and preparation phase until the Codex skills and review contract are in place. Do not make runtime code changes before the skills and this design are reviewed.

## Relationship To Existing Roadmap

Phase 1 improved question quality, distractors, and exam realism. Phase 2 keeps the same release-quality language from `docs/QUESTION_EXPANSION_FEATURE.md`, `docs/QUESTION_EXPANSION_ARCHITECTURE.md`, and `docs/ANSWER_RUBRIC.md`, but adds questions where the learner must reason from realistic code or configuration artifacts.

Use the same distinction throughout this phase:

- `learner-answer grading`: A/B/C/D/F evaluation of the learner response.
- `question fidelity`: release-facing score for generated question quality.
- `AWS-valid`: technically accurate, according to AWS documentation and service behavior.
- `exam-valid`: aligned with AWS Certified Developer Associate scenario reasoning.

## Goals

- Add artifact-review question types for IAM, Lambda, SDK usage, and CloudFormation/SAM.
- Keep artifact snippets short enough for a study session while still requiring applied reasoning.
- Preserve source provenance and artifact metadata for review, fidelity scoring, and release notes.
- Teach secure, maintainable AWS development practices without encouraging unsafe shortcuts.
- Keep generated questions self-authored and based on allowed public documentation, exam objectives, or self-authored scenarios.

## Non-Goals

- Do not add runtime code behavior in this phase before the design and Codex skills are committed.
- Do not ingest exam dumps, paid practice-bank questions, or restricted Skill Builder text.
- Do not build a full static analyzer, policy simulator, CloudFormation linter, or Lambda execution sandbox for `v2.4.1`.
- Do not grade learners by executing their code.
- Do not mix question-fidelity review with learner-answer grading.

## Question Families

### IAM Policy Review

Learners inspect an IAM policy, trust policy, resource policy, or permission boundary fragment and identify the security or access-control issue.

Typical prompts:

- Identify the least-privilege problem in this policy.
- Explain why this trust policy is unsafe.
- Recommend the narrowest permission change that satisfies the scenario.
- Predict whether this request is allowed or denied and explain the policy evaluation path.

Required metadata:

- `artifact_type`: `iam_policy`, `iam_trust_policy`, `iam_resource_policy`, or `iam_permission_boundary`
- `policy_scope`: identity, resource, trust, boundary, or service control policy
- `action_scope`: exact AWS actions under review
- `resource_scope`: resource ARN pattern or wildcard
- `security_concepts`: least privilege, confused deputy, condition keys, explicit deny, cross-account trust, temporary credentials, or service roles

Hard rejection examples:

- Recommends broad `*` permissions when the scenario requires least privilege.
- Treats IAM users and IAM roles as interchangeable for temporary credentials.
- Ignores explicit deny precedence.
- Uses copied official or restricted policy-question wording.

### Lambda Code Review

Learners inspect a short Lambda handler or deployment snippet and identify correctness, reliability, security, configuration, or operational issues.

Typical prompts:

- Explain why this Lambda function times out or retries unexpectedly.
- Identify the missing configuration for environment-specific values.
- Recommend how to handle failures from an event source.
- Explain why secrets should not be hard-coded in the function package.

Required metadata:

- `artifact_type`: `lambda_code`, `lambda_event_source`, or `lambda_configuration`
- `runtime`: Python, Node.js, Java, or other runtime when relevant
- `trigger`: API Gateway, EventBridge, SQS, DynamoDB Streams, S3, or direct invoke
- `operational_concepts`: timeout, concurrency, retries, idempotency, dead-letter handling, cold start, environment variables, layers, or permissions
- `security_concepts`: execution role, secrets handling, input validation, VPC access, or logging hygiene

Hard rejection examples:

- Claims Lambda has unlimited runtime or persistent local state guarantees.
- Recommends hard-coded credentials.
- Confuses invocation permissions with execution-role permissions.
- Requires execution of learner code to decide the grade.

### SDK Usage Review

Learners inspect a short AWS SDK usage snippet and identify a bad client configuration, missing pagination, missing retries, unsafe credential handling, wrong API call, or incorrect error handling.

Typical prompts:

- Identify why this SDK call misses results.
- Explain how credentials should be provided to this workload.
- Recommend the correct API or paginator for the scenario.
- Explain how to make this write operation idempotent.

Required metadata:

- `artifact_type`: `sdk_usage`
- `language`: Python, JavaScript, Java, .NET, or other SDK language when relevant
- `service`: the AWS service under review
- `sdk_concepts`: client configuration, region selection, credentials provider chain, pagination, waiters, retries, idempotency tokens, exception handling, or request throttling
- `failure_mode`: incomplete results, wrong region, access denied, throttling, duplicated writes, stale credentials, or missing error handling

Hard rejection examples:

- Encourages static access keys in source code.
- Treats every paginated API as returning all results in one call.
- Ignores regional service behavior when the scenario depends on region.
- Makes version-specific SDK claims without source metadata.

### CloudFormation And SAM Review

Learners inspect a small CloudFormation or SAM template fragment and identify configuration, dependency, permission, or deployment behavior.

Typical prompts:

- Identify the missing permission or event-source mapping.
- Explain how this SAM resource expands into AWS resources.
- Recommend the safest parameter or output handling.
- Explain why this stack update would fail or replace a resource.

Required metadata:

- `artifact_type`: `cloudformation_template` or `sam_template`
- `resource_types`: AWS resource types in the snippet
- `deployment_concepts`: intrinsic functions, parameters, outputs, conditions, dependencies, transforms, change sets, stack updates, drift, or rollback
- `serverless_concepts`: `AWS::Serverless::Function`, API events, event-source mappings, policies, environment variables, or permissions
- `failure_mode`: invalid reference, missing permission, replacement update, malformed policy, circular dependency, or unsafe output

Hard rejection examples:

- Claims CloudFormation automatically validates application code behavior.
- Ignores replacement risk when a resource property change requires replacement.
- Recommends outputting secrets in plaintext.
- Confuses SAM policy templates with arbitrary IAM policies without explaining the difference.

## Artifact Question Contract

Phase 2 questions should extend the existing generated question contract with artifact-specific fields.

Recommended fields:

- `question_type`: `artifact_review`
- `artifact_type`
- `certification`
- `exam_code`
- `domain`
- `task_statement`
- `difficulty`
- `question`
- `artifact_language`
- `artifact_body`
- `artifact_context`
- `artifact_corrected`
- `expected_issue`
- `reference_answer`
- `required_concepts`
- `bonus_concepts`
- `common_misconceptions`
- `acceptable_answers`
- `must_not_claim`
- `source_examples`
- `question_fidelity`
- `exam_calibration`

`artifact_body` should contain only short, self-authored snippets. `artifact_corrected` should contain the corrected full artifact shown after evaluation for questions with code or configuration examples; changed lines should be highlightable by comparing it with `artifact_body`. Keep snippets compact enough for learners to inspect without scrolling through large files. Prefer one primary issue per question, with optional secondary observations as bonus concepts.

## Artifact Authoring Rules

- Use self-authored snippets based on public AWS documentation and allowed calibration metadata.
- Keep examples minimal and realistic: no toy snippets that make the answer obvious, and no full production templates.
- Include enough scenario context to decide the best answer.
- Avoid secrets, real account IDs, real ARNs, real customer names, and copied production code.
- Use placeholders such as `123456789012`, `example-bucket`, and `my-function` where identifiers are necessary.
- Do not require network calls, local execution, deployment, or AWS credentials to answer the question.
- Make the unsafe or incorrect part visible in the artifact unless the question is explicitly about missing configuration.

## Learner Answer Grading

Artifact-review answers still use the A/B/C/D/F rubric from `docs/ANSWER_RUBRIC.md`.

An A answer should:

- Identify the concrete issue in the artifact.
- Explain why it matters for the scenario.
- Recommend a technically accurate AWS fix.
- Avoid unsafe security or operational claims.

A B answer usually identifies the issue but gives limited reasoning or a less precise fix.

A C answer recognizes the relevant AWS area but misses the exact root cause or best remediation.

A D answer mentions a related concept but fails the main artifact issue.

An F answer points to the wrong service category, recommends unsafe behavior, contradicts the artifact, or provides no meaningful AWS reasoning.

## Question Fidelity Review

Artifact questions should use the existing Phase 1 fidelity dimensions, with artifact-specific evidence:

| Dimension             | Phase 2 Interpretation                                                                                             |
|:----------------------|:-------------------------------------------------------------------------------------------------------------------|
| Concept fidelity      | The artifact tests the intended AWS service boundary, configuration behavior, or code-review decision.             |
| Exam-style fidelity   | The prompt resembles Developer Associate troubleshooting, deployment, security, or development workflow reasoning. |
| Distractor quality    | If options are present, wrong answers are plausible artifact-review misconceptions.                                |
| Technical correctness | The artifact, expected issue, and reference fix are accurate.                                                      |
| Source safety         | The artifact is self-authored and does not copy restricted source text or real secrets.                            |

## Source And Calibration Policy

Allowed sources:

- AWS service documentation.
- AWS CloudFormation and SAM public documentation.
- AWS SDK public documentation and public migration notes.
- AWS Certified Developer Associate public exam guide objectives.
- AWS official sample questions or practice previews only when used as summarized calibration metadata and allowed by terms.
- Self-authored scenarios based on public AWS behavior.

Do not use real exam dumps, copied paid practice-bank content, restricted Skill Builder question text, private customer code, or real incident artifacts.

## Release Metrics

Add Phase 2 metrics when implementation begins:

- Total artifact-review question count.
- Count by `artifact_type`.
- Count by Developer Associate domain and task statement.
- Average artifact question fidelity.
- Human-review AWS-valid pass rate.
- Human-review exam-valid pass rate.
- Hard rejection counts by reason.
- Artifact source-safety rejection count.

Release notes for `v2.4.1` should state whether the release includes design only, generated artifact questions, runtime filtering, or learner-facing UI changes.

## Implementation Sequence

1. Add and review Codex skills for artifact-review question design.
2. Approve this design document.
3. Add source metadata examples for IAM, Lambda, SDK, and CloudFormation/SAM under ignored local data paths.
4. Extend generated question artifacts with the artifact-review contract.
5. Add validation tests for required artifact fields and data separation.
6. Add app filtering and rendering for `artifact_review` only after artifact fields are stable.
7. Add release metrics and release-note rendering.

## Acceptance Criteria For Phase 2 Design

- A dedicated Codex skill exists for AWS code and configuration artifact-review questions.
- The design explains IAM policy, Lambda code, SDK usage, and CloudFormation/SAM question families.
- The artifact-review contract keeps learner-answer grading separate from question-fidelity review.
- The source policy prevents restricted text, real secrets, and real customer artifacts.
- Future code changes have an implementation sequence and release metrics to follow.
