"""Shared Docker lifecycle for explicit deployment guardrails."""

from __future__ import annotations

from contextlib import suppress
import os
from pathlib import Path
import subprocess
import time
import urllib.request

import pytest


def pytest_configure(config) -> None:
    config.deployment_failed = False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        item.config.deployment_failed = True


@pytest.fixture(scope="session")
def deployed_app_url(request) -> str:
    image = os.getenv("DOCKER_IMAGE")
    if not image:
        pytest.fail("DOCKER_IMAGE must name the already-built image under test")

    container_id = _start_container(image)
    try:
        host_port = _container_host_port(container_id)
        base_url = f"http://127.0.0.1:{host_port}"
        _wait_for_http_ok(f"{base_url}/_stcore/health", timeout_seconds=60)
        yield base_url
    finally:
        if request.config.deployment_failed:
            artifacts = Path(os.getenv("DEPLOYMENT_ARTIFACTS_DIR", "metrics/deployment"))
            artifacts.mkdir(parents=True, exist_ok=True)
            logs = subprocess.run(
                ["docker", "logs", container_id],
                check=False,
                capture_output=True,
                text=True,
            )
            (artifacts / "container.log").write_text(
                logs.stdout + logs.stderr,
                encoding="utf-8",
            )
        with suppress(subprocess.CalledProcessError):
            subprocess.run(["docker", "stop", container_id], check=True)


def _container_host_port(container_id: str) -> str:
    for _ in range(20):
        host_port = subprocess.check_output(
            ["docker", "port", container_id, "8501/tcp"],
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        ).strip()
        if host_port:
            return host_port.rsplit(":", 1)[-1]
        time.sleep(0.25)
    raise AssertionError("Docker did not publish a host port for 8501/tcp")


def _start_container(image: str) -> str:
    platform = os.getenv("DOCKER_PLATFORM", "linux/amd64")
    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--pull=never",
                "--platform",
                platform,
                "--rm",
                "-d",
                "-p",
                "127.0.0.1::8501",
                image,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        details = "".join(part or "" for part in (exc.stdout, exc.stderr))
        raise AssertionError(f"Timed out starting Docker image {image!r}: {details}") from exc
    if result.returncode != 0:
        raise AssertionError(
            f"Failed to start Docker image {image!r}: {result.stdout}{result.stderr}"
        )
    container_id = result.stdout.strip()
    if not container_id or "\n" in container_id:
        raise AssertionError(f"Docker returned an invalid container ID: {container_id!r}")
    return container_id


def _wait_for_http_ok(url: str, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            _read_url(url, timeout_seconds=2)
            return
        except Exception as exc:  # noqa: BLE001 - surface the last connection failure.
            last_error = exc
            time.sleep(1)
    raise AssertionError(f"Timed out waiting for {url}: {last_error}")


def _read_url(url: str, timeout_seconds: int) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
        return response.read()
