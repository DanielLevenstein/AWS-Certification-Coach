"""Container health guardrail for an explicitly built deployment image."""

import urllib.request


def test_streamlit_container_health(deployed_app_url: str) -> None:
    with urllib.request.urlopen(f"{deployed_app_url}/_stcore/health", timeout=10) as response:
        assert response.status == 200
        assert response.read().strip() == b"ok"

    with urllib.request.urlopen(f"{deployed_app_url}/", timeout=10) as response:
        body = response.read()
    assert b"streamlit" in body.lower() or b"AWS Certification Coach" in body
