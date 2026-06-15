"""Streamlit entry point for AWS Certification Coach."""

from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

try:
    import streamlit as st
except Exception:  # pragma: no cover - fallback for test environments without streamlit
    class _StreamlitStub:
        def cache_resource(self, func=None, **kwargs):
            if func is None:
                def _decorator(f):
                    return f
                return _decorator
            return func

        # minimal placeholders used when tests import this module; runtime code
        # exercising Streamlit will need the real package.
        session_state = {}

        def sidebar(self):
            raise RuntimeError("streamlit not available")

    st = _StreamlitStub()

from aws_certification_coach.domain import MultipleChoiceQuestion, Question, QuestionFilter
from aws_certification_coach.config import load_evaluator_config
from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.feedback import UserFeedbackRepository
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.quiz.session import QuizSession
from aws_certification_coach.ratings import LETTER_RATINGS, score_to_letter


QUESTIONS_PATH = ROOT_DIR / "data" / "questions" / "sample_questions.json"
USER_FEEDBACK_PATH = ROOT_DIR / "data" / "generated" / "user_feedback.v1.json"


@st.cache_resource
def get_question_repository() -> JsonQuestionRepository:
    return JsonQuestionRepository(QUESTIONS_PATH)


@st.cache_resource
def get_evaluation_service() -> EvaluationService:
    return build_evaluation_service(load_evaluator_config())


@st.cache_resource
def get_feedback_repository() -> UserFeedbackRepository:
    return UserFeedbackRepository(USER_FEEDBACK_PATH)


def _selected_filter(repository: JsonQuestionRepository) -> QuestionFilter:
    certification = st.sidebar.selectbox("Certification", ["All"] + repository.available_certifications())
    domain = st.sidebar.selectbox("Domain", ["All"] + repository.available_domains())
    difficulty = st.sidebar.selectbox("Difficulty", ["All"] + repository.available_difficulties())
    return QuestionFilter(
        certification=None if certification == "All" else certification,
        domain=None if domain == "All" else domain,
        difficulty=None if difficulty == "All" else difficulty,
    )


def _reset_session(questions) -> None:
    st.session_state.quiz_session = QuizSession(questions)
    st.session_state.last_result = None
    st.session_state.feedback_submitted = set()


def main() -> None:
    st.title("🎓 AWS Certification Coach ")

    repository = get_question_repository()
    filters = _selected_filter(repository)
    questions = repository.filter_questions(filters)

    if "quiz_session" not in st.session_state:
        _reset_session(questions)

    if st.sidebar.button("Start / Reset"):
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

    st.caption(f"{question.certification} | {question.domain} | {question.difficulty}")
    st.subheader(question.original_multiple_choice.question if question.original_multiple_choice else question.question)

    user_answer = st.text_area("Your answer", key=f"answer_text_{session.current_index}", height=160)
    evaluate_column, next_column = st.columns([1, 1])
    with evaluate_column:
        evaluate_clicked = st.button("Evaluate Answer", disabled=not user_answer.strip())
    with next_column:
        next_clicked = st.button("Next Question", disabled=not st.session_state.get("last_result"))

    if evaluate_clicked:
        result = get_evaluation_service().evaluate(question, user_answer)
        session.record_answer(question, user_answer, result)
        st.session_state.last_result = result
        st.rerun()

    if next_clicked:
        session.advance()
        st.session_state.last_result = None
        st.rerun()

    result = st.session_state.get("last_result")
    if result:
        feedback_column, source_column = st.columns([3, 2])
        with feedback_column:
            _render_score(result.score)
            missing_concepts = result.missing_concepts
            results_feedback = result.feedback
            # Consider adding back missing concepts for answers with ratings below A.
            st.write("Scoring feedback")
            st.markdown(results_feedback)
            st.write("Detailed answer")
            st.write(result.detailed_answer)
            _render_source_documentation(question.original_multiple_choice)
            if os.environ.get("SHOW_FEEDBACK"):
                _render_feedback_link(question, user_answer, result.score)
        with source_column:
            _render_original_multiple_choice(question.original_multiple_choice)


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


def _render_feedback_form(question: Question, user_answer: str, score: int) -> None:
    submitted = st.session_state.setdefault("feedback_submitted", set())
    if question.question_id in submitted:
        st.success("Thanks. Your grade correction was saved for future training.")
        return

    rating_given = score_to_letter(score)
    st.caption("Tell us if this answer should have received a different grade.")
    correct_rating = st.selectbox(
        "What grade should this answer receive?",
        LETTER_RATINGS,
        index=LETTER_RATINGS.index(rating_given),
        key=f"feedback_rating_{question.question_id}",
    )
    if st.button("Submit Feedback", key=f"submit_feedback_{question.question_id}"):
        get_feedback_repository().submit(
            question=question,
            answer_given=user_answer,
            rating_given=rating_given,
           correct_rating=correct_rating,
        )
        submitted.add(question.question_id)
        st.success("Thanks. Your grade correction was saved for future training.")


def _render_source_documentation(original: MultipleChoiceQuestion | None) -> None:
    if original is None or not original.source_url:
        return
    st.write("Source documentation")
    st.markdown(f"[{original.source_name or 'AWS Documentation'}]({original.source_url})")


def _render_original_multiple_choice(original: MultipleChoiceQuestion | None) -> None:
    st.write("Source multiple-choice question")
    if original is None:
        st.write("No source multiple-choice item is attached.")
        return
    st.caption(original.source_name or "Source item")
    correct_ids = set(original.correct_option_ids)
    for option in original.options:
        option_text = f"{option.option_id}. {option.text}"
        if option.option_id in correct_ids:
            st.success(option_text)
        else:
            st.write(option_text)


if __name__ == "__main__":
    main()
