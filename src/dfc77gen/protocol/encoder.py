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


def format_time_bits_breakdown(time_bits: int) -> str:
    bit_lsb_first = "".join("1" if (time_bits >> i) & 1 else "0" for i in range(59))
    bit_msb_first = f"{time_bits:059b}"

    fields = [
        ("M", 20, 20),
        ("Minute", 21, 27),
        ("P1", 28, 28),
        ("Hour", 29, 34),
        ("P2", 35, 35),
        ("Day", 36, 41),
        ("Weekday", 42, 44),
        ("Month", 45, 49),
        ("Year", 50, 57),
        ("P3", 58, 58),
    ]

    lines = []
    lines.append(f"time_bits (059b, msb->lsb): {bit_msb_first}")
    lines.append(f"time_bits (bit0->bit58):    {bit_lsb_first}")
    lines.append("fields:")
    for name, start, end in fields:
        seg = bit_lsb_first[start : end + 1]
        lines.append(f"  {name:<7} [{start:02d}..{end:02d}] {seg}")

    p1_actual = (time_bits >> 28) & 1
    p2_actual = (time_bits >> 35) & 1
    p3_actual = (time_bits >> 58) & 1
    p1_calc = parity(time_bits, 21, 27)
    p2_calc = parity(time_bits, 29, 34)
    p3_calc = parity(time_bits, 36, 57)

    lines.append("parity:")
    lines.append(f"  P1 bit28 minute(21..27): actual={p1_actual} expected={p1_calc}")
    lines.append(f"  P2 bit35 hour(29..34):   actual={p2_actual} expected={p2_calc}")
    lines.append(f"  P3 bit58 date(36..57):   actual={p3_actual} expected={p3_calc}")
    return "\n".join(lines)
