"""Streamlit entry point for AWS Certification Coach."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

import streamlit as st

from aws_certification_coach.domain import MultipleChoiceQuestion, QuestionFilter
from aws_certification_coach.config import load_evaluator_config
from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.quiz.session import QuizSession


QUESTIONS_PATH = ROOT_DIR / "data" / "questions" / "sample_questions.json"


@st.cache_resource
def get_question_repository() -> JsonQuestionRepository:
    return JsonQuestionRepository(QUESTIONS_PATH)


@st.cache_resource
def get_evaluation_service() -> EvaluationService:
    return build_evaluation_service(load_evaluator_config())


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


def main() -> None:
    st.title("AWS Certification Coach")

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
    st.subheader(question.question)

    user_answer = st.text_area("Your answer", key=f"answer_text_{session.current_index}", height=160)
    if st.button("Evaluate Answer", disabled=not user_answer.strip()):
        result = get_evaluation_service().evaluate(question, user_answer)
        session.record_answer(question, user_answer, result)
        st.session_state.last_result = result

    result = st.session_state.get("last_result")
    if result:
        feedback_column, source_column = st.columns([3, 2])
        with feedback_column:
            st.metric("Score", f"{result.score}%")
            st.write(result.feedback)
            improvements = result.suggested_improvements or result.missing_concepts
            if improvements:
                st.write("What to improve")
                st.write(improvements)
            st.write("Detailed answer")
            st.write(result.detailed_answer)
        with source_column:
            _render_original_multiple_choice(question.original_multiple_choice)
        if st.button("Next Question"):
            session.advance()
            st.session_state.last_result = None
            st.rerun()


def _render_original_multiple_choice(original: MultipleChoiceQuestion | None) -> None:
    st.write("Source multiple-choice question")
    if original is None:
        st.write("No source multiple-choice item is attached.")
        return
    st.caption(original.source_name or "Source item")
    st.write(original.question)
    correct_ids = set(original.correct_option_ids)
    for option in original.options:
        option_text = f"{option.option_id}. {option.text}"
        if option.option_id in correct_ids:
            st.success(option_text)
        else:
            st.write(option_text)


if __name__ == "__main__":
    main()
