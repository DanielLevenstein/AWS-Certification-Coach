AWS Certification Coach v2.0 - Initial Architecture

Project Goal

Develop a lightweight AI-powered AWS certification study platform that presents pre-generated certification questions, evaluates user responses using a Large Language Model (LLM), and provides personalized feedback.

Unlike Version 1.0, this architecture eliminates Retrieval-Augmented Generation (RAG), vector databases, and FAISS indexes in favor of a simpler question-and-evaluation workflow.

---

High-Level Architecture

┌─────────────────┐
│     Student     │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Streamlit Front │
│      End        │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Application API │
│  (Python Layer) │
└───────┬─────────┘
│
├─────────────► Question Repository
│                  (JSON/Database)
│
▼
┌─────────────────┐
│ Evaluation      │
│ Prompt Builder  │
└────────┬────────┘
│
▼
┌─────────────────┐
│ LLM Evaluation  │
│    Service      │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Feedback Engine │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Results Display │
└─────────────────┘

---

Major Components

1. User Interface Layer

Technology:

- Streamlit

Responsibilities:

- Present study questions
- Accept user responses
- Display scores
- Display feedback
- Track session progress

Inputs:

- Question data
- Evaluation results

Outputs:

- User answer submissions

---

2. Question Repository

Purpose:
Store all study content generated offline.

Initial Storage Option:

- JSON files

Future Storage Options:

- SQLite
- PostgreSQL
- DynamoDB

Question Structure:

{
"question_id": "AWS-001",
"certification": "Cloud Practitioner",
"domain": "Security",
"difficulty": "Easy",
"question": "...",
"reference_answer": "...",
"key_concepts": [
"IAM",
"Least Privilege",
"Roles"
]
}

Responsibilities:

- Retrieve questions
- Filter by domain
- Filter by difficulty
- Support randomized quizzes

---

3. Quiz Controller

Purpose:
Manage user study sessions.

Responsibilities:

- Select next question
- Track completed questions
- Track score history
- Manage quiz state

Future Enhancements:

- Adaptive difficulty
- Weak-area targeting
- Exam simulation mode

---

4. Evaluation Prompt Builder

Purpose:
Convert user responses into structured evaluation prompts.

Inputs:

- Question
- Reference answer
- Key concepts
- User response

Generated Prompt Example:

Evaluate the user's answer.

Question:
{question}

Reference Answer:
{reference_answer}

Key Concepts:
{key_concepts}

User Answer:
{user_answer}

Provide:

1. Accuracy Score (0-100)
2. Missing Concepts
3. Strengths
4. Suggested Improvements
5. Final Feedback

Return JSON only.

Responsibilities:

- Standardize prompts
- Ensure consistent scoring
- Reduce LLM hallucination

---

5. LLM Evaluation Service

Purpose:
Evaluate learner responses.

Candidate Models:

AWS:

- Amazon Bedrock

Alternative:

- OpenAI API

Input:

- Evaluation prompt

Output:

{
"score": 85,
"strengths": [...],
"missing_concepts": [...],
"feedback": "..."
}

Responsibilities:

- Semantic answer comparison
- Concept identification
- Feedback generation

---

6. Feedback Engine

Purpose:
Transform model output into user-friendly results.

Responsibilities:

- Format feedback
- Highlight missed concepts
- Present scores
- Generate improvement recommendations

Outputs:

Score: 85%

Strengths:

- Correctly identified IAM Roles

Areas to Improve:

- Mention temporary credentials

Recommendation:
Review IAM security best practices.

---

Offline Content Generation Pipeline

Purpose:
Generate question bank before deployment.

Workflow:

AWS Documentation
│
▼
Content Generation Script
│
▼
LLM Question Generation
│
▼
Quality Review
│
▼
JSON Question Bank

Outputs:

- Question files
- Answer keys
- Key concepts

Benefits:

- No vector database
- No embeddings
- No runtime retrieval

---

Deployment Architecture

Phase 1

User
│
▼
Streamlit App
│
▼
LLM API

Deployment Target:

- Render
  OR
- AWS EC2

Expected Benefits:

- Small Docker image
- Faster startup
- Lower memory usage

---

Future AWS Architecture

Phase 2

User
│
▼
CloudFront
│
▼
Application Load Balancer
│
▼
Containerized App
(ECS/Fargate)
│
├──► DynamoDB
│
└──► Amazon Bedrock

Optional Services:

- CloudWatch
- S3
- Cognito

---

MVP Deliverables

Version 2.0 MVP

Features:

- Question display
- User answer submission
- LLM evaluation
- Score generation
- Feedback generation
- Domain filtering
- Progress tracking

Out of Scope:

- Vector search
- FAISS
- Embeddings
- RAG
- Document ingestion
- User authentication
- Multi-user support

Success Criteria:

- Docker image under 1 GB
- Startup time under 30 seconds
- Response evaluation under 10 seconds
- Successful cloud deployment
- Minimum 100 AWS certification questions
