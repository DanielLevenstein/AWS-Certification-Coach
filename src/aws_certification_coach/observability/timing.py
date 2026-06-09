"""Small timing helper reused from the previous prototype."""

from __future__ import annotations

import time
from typing import Any


def log_timing(label: str, start_time: float, **fields: Any) -> float:
    elapsed = time.perf_counter() - start_time
    extra_fields = " ".join(f"{key}={value}" for key, value in fields.items())
    message = f"TIMING {label} seconds={elapsed:.3f}"
    if extra_fields:
        message = f"{message} {extra_fields}"
    print(message, flush=True)
    return elapsed
