# Artifact Review Rubric

Use this reference to design and review AWS Certification Coach artifact-review questions.

## Shared Requirements

Every artifact-review question should have:

- One primary issue or decision point.
- A short, self-authored artifact snippet.
- Enough scenario context to choose the best remediation.
- Required concepts and common misconceptions.
- A reference answer that identifies the issue, explains impact, and recommends a safe AWS fix.
- Source metadata from allowed public documentation, exam objectives, or self-authored scenarios.

Reject questions that require AWS deployment, credentials, external network calls, or code execution to answer.

## IAM Policy Questions

Required metadata:

- `artifact_type`: `iam_policy`, `iam_trust_policy`, `iam_resource_policy`, or `iam_permission_boundary`
- `policy_scope`
- `action_scope`
- `resource_scope`
- `security_concepts`

Review for:

- Least privilege.
- Explicit deny precedence.
- Trust relationships and principals.
- Resource scoping and condition keys.
- Cross-account access and confused deputy risk.

Reject when the answer encourages broad wildcard permissions without justification, treats users and roles as interchangeable for temporary credentials, or ignores explicit deny behavior.

## Lambda Code Questions

Required metadata:

- `artifact_type`: `lambda_code`, `lambda_event_source`, or `lambda_configuration`
- `runtime`
- `trigger`
- `operational_concepts`
- `security_concepts`

Review for:

- Execution role versus invocation permission.
- Timeout, retry, concurrency, and idempotency behavior.
- Event-source failure handling.
- Environment variables and secrets handling.
- Logging and error handling.

Hard reject when the answer claims unlimited runtime, recommends hard-coded credentials, or depends on executing learner code.

## SDK Usage Questions

Required metadata:

- `artifact_type`: `sdk_usage`
- `language`
- `service`
- `sdk_concepts`
- `failure_mode`

Review for:

- Credential provider chain.
- Region configuration.
- Pagination and waiters.
- Retries, throttling, and idempotency.
- Exception handling and service-specific API selection.

Hard reject when the answer encourages static source-code credentials, assumes paginated APIs return all results in one call, or makes version-specific SDK claims without source metadata.

## CloudFormation And SAM Questions

Required metadata:

- `artifact_type`: `cloudformation_template` or `sam_template`
- `resource_types`
- `deployment_concepts`
- `serverless_concepts`
- `failure_mode`

Review for:

- Intrinsic functions, parameters, outputs, and conditions.
- Dependencies and references.
- Change sets, replacement behavior, rollback, and drift.
- SAM transforms behavior and policy templates.
- Unsafe handling of secrets in parameters or outputs.

Reject when the answer claims CloudFormation validates application code behavior, ignores replacement risk for replacement-required properties, or recommends outputting secrets in plaintext.

## Learner Grade Mapping

- `A`: Identifies the concrete artifact issue, explains impact, and recommends a safe AWS fix.
- `B`: Identifies the issue but gives limited reasoning or a less precise fix.
- `C`: Recognizes the relevant AWS area, or names the strongest plausible wrong service/feature from the source options, but misses the exact root cause or the best remediation.
- `D`: Mentions a related concept but fails the main artifact issue.
- `F`: Points to the wrong service category, contradicts the artifact, recommends unsafe behavior, or provides no meaningful AWS reasoning.

## Fidelity Evidence

Require these review notes when scoring generated artifact questions:

- `covered_concepts`
- `missing_concepts`
- `conflicting_concepts`
- `artifact_validity_notes`
- `matched_exam_style_pattern`
- `source_safety_notes`
- `review_recommendation`: `accept`, `revise`, or `reject`
