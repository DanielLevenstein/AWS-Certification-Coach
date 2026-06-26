from app import _score_grade


def test_score_grade_boundaries():
    assert _score_grade(100)[0] == "A"
    assert _score_grade(90)[0] == "A"
    assert _score_grade(89)[0] == "B"
    assert _score_grade(80)[0] == "B"
    assert _score_grade(79)[0] == "C"
    assert _score_grade(70)[0] == "C"
    assert _score_grade(69)[0] == "D"
    assert _score_grade(60)[0] == "D"
    assert _score_grade(59)[0] == "F"
    assert _score_grade(0)[0] == "F"
