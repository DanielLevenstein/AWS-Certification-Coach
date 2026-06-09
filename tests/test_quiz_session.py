from aws_certification_coach.domain import Question
from aws_certification_coach.quiz.session import QuizSession


def test_quiz_session_randomizes_question_order_with_seed():
    questions = [_question(str(index)) for index in range(10)]

    session = QuizSession(questions, seed=7)

    assert [question.question_id for question in session.questions] != [
        question.question_id for question in questions
    ]
    assert [question.question_id for question in session.questions] == [
        question.question_id for question in QuizSession(questions, seed=7).questions
    ]


def test_quiz_session_can_preserve_order_for_tests():
    questions = [_question(str(index)) for index in range(3)]

    session = QuizSession(questions, shuffle=False)

    assert [question.question_id for question in session.questions] == ["0", "1", "2"]


def _question(question_id: str) -> Question:
    return Question(
        question_id=question_id,
        certification="Cloud Practitioner",
        domain="Test",
        difficulty="Easy",
        question="Question?",
        reference_answer="Answer.",
        key_concepts=[],
    )
