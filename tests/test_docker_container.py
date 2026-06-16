from __future__ import annotations

import os
import subprocess
import time
import urllib.request
from contextlib import suppress

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DOCKER_TESTS") != "1",
    reason="Docker container load test only runs during deploy.",
)


def test_streamlit_app_loads_from_docker_container() -> None:
    image = os.getenv("DOCKER_IMAGE")
    if not image:
        pytest.fail("DOCKER_IMAGE must be set when RUN_DOCKER_TESTS=1")

    container_id = subprocess.check_output(
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "-p",
            "127.0.0.1::8501",
            image,
        ],
        text=True,
    ).strip()
    try:
        host_port = _container_host_port(container_id)
        health_url = f"http://127.0.0.1:{host_port}/_stcore/health"
        page_url = f"http://127.0.0.1:{host_port}/"
        _wait_for_http_ok(health_url, timeout_seconds=60)
        body = _read_url(page_url, timeout_seconds=10)
        assert b"streamlit" in body.lower() or b"AWS Certification Coach" in body
    finally:
        with suppress(subprocess.CalledProcessError):
            subprocess.run(["docker", "stop", container_id], check=True)


def _container_host_port(container_id: str) -> str:
    for _ in range(20):
        host_port = subprocess.check_output(
            [
                "docker",
                "port",
                container_id,
                "8501/tcp",
            ],
            text=True,
        ).strip()
        if host_port:
            return host_port.rsplit(":", 1)[-1]
        time.sleep(0.25)
    raise AssertionError("Docker did not publish a host port for 8501/tcp")


def _wait_for_http_ok(url: str, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            _read_url(url, timeout_seconds=2)
            return
        except Exception as exc:  # noqa: BLE001 - surface last connection failure on timeout.
            last_error = exc
            time.sleep(1)
    raise AssertionError(f"Timed out waiting for {url}: {last_error}")


def _read_url(url: str, timeout_seconds: int) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
        return response.read()
