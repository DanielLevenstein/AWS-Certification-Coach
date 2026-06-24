"""Fast contracts for deployment process helpers."""

import subprocess

import pytest

import conftest


def test_container_start_disables_implicit_pull_and_has_timeout(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="container-id\n", stderr="")

    monkeypatch.setattr(conftest.subprocess, "run", fake_run)

    assert conftest._start_container("candidate:tag") == "container-id"
    assert "--pull=never" in calls[0][0]
    assert calls[0][0][calls[0][0].index("--platform") + 1] == "linux/amd64"
    assert calls[0][1]["timeout"] == 30
    assert calls[0][1]["capture_output"] is True


def test_container_start_reports_timeout(monkeypatch):
    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired("docker run", 30, output="", stderr="daemon stalled")

    monkeypatch.setattr(conftest.subprocess, "run", timeout)

    with pytest.raises(AssertionError, match="Timed out starting Docker image"):
        conftest._start_container("candidate:tag")


def test_container_start_keeps_platform_warning_out_of_container_id(monkeypatch):
    warning = "WARNING: image platform linux/amd64 does not match host linux/arm64/v8"

    monkeypatch.setattr(
        conftest.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(
            command,
            0,
            stdout="2052e0077742\n",
            stderr=warning,
        ),
    )

    assert conftest._start_container("candidate:tag") == "2052e0077742"
