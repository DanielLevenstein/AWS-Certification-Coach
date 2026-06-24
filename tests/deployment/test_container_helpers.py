"""Fast contracts for deployment process helpers."""

import subprocess

import pytest

import conftest


def test_container_start_disables_implicit_pull_and_has_timeout(monkeypatch):
    calls = []

    def fake_check_output(command, **kwargs):
        calls.append((command, kwargs))
        return "container-id\n"

    monkeypatch.setattr(conftest.subprocess, "check_output", fake_check_output)

    assert conftest._start_container("candidate:tag") == "container-id"
    assert "--pull=never" in calls[0][0]
    assert calls[0][1]["timeout"] == 30


def test_container_start_reports_timeout(monkeypatch):
    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired("docker run", 30, output="daemon stalled")

    monkeypatch.setattr(conftest.subprocess, "check_output", timeout)

    with pytest.raises(AssertionError, match="Timed out starting Docker image"):
        conftest._start_container("candidate:tag")
