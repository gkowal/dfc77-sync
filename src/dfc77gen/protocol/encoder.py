from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class TimeBitsResult:
    time_bits: int
    target_time: datetime  # for debugging / future UI if desired


def to_bcd(n: int) -> int:
    return ((int(n) // 10) % 10 << 4) | (n % 10)


def parity(n: int, l: int, u: int) -> int:
    r = 0
    for i in range(l, u + 1):
        if n & (1 << i):
            r += 1
    return r & 1


def build_time_bits(now: datetime) -> TimeBitsResult:
    """
    Builds DCF77 time bits using DCF77 semantics (time of the next minute):

        target_time = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

        bits |= 1 << 20
        bits |= bcd(minute) << 21
        bits |= bcd(hour)   << 29
        bits |= bcd(day)    << 36
        bits |= bcd(isoweekday) << 42
        bits |= bcd(month)  << 45
        bits |= bcd(year%100) << 50
        bits |= parity(bits, 21, 27) << 28
        bits |= parity(bits, 29, 34) << 35
        bits |= parity(bits, 36, 57) << 58
    """
    target_time = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

    bits = 0
    bits |= 1 << 20
    bits |= to_bcd(target_time.minute) << 21
    bits |= to_bcd(target_time.hour) << 29
    bits |= to_bcd(target_time.day) << 36
    bits |= to_bcd(target_time.isoweekday()) << 42
    bits |= to_bcd(target_time.month) << 45
    bits |= to_bcd(target_time.year % 100) << 50
    bits |= parity(bits, 21, 27) << 28
    bits |= parity(bits, 29, 34) << 35
    bits |= parity(bits, 36, 57) << 58

    return TimeBitsResult(time_bits=bits, target_time=target_time)
