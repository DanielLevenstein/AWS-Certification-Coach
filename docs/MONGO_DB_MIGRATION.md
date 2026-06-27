# MongoDB Migration Design

## Purpose

This document proposes a MongoDB schema for migrating the current JSON-backed
knowledge base and question template data into database collections.

Current source files:

- `config/knowledge_base/knowledge_base.json`
- `config/question_templates/question_template.json`
- `config/schema_version.json`

MongoDB uses collections rather than relational tables. In this document,
"table" refers to the proposed MongoDB collection that replaces a root-level
JSON field.

The current JSON source schema version is `3`, matching the version constants
in `config/schema_version.json`. The MongoDB migration should introduce target
schema version `4.1` so the database design can iterate independently from the
current JSON-backed schema.

## Source Root Fields

### Knowledge Base

Root-level fields in `knowledge_base.json`:

| Root field | Current type | Proposed collection |
| --- | --- | --- |
| `schema_version` | number | `content_manifests` |
| `description` | string | `content_manifests` |
| `syntax_aliases` | array | `syntax_aliases` |
| `services` | array | `services` |
| `concepts` | array | `concepts` |
| `common_misconceptions` | array | `misconceptions` |
| `must_not_claim` | array | `misconceptions` |

### Question Template

Root-level fields in `question_template.json`:

| Root field | Current type | Proposed collection |
| --- | --- | --- |
| `schema_version` | number | `content_manifests` |
| `description` | string | `content_manifests` |
| `templates` | array | `question_templates` |
| `service_scenarios` | array | `service_scenarios` |
| `developer_question_scenarios` | array | `developer_question_scenarios` |

## Proposed Collections

### `content_manifests`

Stores metadata for imported source documents. This preserves root-level scalar
fields that describe an entire source file rather than an individual record.

Suggested document shape:

```json
{
  "_id": "knowledge_base",
  "source": "knowledge_base",
  "source_path": "config/knowledge_base/knowledge_base.json",
  "schema_version": 4.1,
  "source_schema_version": 3,
  "description": "Source file description",
  "imported_at": "2026-06-27T00:00:00Z"
}
```

Indexes:

- Unique index on `source`
- Optional index on `schema_version`

Notes:

- Add one document for `knowledge_base`.
- Add one document for `question_template`.
- Set migrated `schema_version` to `4.1`.
- Preserve the source JSON version as `source_schema_version: 3`, matching
  `KNOWLEDGE_BASE_VERSION`, `QUESTION_SCHEMA_VERSION`, and
  `USER_FEEDBACK_VERSION` in `config/schema_version.json`.
- Keep `schema_version` here unless the application needs per-record schema
  versioning later.

### `syntax_aliases`

Derived from `knowledge_base.syntax_aliases`.

Current fields:

- `alias`
- `canonical`

Suggested document shape:

```json
{
  "_id": "api gateway",
  "alias": "api gateway",
  "canonical": "apigateway",
  "source": "knowledge_base",
  "source_order": 0
}
```

Indexes:

- Unique index on `alias`
- Index on `canonical`

Notes:

- Use normalized lowercase `alias` as `_id` if aliases are guaranteed unique.
- Preserve `source_order` to support deterministic JSON export.

### `services`

Derived from `knowledge_base.services`.

Current fields:

- `id`
- `name`
- `tokens`
- `aliases`
- `source_url`
- `description`

Suggested document shape:

```json
{
  "_id": "amazon-athena",
  "id": "amazon-athena",
  "name": "Amazon Athena",
  "tokens": ["athena"],
  "aliases": ["athena", "amazon athena"],
  "source_url": "https://docs.aws.amazon.com/athena/latest/ug/what-is.html",
  "description": "Amazon Athena is an AWS service or feature used by generated certification-coach scenarios.",
  "source": "knowledge_base",
  "source_order": 0
}
```

Indexes:

- Unique index on `id`
- Text or multikey indexes on `name`, `tokens`, and `aliases`
- Optional index on `source_url`

Notes:

- Use `id` as `_id`.
- `tokens` and `aliases` should remain embedded arrays because they are small,
  owned by the service record, and commonly read with the service.

### `concepts`

Derived from `knowledge_base.concepts`.

Current fields:

- `id`
- `name`
- `aliases`
- `service_ids`
- `description`

Suggested document shape:

```json
{
  "_id": "accounts",
  "id": "accounts",
  "name": "accounts",
  "aliases": [],
  "service_ids": ["service-control-policies"],
  "description": "accounts is a reusable concept for scenarios about Service Control Policies.",
  "source": "knowledge_base",
  "source_order": 0
}
```

Indexes:

- Unique index on `id`
- Multikey index on `service_ids`
- Text or multikey indexes on `name` and `aliases`

Notes:

- Use `id` as `_id`.
- Keep `service_ids` embedded as references to `services._id`.
- Do not duplicate full service records inside concepts.

### `misconceptions`

Derived from `knowledge_base.common_misconceptions` and
`knowledge_base.must_not_claim`.

Current fields:

- `id`
- `key_concepts`
- `common_misconceptions`
- `acceptable_answers`
- `must_not_claim`
- `source_url`
- `do_not_claim_explanation`

Suggested document shape:

```json
{
  "_id": "iam",
  "id": "iam",
  "key_concepts": ["IAM", "temporary credentials", "least privilege", "trusted entities"],
  "common_misconceptions": [
    "IAM user access keys is the best fit for this requirement."
  ],
  "acceptable_answers": ["Use IAM roles.", "IAM roles"],
  "must_not_claim": [
    "IAM user access keys satisfies the scenario better than IAM roles."
  ],
  "source_url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html",
  "do_not_claim_explanation": [
    "IAM roles is a better option for this scenario. IAM user access keys does not satisfy the same requirement."
  ],
  "source": "knowledge_base",
  "source_order": 0
}
```

Indexes:

- Unique index on `id`
- Multikey index on `key_concepts`
- Optional text index across `common_misconceptions`, `acceptable_answers`,
  `must_not_claim`, and `do_not_claim_explanation`

Notes:

- Use `id` as `_id` if each misconception remains unique.
- Keep the arrays embedded because they are profile-owned rubric data.
- The current `common_misconceptions` and `must_not_claim` arrays are identical,
  so the first implementation should import them once into this root-level
  collection instead of maintaining two duplicated collections.
- The import should verify that both source arrays remain identical. If they
  diverge in the future, stop the import and require an explicit schema decision
  rather than silently merging different records.

### `question_templates`

Derived from `question_template.templates`.

Current fields:

- `id`
- `question_type`
- `certifications`
- `prompt_variants`
- `question_pattern`
- `reference_answer_pattern`
- `option_pattern`
- `option_order`
- `selection_rule`
- `distractor_recipes`
- `required_slots`
- `rubric_merge`
- `composition_rules`

Suggested document shape:

```json
{
  "_id": "service-selection-freeform",
  "id": "service-selection-freeform",
  "question_type": "service_selection",
  "certifications": [
    "Cloud Practitioner",
    "Solutions Architect Associate",
    "AWS Certified Developer"
  ],
  "prompt_variants": [
    "A team is reviewing an AWS design and needs a solution that can {purpose}. Which AWS service or feature should they choose?"
  ],
  "question_pattern": "Explain which AWS service or feature should be used to {purpose}.",
  "reference_answer_pattern": "Use {service_name} to {purpose}.",
  "option_pattern": "Use {service_name}.",
  "option_order": ["correct", "distractor", "distractor", "distractor"],
  "selection_rule": {
    "correct_option_ids": ["A"],
    "instruction": "Choose the single best AWS service or feature."
  },
  "distractor_recipes": [
    {
      "id": "adjacent-service",
      "description": "Use a plausible but incorrect service or feature from the service scenario."
    }
  ],
  "required_slots": ["service_id", "service_name", "purpose", "concepts", "distractors"],
  "rubric_merge": {
    "key_concepts": "scenario_concepts"
  },
  "composition_rules": {
    "source_url": "knowledge_service_source_url"
  },
  "source": "question_template",
  "source_order": 0
}
```

Indexes:

- Unique index on `id`
- Index on `question_type`
- Multikey index on `certifications`
- Multikey index on `required_slots`

Notes:

- Use `id` as `_id`.
- Keep template rules embedded because they are edited and loaded as one unit.
- Insert one MongoDB document per item in `question_template.templates`; do not
  store the entire `question_template.json` file as a single
  `question_templates` document. The current source file has one template, so
  the initial collection count is one, but the collection shape supports
  multiple templates directly.

### `service_scenarios`

Derived from `question_template.service_scenarios`.

Current fields:

- `id`
- `service_id`
- `domain`
- `certification`
- `exam_code`
- `difficulty`
- `purpose`
- `key_concepts`
- `distractors`

Suggested document shape:

```json
{
  "_id": "iam-roles",
  "id": "iam-roles",
  "service_id": "iam-roles",
  "domain": "Security",
  "certification": "Cloud Practitioner",
  "exam_code": "CLF-C02",
  "difficulty": "Easy",
  "purpose": "grant temporary credentials to trusted AWS resources without storing long-term access keys",
  "key_concepts": ["IAM", "temporary credentials", "least privilege", "trusted entities"],
  "distractors": ["IAM user access keys", "AWS Shield Advanced", "hard-coded credentials"],
  "source": "question_template",
  "source_order": 0
}
```

Indexes:

- Unique index on `id`
- Index on `service_id`
- Index on `domain`
- Compound index on `certification`, `exam_code`, and `difficulty`
- Multikey index on `key_concepts`

Notes:

- Use `id` as `_id`.
- Treat `service_id` as a reference to `services._id` where values overlap.
- Keep `distractors` embedded because they are scenario-owned generation inputs.
- Keep this separate from `developer_question_scenarios`; the two scenario
  types do not share the same schema.

### `developer_question_scenarios`

Derived from `question_template.developer_question_scenarios`.

Current fields:

- `id`
- `generated_question`
- `correct_option`
- `reference_answer`
- `distractors`

Suggested document shape:

```json
{
  "_id": "dva-lambda-sqs-dlq",
  "id": "dva-lambda-sqs-dlq",
  "generated_question": "A Lambda function processes messages from an SQS queue. A few messages repeatedly fail and delay later processing. Which configuration should the developer use to isolate failed messages while allowing successful messages to continue?",
  "correct_option": "Configure an SQS dead-letter queue.",
  "reference_answer": "Configure the Lambda event source mapping with an SQS dead-letter queue so failed messages can be isolated after retries.",
  "distractors": [
    "Configure an SNS topic subscription.",
    "Add a CloudWatch alarm only.",
    "Use Lambda provisioned concurrency."
  ]
}
```

Indexes:

- Unique index on `id`

Notes:

- Use `id` as `_id`.
- Insert one MongoDB document per item in
  `question_template.developer_question_scenarios`.
- Store this as a separate collection because these records are pre-authored
  developer question scenarios. They do not include the service-selection
  metadata fields used by `service_scenarios`, such as `service_id`, `domain`,
  `certification`, `exam_code`, `difficulty`, `purpose`, or `key_concepts`.
- Keep `distractors` embedded because they are owned by the scenario.

## Supporting Data Collections

The first migration should also account for feedback and structured-answer
training data currently stored under `config/data`. These files are not part of
the knowledge base or question-template root schema, but they are closely tied
to evaluation, calibration, and future model quality workflows.

### `generated_questions`

Derived from the generated app question pipeline:

- `scripts/generate_app_question_artifacts.py`
- `scripts/generate_developer_question_artifacts.py`
- `data/original_questions/developer_associate_sources.json`

This collection stores app-facing generated questions. It is intentionally
separate from `question_templates`, `service_scenarios`, and
`developer_question_scenarios`.

Rationale:

- `question_templates` contains reusable generation rules.
- `service_scenarios` and `developer_question_scenarios` contain source inputs
  for generation.
- `generated_questions` contains the rendered question bank consumed by the app.

Current generated-question fields include:

- `schema_version`
- `certification`
- `exam_code`
- `domain`
- `difficulty`
- `question_type`
- `question`
- `reference_answer`
- `key_concepts`
- `required_concepts`
- `bonus_concepts`
- `common_misconceptions`
- `acceptable_answers`
- `must_not_claim`
- `do_not_claim_explanation`
- `original_multiple_choice`
- optional Developer metadata such as `source_examples`, `exam_calibration`,
  `question_fidelity`, and artifact-review fields

Indexes:

- Index on `certification`
- Index on `domain`
- Index on `difficulty`
- Index on `exam_code`
- Index on `question_type`

Management guidance:

- Recreate this collection from the raw JSON/template sources during database
  rebuilds.
- Do not merge generated question documents into `question_templates`; generated
  rows are runtime content, while templates are source rules.
- Keep generated question documents exportable to the current
  `data/questions/sample_questions.json` shape for compatibility checks.

### `user_feedback`

Derived from versioned user feedback files:

- `config/data/user_feedback.v2.json`
- `config/data/user_feedback.v3.json`

Current `user_feedback.v3.json` fields:

- `schema_version`
- `question`
- `exam_code`
- `reference_answer`
- `original_multiple_choice`
- `answer_given`
- `correct_rating`
- `rating_given`
- `feedback_text`
- `key_concepts`
- `acceptable_answers`
- `common_misconceptions`
- `must_not_claim`
- `do_not_claim_explanation`
- `source_url`

Suggested document shape:

```json
{
  "_id": "generated-or-imported-feedback-id",
  "schema_version": 3,
  "question": "A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?",
  "exam_code": "DVA-C02",
  "reference_answer": "Use an API Gateway Lambda authorizer to run custom authorization logic before invoking the backend Lambda integration.",
  "original_multiple_choice": {
    "question": "A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?",
    "options": [],
    "correct_option_ids": ["A"],
    "explanation": "Use an API Gateway Lambda authorizer to run custom authorization logic before invoking the backend Lambda integration."
  },
  "answer_given": "Learner answer text",
  "correct_rating": "D",
  "rating_given": "A",
  "feedback_text": "",
  "key_concepts": [],
  "acceptable_answers": [],
  "common_misconceptions": [],
  "must_not_claim": [],
  "do_not_claim_explanation": [],
  "source_url": "https://docs.aws.amazon.com/example",
  "source": "user_feedback",
  "source_file": "config/data/user_feedback.v3.json",
  "source_order": 0,
  "created_at": "2026-06-27T00:00:00Z"
}
```

Indexes:

- Index on `schema_version`
- Index on `exam_code`
- Compound index on `correct_rating` and `rating_given`
- Optional text index on `question`, `answer_given`, and `feedback_text`

Management guidance:

- Treat `user_feedback.v3.json` as the canonical seed source for the initial
  import because it matches `USER_FEEDBACK_VERSION: 3`.
- Keep older versioned files such as `user_feedback.v2.json` as historical
  migration inputs only when backfilling or comparing schema changes.
- Generate stable `_id` values during import from a deterministic hash of
  `schema_version`, `question`, `answer_given`, `correct_rating`, and
  `rating_given` unless a future feedback capture flow provides explicit IDs.
- Preserve `original_multiple_choice` as an embedded document to keep the
  learner response attached to the exact question context that produced it.
- Do not merge feedback records into the core question template collections;
  feedback is observed evaluation data, not template source data.

### `structured_answer_training_examples`

Derived from:

- `config/data/structured_answer_training_data.json`

Current fields:

- `certification`
- `exam_code`
- `domain`
- `difficulty`
- `question`
- `reference_answer`
- `key_concepts`
- `required_concepts`
- `acceptable_answers`
- `common_misconceptions`
- `must_not_claim`
- `original_multiple_choice`
- `partial_answers`
- `do_not_claim_explanation`

Suggested document shape:

```json
{
  "_id": "generated-or-imported-training-example-id",
  "certification": "AWS Certified Developer",
  "exam_code": "DVA-C02",
  "domain": "Deployment",
  "difficulty": "Medium",
  "question": "A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?",
  "reference_answer": "Define the install, build, and test command phases in an AWS CodeBuild buildspec file for the managed build project.",
  "key_concepts": ["CodeBuild buildspec", "build phases", "test commands"],
  "required_concepts": ["CodeBuild buildspec"],
  "acceptable_answers": ["Use a CodeBuild buildspec file."],
  "common_misconceptions": ["CodeDeploy AppSpec"],
  "must_not_claim": ["CodeDeploy AppSpec is the build command file."],
  "original_multiple_choice": {
    "question": "Where should a developer define repeatable build commands?",
    "options": [],
    "correct_option_ids": ["A"],
    "explanation": "Define the install, build, and test command phases in an AWS CodeBuild buildspec file."
  },
  "partial_answers": [
    {
      "answer": "AWS Code Build",
      "rating": 0.85,
      "source": "structured_answer_test_case"
    }
  ],
  "do_not_claim_explanation": [],
  "source": "structured_answer_training_data",
  "source_file": "config/data/structured_answer_training_data.json",
  "source_order": 0
}
```

Indexes:

- Compound index on `certification`, `exam_code`, `domain`, and `difficulty`
- Multikey index on `key_concepts`
- Multikey index on `required_concepts`
- Optional text index on `question`, `reference_answer`, and
  `partial_answers.answer`

Management guidance:

- Store these records in a separate collection from `user_feedback` because they
  are curated training and evaluation examples, not live learner feedback.
- Do not add `schema_version` to individual records before implementation,
  because the current JSON file is a root array without an explicit record-level
  schema field. Track migrated version `4.1` and source version `3` through
  import metadata or `content_manifests` instead.
- Preserve `partial_answers` as embedded examples because they are tightly
  coupled to the reference answer and rubric fields for the same question.
- Keep deterministic `source_order` so the MongoDB collection can be exported
  back to the same JSON order for regression tests.
- Do not store generated model outputs or metrics here; generated artifacts
  should remain outside committed `data` and `metrics` paths unless explicitly
  promoted to curated training examples.

## Relationships

Recommended references:

| From collection | Field | To collection | Notes |
| --- | --- | --- | --- |
| `concepts` | `service_ids[]` | `services._id` | Many concepts can reference many services. |
| `service_scenarios` | `service_id` | `services._id` | Some scenario service IDs may represent service features; validate during import. |
| `misconceptions` | `id` | `services._id` or logical misconception ID | Do not enforce until IDs are audited. |
| `question_templates` | `required_slots[]` | application slot names | Keep as embedded strings. |
| `developer_question_scenarios` | `id` | developer scenario ID | Separate scenario source; no service reference is implied. |

MongoDB does not enforce these relationships by default. The application import
and validation layer should check referential integrity.

## Migration Approach

1. Create collections and indexes.
2. Import root scalar metadata into `content_manifests`.
3. Import each root array item as its own document in the corresponding
   collection. For `question_template.templates`, this means one document per
   question template. For `question_template.developer_question_scenarios`,
   this means one document per developer scenario. For
   `common_misconceptions` and `must_not_claim`, first verify the arrays are
   identical, then import them once into `misconceptions`.
4. Import `user_feedback.v3.json` into `user_feedback`.
5. Import `structured_answer_training_data.json` into
   `structured_answer_training_examples`.
6. Preserve source payload fields as-is. Store import metadata such as
   `schema_version: 4.1`, `source_schema_version: 3`, `source`, and
   `source_order` only as repository metadata where needed, not as a required
   schema change to every source record.
7. Validate uniqueness for natural keys such as `id` and `alias`.
8. Validate references from `concepts.service_ids` and
   `service_scenarios.service_id`.
9. Add a deterministic export path that can regenerate the current JSON files
   from MongoDB for compatibility testing.
10. Run existing knowledge and question-generation tests against the exported
   JSON, then move runtime reads to MongoDB behind a repository interface.

## Recreate Helper

The initial implementation includes `recreate_database.sh`, which rebuilds a
MongoDB database from the raw JSON files listed in this design.

Default behavior:

- Uses `.venv/bin/python`, creating `.venv` first if needed.
- Installs `requirements.txt` before running the migration script.
- Runs `scripts/recreate_mongo_database.py --drop-existing --yes`.
- Uses `MONGODB_URI` when set, otherwise `mongodb://localhost:27017`.
- Uses `AWS_COACH_MONGODB_DATABASE` when set, otherwise
  `aws_certification_coach`.

Useful commands:

```sh
./recreate_database.sh --dry-run
MONGODB_URI="mongodb://localhost:27017" AWS_COACH_MONGODB_DATABASE="aws_certification_coach" ./recreate_database.sh
```

## Compatibility Requirements

- Preserve all current field names during the first migration.
- Preserve array ordering where application behavior or generated output may
  depend on it.
- Do not drop or rename root-level fields until all JSON consumers have moved to
  the MongoDB-backed repository.
- Avoid schema changes before implementation, except for combining
  `common_misconceptions` and `must_not_claim` into the single root-level
  `misconceptions` collection because those arrays are currently identical.
- Keep `service_scenarios` and `developer_question_scenarios` separate because
  they have different field sets and generation roles.
- Keep generated `data` and `metrics` artifacts out of the migration commit.

## Migration Decisions

### Combine Misconception Sources

Import `knowledge_base.common_misconceptions` and
`knowledge_base.must_not_claim` into a single root-level `misconceptions`
collection.

Rationale:

- The current arrays are identical.
- A single collection avoids duplicated data and duplicated indexes.
- The document shape remains unchanged; only the duplicated source arrays are
  consolidated at the collection boundary.

Implementation guidance:

- Validate source parity before import.
- Fail fast if the arrays diverge so implementation does not introduce an
  accidental schema change.
- Preserve the existing misconception document fields exactly.

### Allow Flexible `service_scenarios.service_id` References

Do not hard-restrict `service_scenarios.service_id` to `services._id` during the
first migration.

Rationale:

- Some scenario IDs may represent AWS service features or exam-specific
  concepts rather than top-level service records.
- A hard database constraint could block valid existing question scenarios.
- MongoDB does not enforce cross-collection references natively, so validation
  belongs in the import and application repository layer.

Implementation guidance:

- Validate and report whether each `service_scenarios.service_id` matches a
  `services._id`.
- Treat unmatched values as warnings during the initial migration, not import
  failures.
- Revisit strict enforcement after the scenario IDs are audited.

### Keep Semantic Retrieval in the Application Layer

Keep application-level semantic retrieval as the primary retrieval path for the
first migration.

Rationale:

- The project already depends on knowledge and semantic-evaluation workflows.
- MongoDB text indexes are useful for exact and keyword-style lookup, but they
  are not a replacement for semantic matching.
- Atlas Search may be useful later, but adopting it during the first migration
  would add infrastructure scope beyond moving JSON content into MongoDB.

Implementation guidance:

- Add basic indexes for exact lookup and filtering.
- Add optional MongoDB text indexes only for administrative search, debugging,
  or fallback keyword search.
- Keep semantic ranking, grading, and retrieval behavior controlled by the
  existing application code until a dedicated retrieval redesign is planned.

### Store Schema Version on Source Manifests First

Store migrated `schema_version: 4.1` and `source_schema_version: 3` in
`content_manifests` during the first migration. Do not duplicate version fields
onto imported documents that do not already carry a schema version.

Rationale:

- The current JSON files define schema version at the document level.
- Source-level versioning preserves the existing contract.
- Adding record-level version fields before implementation would be a schema
  change for files that do not currently include them.
- A `4.1` target version gives the MongoDB schema room for iterative migration
  updates without changing the current JSON source version constants first.

Future option:

- Add per-record `schema_version` only after implementation proves a need for
  partial migrations, mixed-version imports, or independently versioned record
  updates.
