from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratorConfig:
    frequency: float = 77500.0
    samplerate: int = 192000
    amplitude: float = 1.0
    utc: bool = False
    offset: int = 0  # seconds offset

    # Keep the same 100 ms block policy initially: blocksize = samplerate // 10
    latency: str = "low"
    channels: int = 1