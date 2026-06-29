"""Streamlit entry point for AWS Certification Coach."""

from __future__ import annotations

import hashlib
import html
import os
from difflib import SequenceMatcher
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

import streamlit as st

from aws_certification_coach.domain import MultipleChoiceQuestion, Question, QuestionFilter, MultipleChoiceOption
from aws_certification_coach.config import load_evaluator_config
from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.feedback import UserFeedbackRepository
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.questions.visibility import visible_questions
from aws_certification_coach.quiz.session import QuizSession
from aws_certification_coach.ratings import LETTER_RATINGS, score_to_letter

# TODO move user_feedback version to schema_version.json
QUESTIONS_PATH = ROOT_DIR / "data" / "questions" / "sample_questions.json"
USER_FEEDBACK_PATH = Path(
    os.environ.get(
        "USER_FEEDBACK_PATH",
        ROOT_DIR / "data" / "generated" / "user_feedback.v3.json",
    )
)

author = "Daniel Levenstein"
linked_in_url = "https://www.linkedin.com/in/daniel-aaron-levenstein/"
github_url="https://github.com/DanielLevenstein/AWS-Certification-Coach"


@st.cache_resource
def get_question_repository() -> JsonQuestionRepository:
    return JsonQuestionRepository(QUESTIONS_PATH)


@st.cache_resource
def get_evaluation_service() -> EvaluationService:
    return build_evaluation_service(load_evaluator_config())


@st.cache_resource
def get_feedback_repository() -> UserFeedbackRepository:
    return UserFeedbackRepository(USER_FEEDBACK_PATH)


def _selected_filter(questions: list[Question]) -> QuestionFilter:
    certification = st.sidebar.selectbox("Certification", ["All"] + _unique_sorted(q.certification for q in questions))
    domain = st.sidebar.selectbox("Domain", ["All"] + _unique_sorted(q.domain for q in questions))
    difficulty = st.sidebar.selectbox("Difficulty", ["All"] + _unique_sorted(q.difficulty for q in questions))
    question_category = st.sidebar.selectbox(
        "Question Category",
        ["All"] + _unique_sorted(q.question_category for q in questions),
    )
    return QuestionFilter(
        certification=None if certification == "All" else certification,
        domain=None if domain == "All" else domain,
        difficulty=None if difficulty == "All" else difficulty,
        question_category=None if question_category == "All" else question_category,
    )


def _reset_session(questions) -> None:
    st.session_state.quiz_session = QuizSession(questions)
    st.session_state.last_result = None
    st.session_state.show_answers = False
    st.session_state.feedback_submitted = set()


def _visible_questions(questions: list[Question]) -> list[Question]:
    return visible_questions(questions)


def _filter_questions(questions: list[Question], filters: QuestionFilter) -> list[Question]:
    if filters.certification:
        questions = [q for q in questions if q.certification == filters.certification]
    if filters.domain:
        questions = [q for q in questions if q.domain == filters.domain]
    if filters.difficulty:
        questions = [q for q in questions if q.difficulty == filters.difficulty]
    if filters.question_category:
        questions = [q for q in questions if q.question_category == filters.question_category]
    return questions


def _unique_sorted(values) -> list[str]:
    return sorted(set(values))


def main() -> None:
    st.title("🎓 AWS Certification Coach")
    repository = get_question_repository()
    available_questions = _visible_questions(repository.all())
    filters = _selected_filter(available_questions)
    questions = _filter_questions(available_questions, filters)

    if "quiz_session" not in st.session_state:
        _reset_session(questions)

    _render_feedback_download()

    if st.sidebar.button("Next Question"):
        _reset_session(questions)

    session: QuizSession = st.session_state.quiz_session
    if session.is_complete:
        st.success("Session complete.")
        st.write(f"Answered questions: {len(session.completed)}")
        st.write(f"Average score: {session.average_score:.0f}%")
        return

    question = session.current_question()
    if question is None:
        st.warning("No questions match the selected filters.")
        return

    result = st.session_state.get("last_result")
    st.caption(f"{question.certification} | {question.domain} | {question.difficulty}")
    st.subheader(question.question)
    _render_artifact(question, show_corrected=bool(result))

    user_answer = st.text_area("Your answer", key=f"answer_text_{session.current_index}", height=160)
    evaluate_column, show_answers_column, next_column = st.columns([1, 1, 1])
    with evaluate_column:
        evaluate_clicked = st.button("Evaluate Answer")
    with show_answers_column:
        show_answers_clicked = st.button("Show Options")
    with next_column:
        next_clicked = st.button("Next Question", disabled=not st.session_state.get("last_result"))

    if show_answers_clicked:
        st.session_state.show_answers = True
        st.rerun()

    if evaluate_clicked:
        result = get_evaluation_service().evaluate(question, user_answer)
        session.record_answer(question, user_answer, result)
        st.session_state.last_result = result
        st.session_state.show_answers = False
        st.rerun()

    if next_clicked:
        session.advance()
        st.session_state.last_result = None
        st.session_state.show_answers = False
        st.rerun()

    _render_contact_info_link()
    if st.session_state.get("show_answers") and not result:
        _render_original_multiple_choice(question.original_multiple_choice, highlight_correct=False)
    if result:
        feedback_column, source_column = st.columns([3, 2])
        with feedback_column:
            _render_score(result.score)
            _render_answer_feedback(result.score, result.feedback, result.suggested_improvements)
            st.markdown("### Detailed Answer")
            st.write(result.detailed_answer)
            _render_source_documentation(question.original_multiple_choice)
            _render_feedback_link(question, user_answer, result.score)
        with source_column:
            _render_original_multiple_choice(question.original_multiple_choice, highlight_correct=True)
            _render_multiple_choice_source_documentation(question.original_multiple_choice)


def _render_score(score: int) -> None:
    grade, color = _score_grade(score)
    st.markdown(
        f"""
        <div aria-label="Score: {grade}" style="
            border-left: 0.35rem solid {color};
            border-radius: 0.45rem;
            background: color-mix(in srgb, {color} 12%, transparent);
            padding: 0.7rem 0.9rem;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 0.85rem; font-weight: 600;">Score</div>
            <div style="display: flex; align-items: baseline; gap: 0.65rem;">
                <span style="color: {color}; font-size: 1.1rem; font-weight: 700;">Grade {grade}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _score_grade(score: int) -> tuple[str, str]:
    grade = score_to_letter(score)
    colors = {
        "A": "#3ddc84",
        "B": "#62a8ff",
        "C": "#f2cc60",
        "D": "#ff9f43",
        "F": "#ff6b6b",
    }
    return grade, colors[grade]

def _render_feedback_link(question: Question, user_answer: str, score: int) -> None:
    with st.expander("Submit feedback", expanded=False):
        _render_feedback_form(question, user_answer, score)


def _render_answer_feedback(score: int, feedback: str, suggest_improvements: list[str]) -> None:
    if score_to_letter(score) == "A":
        return
    if feedback:
        st.info(feedback)
    elif suggest_improvements:
            st.info(f"Here are some suggestions for improving your answer:")
            output = ""
            for suggestion in suggest_improvements:
                output+= f"- {suggestion}\n"
            st.write(output)

def _render_contact_info_link() -> None:
    st.markdown(f"Author: [{author}]({linked_in_url}) — GitHub: [AWS-Certification-Coach]({github_url})")

def _render_feedback_form(question: Question, user_answer: str, score: int) -> None:
    submitted = st.session_state.setdefault("feedback_submitted", set())
    question_key = _question_key(question)
    if question_key in submitted:
        st.success("Thanks. Your grade correction was saved for future training.")
        return

    rating_given = score_to_letter(score)
    st.caption("Tell us if this answer should have received a different grade.")
    correct_rating = st.selectbox(
        "What grade should this answer receive?",
        LETTER_RATINGS,
        index=LETTER_RATINGS.index(rating_given),
        key=f"feedback_rating_{question_key}",
    )
    feedback_text = st.text_area(
        "What should the evaluator consider?",
        key=f"feedback_text_{question_key}",
        height=100,
        placeholder="Optional context about missing concepts, expected credit, or grading issues.",
    )
    if st.button("Submit Feedback", key=f"submit_feedback_{question_key}"):
        get_feedback_repository().submit(
            question=question,
            answer_given=user_answer,
            rating_given=rating_given,
            correct_rating=correct_rating,
            feedback_text=feedback_text,
        )
        submitted.add(question_key)
        st.success("Thanks. Your grade correction was saved for future training.")


def _render_feedback_download() -> None:
    st.sidebar.download_button(
        "Download feedback",
        data=get_feedback_repository().export_json(),
        file_name=USER_FEEDBACK_PATH.name,
        mime="application/json",
    )


def _question_key(question: Question) -> str:
    original = question.original_multiple_choice
    raw_key = "\n".join(
        [
            question.certification,
            question.domain,
            question.difficulty,
            question.question,
            question.reference_answer,
            original.question if original else "",
        ]
    )
    return hashlib.sha1(raw_key.encode("utf-8")).hexdigest()[:16]


def _render_source_documentation(original: MultipleChoiceQuestion | None) -> None:
    if original is None or not original.source_url:
        return
    st.markdown("### Source Documentation")
    st.markdown(f"[{original.source_name or 'AWS Documentation'}]({original.source_url})")


def _render_artifact(question: Question, *, show_corrected: bool = False) -> None:
    if question.question_type != "artifact_review" or not question.artifact_body:
        return
    caption_parts = [part for part in [question.artifact_type, question.artifact_language] if part]
    if caption_parts:
        st.caption(" | ".join(caption_parts))
    if show_corrected:
        _render_artifact_block(
            "Original Config",
            question.artifact_body,
            question.artifact_language,
            context=question.artifact_context,
            expanded=False,
        )
    if show_corrected and question.artifact_corrected:
        _render_artifact_block(
            "Corrected Config",
            question.artifact_corrected,
            question.artifact_language,
            expanded=True,
            original_body=question.artifact_body,
        )
        return
    if show_corrected:
        return
    _render_artifact_block(
        "Original Config",
        question.artifact_body,
        question.artifact_language,
        context=question.artifact_context,
        expanded=True,
    )


def _render_artifact_block(
    label: str,
    artifact_body: str,
    artifact_language: str = "",
    *,
    context: str = "",
    expanded: bool = False,
    original_body: str = "",
) -> None:
    if not artifact_body:
        return
    with st.expander(label, expanded=expanded):
        if artifact_language:
            st.caption(artifact_language)
        if context:
            st.write(context)
        if original_body:
            _render_highlighted_code(artifact_body, original_body)
            return
        st.code(artifact_body, language=_streamlit_code_language(artifact_language))


def _render_highlighted_code(corrected_body: str, original_body: str) -> None:
    changed_lines = _changed_corrected_line_indexes(original_body, corrected_body)
    rendered_lines = []
    for index, line in enumerate(corrected_body.splitlines() or [""]):
        escaped_line = html.escape(line) or " "
        if index in changed_lines:
            rendered_lines.append(f'<span class="corrected-code-line">{escaped_line}</span>')
        else:
            rendered_lines.append(escaped_line)
    rendered_code = "\n".join(rendered_lines)
    st.markdown(
        f"""
        <style>
        .corrected-code-block {{
            background: #0e1117;
            border-radius: 0.45rem;
            color: #fafafa;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
            font-size: 0.875rem;
            line-height: 1.45;
            margin: 0;
            overflow-x: auto;
            padding: 1rem;
            white-space: pre;
        }}
        .corrected-code-line {{
            background: rgba(61, 220, 132, 0.24);
            border-left: 0.2rem solid #3ddc84;
            display: block;
            margin-left: -0.45rem;
            padding-left: 0.25rem;
        }}
        </style>
        <pre class="corrected-code-block"><code>{rendered_code}</code></pre>
        """,
        unsafe_allow_html=True,
    )


def _changed_corrected_line_indexes(original_body: str, corrected_body: str) -> set[int]:
    changed_lines: set[int] = set()
    matcher = SequenceMatcher(a=original_body.splitlines(), b=corrected_body.splitlines())
    for tag, _original_start, _original_end, corrected_start, corrected_end in matcher.get_opcodes():
        if tag != "equal":
            changed_lines.update(range(corrected_start, corrected_end))
    return changed_lines


def _streamlit_code_language(artifact_language: str) -> str | None:
    language = artifact_language.strip().lower()
    aliases = {
        "cloudformation": "yaml",
        "sam": "yaml",
        "iam-json": "json",
        "json": "json",
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "yaml": "yaml",
    }
    return aliases.get(language)


def _render_original_multiple_choice(
    original: MultipleChoiceQuestion | None,
    *,
    highlight_correct: bool = True,
) -> None:
    st.markdown("### Multiple-choice Answers")
    if original is None:
        st.write("No source multiple-choice item is attached.")
        return
    correct_ids = set(original.correct_option_ids)
    for option in original.options:
        option_text = f"{option.option_id}. {option.text}"
        if highlight_correct and option.option_id in correct_ids:
            st.success(option_text)
        else:
            st.write(option_text)
        _render_artifact_block(
            f"Option {option.option_id} Artifact",
            option.artifact_body,
            option.artifact_language,
            context=option.artifact_context,
            expanded=False,
        )


def _render_multiple_choice_source_documentation(original: MultipleChoiceQuestion) -> None:
    options_with_sources = [option for option in original.options if option.source_url]
    if not options_with_sources:
        if original.source_url:
            st.markdown("### Documentation")
            st.markdown(f"- [{original.source_name or 'AWS Documentation'}]({original.source_url})")
        return
    st.markdown("### Documentation")
    seen_urls: set[str] = set()
    documentation_links = ""
    source_label_counts = _source_label_counts(options_with_sources)
    for option in original.options:
        if not option.source_url or option.source_url in seen_urls:
            continue
        seen_urls.add(option.source_url)
        documentation_links += f"- [{_source_label(option, source_label_counts)}]({option.source_url})\n"
    st.markdown(documentation_links )


def _source_label_counts(options: list[MultipleChoiceOption]) -> dict[str, int]:
    labels: dict[str, int] = {}
    for option in options:
        label = option.metadata.get("service_name", "").strip()
        if not label:
            continue
        labels[label] = labels.get(label, 0) + 1
    return labels


def _source_label(option: MultipleChoiceOption, source_label_counts: dict[str, int] | None = None) -> str:
    service_name = option.metadata.get("service_name", "").strip()
    if service_name and (source_label_counts or {}).get(service_name, 0) <= 1:
        return service_name
    return option.text.removeprefix("Use ").rstrip(".")

if __name__ == "__main__":
    main()
