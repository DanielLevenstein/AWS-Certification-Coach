import app


def test_feedback_flag_requires_truthy_value(monkeypatch):
    monkeypatch.delenv("SHOW_FEEDBACK", raising=False)
    assert app._env_enabled(app.SHOW_FEEDBACK_ENV) is False

    monkeypatch.setenv("SHOW_FEEDBACK", "false")
    assert app._env_enabled(app.SHOW_FEEDBACK_ENV) is False

    monkeypatch.setenv("SHOW_FEEDBACK", "1")
    assert app._env_enabled(app.SHOW_FEEDBACK_ENV) is True
