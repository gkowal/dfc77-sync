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

    def __post_init__(self) -> None:
        if self.samplerate <= 0:
            raise ValueError("samplerate must be > 0")
        if self.amplitude <= 0.0 or self.amplitude > 1.0:
            raise ValueError("amplitude must be in (0, 1.0]")
        if self.offset < 0 or self.offset > 59:
            raise ValueError("offset must be in range 0..59")
        if self.frequency >= self.samplerate / 2:
            raise ValueError("frequency must be below Nyquist (samplerate / 2)")
