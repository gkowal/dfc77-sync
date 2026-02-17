from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class GeneratorState:
    """
    Holds the same state variables as the original DCF77Generator:
      - phase
      - count_sec
      - count_dec
      - time_bits
    """
    phase: float = 0.0
    count_sec: int = 0
    count_dec: int = 0
    time_bits: int = 0

    def seed_from_wallclock(self, now: datetime, offset_s: int) -> None:
        # Matches:
        #   self.count_sec = (now.second + self.offset) % 60
        #   self.count_dec = int(now.microsecond // 1e5)
        self.count_sec = (now.second + offset_s) % 60
        self.count_dec = int(now.microsecond // 1e5)

    def advance_block(self) -> None:
        # Matches the callback tail:
        #   self.count_dec += 1
        #   if self.count_dec >= 10: self.count_dec=0; self.count_sec += 1
        #   if self.count_sec >= 60: self.count_sec=0
        self.count_dec += 1
        if self.count_dec >= 10:
            self.count_dec = 0
            self.count_sec += 1
        if self.count_sec >= 60:
            self.count_sec = 0

    def is_start_of_second(self) -> bool:
        return self.count_dec == 0

    def is_minute_refresh_point(self) -> bool:
        # Refresh time bits at a deterministic end-of-minute hook.
        # This preserves the original timing point:
        #   if self.count_sec == 59 and self.count_dec == 0: self.update_time_bits()
        return self.count_sec == 59 and self.count_dec == 0
