from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class GeneratorState:
    """
    Runtime counters for the DCF77 frame generator.

    `count_sec` advances once per second (0..59).
    `count_deci` advances once per 100 ms block (0..9).
    """
    phase: float = 0.0
    count_sec: int = 0
    count_dec: int = 0
    time_bits: int = 0

    @property
    def count_deci(self) -> int:
        return self.count_dec

    @count_deci.setter
    def count_deci(self, value: int) -> None:
        self.count_dec = value

    def seed_from_wallclock(self, now: datetime, offset_s: int) -> None:
        # Keep alignment with second + offset and 100 ms sub-second tick.
        self.count_sec = (now.second + offset_s) % 60
        self.count_deci = int(now.microsecond // 1e5)

    def advance_block(self) -> None:
        # Advance one 100 ms audio block.
        self.count_deci += 1
        if self.count_deci >= 10:
            self.count_deci = 0
            self.count_sec += 1
        if self.count_sec >= 60:
            self.count_sec = 0

    def is_start_of_second(self) -> bool:
        return self.count_deci == 0

    def is_minute_refresh_point(self) -> bool:
        # Refresh time bits at a deterministic end-of-minute hook.
        return self.count_sec == 59 and self.count_deci == 0
