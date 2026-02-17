from __future__ import annotations


def is_low_pulse(count_sec: int, count_deci: int, time_bits: int) -> bool:
    """
    Returns whether the current 100 ms block is in the low-amplitude pulse window.

    DCF77 pulse timing:
      - second 0..58: always low during first decisecond (count_deci == 0)
      - bit value 1: also low during second decisecond (count_deci == 1)
      - second 59: no low pulse marker
    """
    if count_sec < 59:
        if count_deci == 0:
            return True
        if count_deci == 1 and ((time_bits >> count_sec) & 1):
            return True
    return False


def is_silence(count_sec: int, count_dec: int, time_bits: int) -> bool:
    """
    Backward-compatible alias for older call sites.
    """
    return is_low_pulse(count_sec=count_sec, count_deci=count_dec, time_bits=time_bits)
