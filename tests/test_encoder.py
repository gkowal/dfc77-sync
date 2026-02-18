from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from dcf77gen.protocol.encoder import BERLIN_TZ, build_time_bits, parity, to_bcd


def _field(bits: int, start: int, end: int) -> int:
    width = end - start + 1
    return (bits >> start) & ((1 << width) - 1)


def test_build_time_bits_local_mode_encodes_expected_fields_and_parity() -> None:
    now = datetime(2026, 2, 18, 10, 58, 45, tzinfo=BERLIN_TZ)
    result = build_time_bits(now, utc_mode=False)
    bits = result.time_bits

    assert result.target_time == datetime(2026, 2, 18, 10, 59, 0, tzinfo=BERLIN_TZ)
    assert _field(bits, 16, 16) == 0  # A1
    assert _field(bits, 17, 17) == 1  # Z1 (CET)
    assert _field(bits, 18, 18) == 0  # Z2 (CEST)
    assert _field(bits, 19, 19) == 0  # A2
    assert _field(bits, 20, 20) == 1  # start marker

    assert _field(bits, 21, 27) == to_bcd(59)
    assert _field(bits, 29, 34) == to_bcd(10)
    assert _field(bits, 36, 41) == to_bcd(18)
    assert _field(bits, 42, 44) == to_bcd(3)
    assert _field(bits, 45, 49) == to_bcd(2)
    assert _field(bits, 50, 57) == to_bcd(26)

    assert _field(bits, 28, 28) == parity(bits, 21, 27)
    assert _field(bits, 35, 35) == parity(bits, 29, 34)
    assert _field(bits, 58, 58) == parity(bits, 36, 57)


def test_build_time_bits_utc_mode_clears_cet_cest_indicators() -> None:
    now = datetime(2026, 2, 18, 9, 58, 45, tzinfo=ZoneInfo("UTC"))
    result = build_time_bits(now, utc_mode=True)
    bits = result.time_bits

    assert _field(bits, 16, 16) == 0  # A1
    assert _field(bits, 17, 17) == 0  # Z1
    assert _field(bits, 18, 18) == 0  # Z2
